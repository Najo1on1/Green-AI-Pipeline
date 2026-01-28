# Use a lightweight Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dependencies explicitly
RUN pip install flask

# Copy our code
COPY main.py .

# Command to run the app
CMD ["python", "main.py"]