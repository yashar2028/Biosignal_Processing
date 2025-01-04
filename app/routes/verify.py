import secrets
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel


templates = Jinja2Templates(directory="app/templates")
router = APIRouter()


class VerifyOTP(BaseModel):
    otp: str

    @classmethod
    def form(cls, otp: str = Form(..., max_length=30)):
        return cls(otp=otp)


@router.get("/verify", response_class=HTMLResponse)
async def render_verify_page(request: Request):
    """
    Handles rendering the verify page.
    """
    message = request.cookies.get("flash_message", "")
    return templates.TemplateResponse(
        "verify.html", {"request": request, "flash_message": message}
    )


@router.post("/verify", response_class=RedirectResponse)
async def verify_otp(
    request: Request,
    otp_data: VerifyOTP = Depends(VerifyOTP.form),
):

    user_email_exist_in_session = request.cookies.get("user_email")
    if (
        user_email_exist_in_session
    ):  # First check to see if user is already verified.
        response = RedirectResponse(url="/display")
        message = "Already verified."
        response.set_cookie(key="flash_message", value=message, max_age=10)
        return response

    otp_in_cookie = request.cookies.get("otp_token")
    user_email = request.cookies.get("user_email_temporary_session")

    if not otp_in_cookie or not user_email:
        response = RedirectResponse(url="/")
        message = "Verification session expired. Please login again."
        response.set_cookie(key="flash_message", value=message, max_age=10)
        return response

    if secrets.compare_digest(
        otp_data.otp, otp_in_cookie
    ):  # Check if the provided OTP matches the one stored in the cookie.
        response = RedirectResponse(url="/display", status_code=303)
        response.set_cookie(
            key="user_email", value=user_email, max_age=3600
        )  # The main session to verify user is successfully logged in is created here. Only this session can access /display.
        response.set_cookie(
            key="flash_message",
            value="Verification successful! Click on capture to begin aquisition.",
            max_age=10,
        )
        return response

    else:
        return templates.TemplateResponse(
            "verify.html",
            {
                "request": request,
                "flash_message": "Invalid OTP. Please try again.",
            },
        )
