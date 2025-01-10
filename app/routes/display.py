import os
import asyncio
import logging
import pandas as pd
from datetime import datetime, timedelta
from bitalino import BITalino
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from app.dependencies import get_db
from app.models import SignalAmplitude

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
logging.basicConfig(level=logging.DEBUG)


@router.get("/display", response_class=HTMLResponse, status_code=200)
async def display(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        user_email = request.cookies.get("user_email")
        message = request.cookies.get(
            "flash_message", ""
        )  # Default msg value ""

        if not user_email:
            response = RedirectResponse(url="/")
            message = "In order to access the dashboard you need to login."
            response.set_cookie(key="flash_message", value=message, max_age=10)
            return response

        result = await db.execute(  # Query the cpatured data from database.
            select(SignalAmplitude).order_by(SignalAmplitude.timestamp)
        )
        signals = result.scalars().all()

        # Transform the data into a JSON-serializable format
        signal_data = [
            {
                "timestamp": signal.timestamp.isoformat(),
                "first_channel": signal.first_channel,
                "second_channel": signal.second_channel,
            }
            for signal in signals
        ]

        return templates.TemplateResponse(
            "display.html",
            {
                "request": request,
                "flash_message": message,
                "signal_data": signal_data,
            },
        )
    except Exception as e:
        logging.error(f"Error loading display page: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while loading the display page.",
        )


@router.post("/start-device", response_class=RedirectResponse)
async def start_device(request: Request, db: AsyncSession = Depends(get_db)):
    device_address = "98:D3:11:FD:1F:3A"
    sampling_rate = 100
    duration = 20
    csv_folder = "csv_output"

    try:
        os.makedirs(
            csv_folder, exist_ok=True
        )  # Check if the output folder exists

        device = await asyncio.to_thread(BITalino, device_address)

        eeg_channels = [2, 3]
        await asyncio.to_thread(device.start, sampling_rate, eeg_channels)

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

            new_signal = SignalAmplitude(  # Here each signal value in each channel is creted and added to database along with the timestamp.
                first_channel=eeg_signal_a3,
                second_channel=eeg_signal_a4,
                timestamp=current_time_utc,
            )
            db.add(new_signal)

        await db.commit()

        device.stop()

        # Save data to CSV
        eeg_df = pd.DataFrame(
            {
                "UTC Timestamp": time_list,
                "EEG Signal A3 (μV)": eeg_data_list_a3,
                "EEG Signal A4 (μV)": eeg_data_list_a4,
            }
        )
        csv_file = os.path.join(csv_folder, "eeg_data_a3_a4_utc.csv")
        eeg_df.to_csv(csv_file, index=False)

        message = (
            f"Data capture complete! Data saved to {csv_file} at csv_output."
        )
        response = RedirectResponse(url="/display")
        response.set_cookie("flash_message", value=message, max_age=10)

        return response

    except Exception as e:
        logging.error(f"Error starting BITalino: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while capturing data: {str(e)}",
        )

    finally:

        if "device" in locals():
            try:
                await asyncio.to_thread(device.close)
            except Exception as cleanup_error:
                logging.error(
                    f"Failed to close BITalino device: {cleanup_error}",
                    exc_info=True,
                )
