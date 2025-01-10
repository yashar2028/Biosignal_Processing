# This is the image of the application itself. This image is used along with a postgres imgae in docker-compos.yml to dockerize the whole app.

# Use Python 3.11 slim as the base image
FROM python:3.11-slim

# Install system dependencies (compilers and libraries required for building certain Python packages)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    bluez \
    gcc \
    libpq-dev \
    make \
    libbluetooth-dev \
    libc6-dev \
    curl && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - --yes

# Ensure Poetry is available in the PATH
ENV PATH="/root/.local/bin:$PATH"

# Set the working directory in the container
WORKDIR /app

# Copy the pyproject.toml, poetry.lock to install dependencies
COPY pyproject.toml poetry.lock* /app/

# Install the dependencies defined in the pyproject.toml file
RUN poetry install --no-root

# Copy the application code
COPY app/ /app/app/

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to start the FastAPI app directly (no migrations)
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

