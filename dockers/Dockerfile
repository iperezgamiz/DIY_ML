# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Install system dependencies required for Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container to /app, which is where the Flask app resides
WORKDIR /app

# Copy the relevant directories into the container
COPY ./api /app
COPY ./queues /queues

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable for the Flask application
ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV PYTHONPATH="/app:/queues"

# Run app.py when the container launches
CMD ["flask", "run", "--host=0.0.0.0"]
