# Use the official Python image from the Docker Hub
FROM python:3.9.12-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt


# Print the current working directory
RUN pwd

# List the files in the current directory
RUN ls -la

# Copy the entire Flask app code into the container
COPY Flaskapp/ ./Flaskapp/

RUN apt-get update && apt-get install -y wget bzip2 libxtst6 libgtk-3-0 libx11-xcb-dev libdbus-glib-1-2 libxt6 libpci-dev && rm -rf /var/lib/apt/lists/*

# Install Firefox
RUN wget -qO - https://mozilla.org/ | tar xz -C /opt

# Expose the port your app runs on
EXPOSE 5000

# Set the command to run Firefox in headless mode when the container starts
CMD ["firefox", "-headless"]
# # Set the command to run your application
# CMD ["python", "Flaskapp/app.py"]
