from fastapi import APIRouter, Response
from fastapi.responses import RedirectResponse

router = APIRouter()


def clear_sessions(response: Response):
    response.delete_cookie("user_email")
    response.delete_cookie("user_email_temporary_session")
    response.delete_cookie("otp_token")
    response.delete_cookie("flash_message")

    return response


@router.get("/logout", response_class=RedirectResponse)
async def logout(response: Response):
    response = clear_sessions(response)

    return RedirectResponse(url="/")
