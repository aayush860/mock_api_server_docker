# Use an official Python runtime as a parent image
FROM python:3-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed dependencies specified in requirements.txt
RUN python -m pip install -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Copy the data seeding script into the working directory
COPY ./db/data_seed.py .

# Copy the entrypoint script into the working directory
COPY entrypoint.sh .

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Expose the port Flask runs on
EXPOSE 5000

# Make the entrypoint script executable
RUN chmod +x entrypoint.sh

# Set the entry point to the entrypoint script
ENTRYPOINT ["./entrypoint.sh"]