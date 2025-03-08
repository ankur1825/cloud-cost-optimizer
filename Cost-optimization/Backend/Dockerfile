# Use the official Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the backend code into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the API port
EXPOSE 8000

# Start both FastAPI and Celery
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

