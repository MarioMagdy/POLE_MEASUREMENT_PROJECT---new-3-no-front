# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Gunicorn
RUN pip install gunicorn

# Make port 5500 available to the world outside this container
EXPOSE 5500

# Run Gunicorn, specifying the application module and binding it to the port
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5500", "flask_backend_v2:app"]