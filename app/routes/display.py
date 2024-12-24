from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="../../templates")


@router.get("/display", response_class=HTMLResponse, status_code=200)
async def display(request: Request):
    user_email = request.cookies.get("user_email")
    message = request.cookies.get("flash_message")

    if not user_email:
        response = RedirectResponse(url="/login")
        message = "In order to access the dashboard you need to login."  # TODO: Capture and show it in login page.
        response.set_cookie(key="flash_message2", value=message, max_age=10)
        return response

    return templates.TemplateResponse(
        "display.html", {"request": request, "flash_message": message}
    )
