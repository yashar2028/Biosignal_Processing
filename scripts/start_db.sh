#!/bin/bash

# Define variables for the database
DB_NAME="signaldb"
DB_USER="user1"
DB_PASSWORD="12345678910"
DB_PORT=5432
DB_CONTAINER_NAME="postgres_database"

# Check if the container exists (whether stopped or running)
EXISTING_CONTAINER=$(docker ps -aq -f name=$DB_CONTAINER_NAME)

if [ "$EXISTING_CONTAINER" ]; then
  # If container exists, try to start it
  echo "Starting existing PostgreSQL container."
  docker start $DB_CONTAINER_NAME
else
  # If container doesn't exist, run a new PostgreSQL container
  echo "Running a new PostgreSQL container."
  docker run --name $DB_CONTAINER_NAME \
    -e POSTGRES_USER=$DB_USER \
    -e POSTGRES_PASSWORD=$DB_PASSWORD \
    -e POSTGRES_DB=$DB_NAME \
    -p $DB_PORT:5432 \
    -d postgres
fi

echo "PostgreSQL is running on port $DB_PORT."

