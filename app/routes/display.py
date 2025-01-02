import pandas as pd
from datetime import datetime, timedelta
from bitalino import BITalino
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="../templates")


@router.get("/display", response_class=HTMLResponse, status_code=200)
async def display(request: Request):
    user_email = request.cookies.get("user_email")
    message = request.cookies.get("flash_message")

    if not user_email:
        response = RedirectResponse(url="/login")
        message = "In order to access the dashboard you need to login."
        response.set_cookie(key="flash_message", value=message, max_age=10)
        return response

    return templates.TemplateResponse(
        "display.html", {"request": request, "flash_message": message}
    )


@router.post("/start-device", response_class=RedirectResponse)
async def start_device(request: Request):
    device_address = "98:D3:11:FD:1F:3A"
    sampling_rate = 100
    duration = 20

    try:
        device = BITalino(device_address)

        eeg_channels = [2, 3]
        device.start(sampling_rate, eeg_channels)

        start_time_utc = datetime.utcnow()

        eeg_data_list_a3 = []
        eeg_data_list_a4 = []
        time_list = []

        for i in range(sampling_rate * duration):
            data = device.read(1)

            eeg_signal_a3 = data[0, -2]
            eeg_signal_a4 = data[0, -1]

            current_time_utc = start_time_utc + timedelta(
                seconds=i / sampling_rate
            )

            eeg_data_list_a3.append(eeg_signal_a3)
            eeg_data_list_a4.append(eeg_signal_a4)
            time_list.append(current_time_utc)

        device.stop()

        # Save data to CSV
        eeg_df = pd.DataFrame(
            {
                "UTC Timestamp": time_list,
                "EEG Signal A3 (μV)": eeg_data_list_a3,
                "EEG Signal A4 (μV)": eeg_data_list_a4,
            }
        )
        csv_file = "eeg_data_a3_a4_utc.csv"
        eeg_df.to_csv(csv_file, index=False)

        message = f"Data capture complete! Data saved to {csv_file}."
        response = RedirectResponse(url="/display")
        response.set_cookie("flash_message", value=message, max_age=10)

        return response

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while capturing data: {str(e)}",
        )

    finally:

        if "device" in locals():
            device.close()
