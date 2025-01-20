# import os
# import secrets
# from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Form, Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, EmailStr
from werkzeug.security import check_password_hash
from fastapi.templating import Jinja2Templates

# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail
from app.dependencies import get_db
from app.models import User


templates = Jinja2Templates(directory="app/templates")
router = APIRouter()

# load_dotenv()

# SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
# SENDGRID_FROM_EMAIL = os.getenv(
#    "SENDGRID_FROM_EMAIL"
# )  # Reading the email configration from .env which is used Below to send email.


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


'''
async def send_email(to_email: str, subject: str, body: str):
    """
    Function to send an email using SendGrid API.
    """
    message = Mail(
        from_email=SENDGRID_FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        plain_text_content=body,
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}",
        )

'''


@router.get("/", response_class=HTMLResponse)
async def render_login_page(request: Request):
    """
    Handles rendering the login page.
    """
    message = request.cookies.get("flash_message", "")
    return templates.TemplateResponse(
        "login.html", {"request": request, "flash_message": message}
    )


@router.post("/", response_class=RedirectResponse, status_code=201)
async def login_user(
    request: Request,
    user: Login = Depends(Login.form),
    db: AsyncSession = Depends(get_db),
):

    if (
        request.headers.get("Content-Type")
        == "application/x-www-form-urlencoded"
    ):

        user_email_exist_in_session = request.cookies.get(
            "user_email_temporary_session"
        )  # Changed user_email cookie to user_email_temporary_session.
        if (
            user_email_exist_in_session
        ):  # First check to see if user is already logged in.
            response = RedirectResponse(url="/display", status_code=303)
            message = "Already logged in."
            response.set_cookie(key="flash_message", value=message, max_age=10)
            return response

        try:
            query = select(User).filter(User.email == user.email)
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

            response = RedirectResponse(
                url="/display", status_code=303
            )  # Changed /verify to /display to bypass the verifications. To solve the problem for email config security in docker.

            # otp_token = secrets.token_urlsafe(
            #    16
            # )  # Generating the one-time token.

            response.set_cookie(
                key="user_email_temporary_session",
                value=user.email,
                max_age=120,
            )  # This is a temporary cookie to retreive the email at verify, and only there make the real session. OTP is functional but to make things simpler for docker it is bypassed in this version

            """
            response.set_cookie(  # Storing the OTP in a secure cookie.
                key="otp_token",
                value=otp_token,
                max_age=300,
                httponly=True,
                secure=True,
            )

            subject = "Your One-Time Login Token"
            body = f"Your OTP is: {otp_token}"
            await send_email(
                current_user.email, subject, body
            )  # Sent token via email.
            """

            return response

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred: {str(e)}",
            )
