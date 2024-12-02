# Use a lightweight Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the application code
COPY . /app

# Install dependencies
RUN pip install flask opentelemetry-api opentelemetry-sdk \
    opentelemetry-instrumentation-flask azure-monitor-opentelemetry-exporter

# Expose the application port
EXPOSE 8080

# Run the Flask application
CMD ["python", "app.py"]
