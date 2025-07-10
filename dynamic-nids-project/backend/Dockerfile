# backend/Dockerfile

# Use an official, slim Python runtime as the parent image for a smaller footprint
FROM python:3.11-slim

# Set environment variables to prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory within the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Using --no-cache-dir reduces the final image size by not storing the pip cache
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's source code to the working directory
COPY . .

# Define the command to run the application using Uvicorn
# The --host 0.0.0.0 flag makes the server accessible from outside the container.
# The --reload flag enables hot-reloading for development, automatically restarting
# the server when code changes are detected in the mounted volume.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
