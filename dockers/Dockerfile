# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Install system dependencies required for Python packages like bcrypt
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the contents of the api directory into the container at /app
COPY ./api /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=app.py
ENV FLASK_ENV=development

# Run app.py when the container launches
CMD ["flask", "run", "--host=0.0.0.0"]
