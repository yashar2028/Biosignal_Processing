import os
import secrets
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Form, Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, EmailStr
from werkzeug.security import check_password_hash
from fastapi.templating import Jinja2Templates
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

load_dotenv()

email_config = ConnectionConfig(  # Reading the email configration from .env. Below used to send email.
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT")),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_TLS=os.getenv("MAIL_TLS") == "True",
    MAIL_SSL=os.getenv("MAIL_SSL") == "True",
    USE_CREDENTIALS=os.getenv("USE_CREDENTIALS") == "True",
    VALIDATE_CERTS=os.getenv("VALIDATE_CERTS") == "True",
)

templates = Jinja2Templates(directory="../templates")
router = APIRouter()


class Login(BaseModel):
    email: EmailStr
    password: str

    @classmethod
    def form(
        cls,
        email: EmailStr = Form(...),
        password: str = Form(..., min_length=6, max_length=128),
    ):
        return cls(email=email, password=password)


@router.post("/login", response_class=HTMLResponse, status_code=201)
async def login_user(
    request: Request,
    user: Login = Depends(Login.form),
    db: AsyncSession = Depends(),
):

    from app.main import get_db, User

    db: AsyncSession = await get_db().__anext__()  # Get database session

    message = request.cookies.get("flash_message")

    if (
        request.headers.get("Content-Type")
        == "application/x-www-form-urlencoded"
    ):

        user_email_exist_in_session = request.cookies.get("user_email")
        if (
            user_email_exist_in_session
        ):  # First check to see if user is already logged in.
            response = RedirectResponse(url="/display")
            message = "Already logged in."
            response.set_cookie(key="flash_message", value=message, max_age=10)
            return response

        try:
            query = select(User).where(User.email == user.email)
            result = await db.execute(query)
            current_user = result.scalar_one_or_none()

            if not current_user or not check_password_hash(
                current_user.password, user.password
            ):
                return templates.TemplateResponse(
                    "login.html",
                    {
                        "request": request,
                        "flash_message": "Invalid email or password. Please try again.",
                    },
                )

            response = RedirectResponse(url="/verify")

            otp_token = secrets.token_urlsafe(
                16
            )  # Generating the one-time token.

            response.set_cookie(
                key="user_email_temporary_session",
                value=user.email,
                max_age=120,
            )  # This is a temporary cookie to retreive the email at verify, and only there make the real session.
            response.set_cookie(  # Storing the OTP in a secure cookie.
                key="otp_token",
                value=otp_token,
                max_age=300,
                httponly=True,
                secure=True,
            )

            email_message = MessageSchema(
                subject="Your One-Time Login Token",
                recipients=[current_user.email],
                body=f"Your one-time login token is: {otp_token}",
                subtype="plain",
            )
            fm = FastMail(email_config)
            await fm.send_message(email_message)  # Sent token via email.

            return response

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred: {str(e)}",
            )

    return templates.TemplateResponse(
        "login.html", {"request": request, "flash_message": message}
    )
