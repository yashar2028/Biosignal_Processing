import os
import asyncio
import logging
import csv
import numpy as np
from scipy.signal import welch
from scipy.signal import argrelextrema
from datetime import datetime, timedelta
from bitalino import BITalino
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from app.dependencies import get_db
from app.models import SignalAmplitude
from app.socket import manager

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
logging.basicConfig(level=logging.DEBUG)


csv_path = "csv_output/eeg_data_a3_a4_utc.csv"


def simps(y, x):
    """
    local version of simps without need for scipy.integrate
    """
    if len(x) < 3 or len(x) % 2 == 0:
        raise ValueError("Simpson's rule requires an odd number of samples.")

    h = (x[-1] - x[0]) / (len(x) - 1)
    integral = y[0] + y[-1] + 4 * np.sum(y[1:-1:2]) + 2 * np.sum(y[2:-2:2])
    return integral * h / 3


def read_csv_for_analysis():
    timestamps = []
    eeg_signal_a3 = []
    eeg_signal_a4 = []

    with open(csv_path, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        _ = next(reader)  # To skip the header row

        for row in reader:
            raw_timestamp = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S.%f")
            formatted_timestamp = raw_timestamp.strftime(
                "%m/%d/%Y %I:%M:%S %p"
            )
            timestamps.append(formatted_timestamp)
            eeg_signal_a3.append(float(row[1]))
            eeg_signal_a4.append(float(row[2]))

    # Convert to numpy arrays for efficient computation
    timestamps = np.array(timestamps)
    eeg_signal_a3 = np.array(eeg_signal_a3)
    eeg_signal_a4 = np.array(eeg_signal_a4)

    return eeg_signal_a3, eeg_signal_a4


def find_minima_around(frequencies, psd, target_freq, search_range=2):
    """
    Finds two minima around the target frequency within the specified search range.
    """
    range_indices = (frequencies >= target_freq - search_range) & (
        frequencies <= target_freq + search_range
    )
    freqs_in_range = frequencies[range_indices]
    psd_in_range = psd[range_indices]

    minima_indices = argrelextrema(psd_in_range, comparator=np.less)[0]

    if len(minima_indices) >= 2:
        minima_freqs = freqs_in_range[minima_indices]
        sorted_indices = np.argsort(np.abs(minima_freqs - target_freq))[:2]
        return minima_freqs[sorted_indices]
    else:
        return np.array(
            [target_freq - search_range, target_freq + search_range]
        )


# Function to detect closed eyes using minima-based integration. This is used below for analysis.
def detect_closed_eyes_minima(
    frequencies, psd, target_freq=10, threshold=0.065
):

    minima_freqs = find_minima_around(frequencies, psd, target_freq)

    total_power = simps(psd, frequencies)

    band_indices = (frequencies >= minima_freqs[0]) & (
        frequencies <= minima_freqs[1]
    )

    band_power = simps(psd[band_indices], frequencies[band_indices])

    relative_power = band_power / total_power

    if (
        relative_power > threshold
    ):  # Compration with threshhold. The threshhold was concluded as result of experiments.
        return f"Warning: Closed eyes! Relative power = {relative_power:.2%}"
    else:
        return f"No closed eyes!. Relative power = {relative_power:.2%}"


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

        eeg_signal_a3, eeg_signal_a4 = read_csv_for_analysis()
        sampling_rate = 100

        f_a3, psd_a3 = welch(
            eeg_signal_a3, sampling_rate, nperseg=sampling_rate
        )
        # f_a4, psd_a4 = welch(eeg_signal_a4, sampling_rate, nperseg=sampling_rate)
        percentage_eyes_a3 = detect_closed_eyes_minima(
            f_a3, psd_a3, threshold=0.065
        )
        # percentage_eyes_a4 = detect_closed_eyes_minima(f_a4, psd_a4, threshold=0.065)

        return templates.TemplateResponse(
            "display.html",
            {
                "request": request,
                "flash_message": message,
                "signal_data": signal_data,
                "analysis_result": percentage_eyes_a3,
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

        await manager.broadcast("Acquisition started. Capturing...")

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

            new_signal = SignalAmplitude(  # Here each signal value in each channel is created and added to database along with the timestamp.
                first_channel=eeg_signal_a3,
                second_channel=eeg_signal_a4,
                timestamp=current_time_utc,
            )
            db.add(new_signal)

        await db.commit()

        device.stop()

        # Save data to CSV
        csv_file = os.path.join(csv_folder, "eeg_data_a3_a4_utc.csv")
        with open(csv_file, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                ["UTC Timestamp", "EEG Signal A3 (uV)", "EEG Signal A4 (uV)"]
            )
            for timestamp, a3, a4 in zip(
                time_list, eeg_data_list_a3, eeg_data_list_a4
            ):
                writer.writerow([timestamp, a3, a4])

        await manager.broadcast(
            "Acquisition completed! Please refresh the page."
        )

        flash_message = f"Data saved to {csv_file}."
        response = RedirectResponse(url="/display")
        response.set_cookie("flash_message", value=flash_message, max_age=10)

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
