from fastapi import APIRouter, Depends, Form, Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, EmailStr
from werkzeug.security import generate_password_hash
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="../templates")
router = APIRouter()


class Register(
    BaseModel
):  # This BaseModel is used for validating types, contraints, etc.
    first_name: str
    last_name: str
    role: str
    email: EmailStr
    password: str

    @classmethod  # Converting the BaseModel to pydantic model on receiving form input.
    def form(
        cls,
        first_name: str = Form(..., min_length=2, max_length=50),
        last_name: str = Form(..., min_length=2, max_length=50),
        role: str = Form(..., min_length=2, max_length=50),
        email: EmailStr = Form(...),
        password: str = Form(..., min_length=6, max_length=128),
    ):
        return cls(
            first_name=first_name,
            last_name=last_name,
            role=role,
            email=email,
            password=password,
        )


@router.post("/register", response_class=HTMLResponse, status_code=201)
async def register_user(
    request: Request,
    user: Register = Depends(Register.form),
    db: AsyncSession = Depends(),
):

    # Defer the imports to avoid circular dependencies
    from app.main import get_db, User

    db: AsyncSession = await get_db().__anext__()  # Get database session

    if (
        request.headers.get("Content-Type")
        == "application/x-www-form-urlencoded"
    ):
        hashed_password = generate_password_hash(user.password)
        new_user = User(
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            email=user.email,
            password=hashed_password,
        )

        try:
            user = select(User).filter_by(email=user.email)
            result = await db.execute(user)
            user_exists = (
                result.scalar_one_or_none()
            )  # This returns None or the user if it was found.

            if user_exists:
                return templates.TemplateResponse(
                    "register.html",
                    {
                        "request": request,
                        "flash_message": "User already exists! Please login.",
                    },
                )

            db.add(new_user)
            await db.commit()

            response = RedirectResponse(url="/login")
            response.set_cookie(
                key="user_email", value=user.email, max_age=3600
            )  # Setting the user email as session cookie. Expiration in one hour.

            message = "Registration successful! Please login."
            response.set_cookie(
                key="flash_message", value=message, max_age=10
            )  # Store a flash message for a short time in order to pass it to /login and show the message there.

            return response

        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred: {str(e)}",
            )
            return templates.TemplateResponse(
                "register.html",
                {
                    "request": request,
                    "flash_message": "Registration Failed! Please try again.",
                },
            )  # Failure message.

    return templates.TemplateResponse("register.html", {"request": request})
