# Use the official Python image from the Docker Hub
FROM python:3.9.12-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Install Firefox and dependencies for Selenium
RUN apt-get update && apt-get install -y \
    firefox-esr \
    wget \
    libgtk-3-0 \
    libdbus-glib-1-2 \
    libxt6 \
    libx11-xcb1 \
    libxcomposite1 \
    libasound2 \
    libgl1-mesa-glx \
    xvfb \
    && apt-get clean

# Download and install Geckodriver
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz \
    && tar -xvzf geckodriver-v0.30.0-linux64.tar.gz \
    && chmod +x geckodriver \
    && mv geckodriver /usr/local/bin/ \
    && rm geckodriver-v0.30.0-linux64.tar.gz

# Set up Xvfb to run Firefox in headless mode
RUN Xvfb :99 -screen 0 1280x1024x24 &

# Print the current working directory
RUN pwd

# List the files in the current directory
RUN ls -la

# Copy the entire Flask app code into the container
COPY Flaskapp/ ./Flaskapp/

# Expose the port your app runs on
EXPOSE 5000

# Set the display environment variable for headless Firefox
ENV DISPLAY=:99

# Set the command to run your application
CMD ["python", "Flaskapp/app.py"]
