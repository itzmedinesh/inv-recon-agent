# Use an official Python image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt requirements.txt

# Upgrade pip
RUN pip install --upgrade pip

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask app
COPY . .

# Expose the application port
EXPOSE 5000

# Run the Flask application
CMD ["python", "run.py"]