# Use an official base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy your application files to the container
COPY . /app

# Install dependencies
RUN pip install -r requirements.txt

# Expose a port (optional, if the app runs on a specific port)
EXPOSE 8000

# Define the command to run your app
CMD ["python", "manage.py", "runserver","0.0.0.0:8000"]
