# Use the official Python image from the Docker Hub
FROM python:3.9.12-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the requirements file into the container
COPY ../requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire Flask app code into the container
COPY Flaskapp/ ./Flaskapp/

# Expose the port your app runs on
EXPOSE 5000

# Set the command to run your application
CMD ["python", "Flaskapp/app.py"]
