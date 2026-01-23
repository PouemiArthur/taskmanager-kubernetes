# Start FROM a base image (like inheriting from a parent class)
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements first (Docker caching optimization!)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY pjrapp.py .

# Expose port (documentation, doesn't actually publish)
EXPOSE 5000

# Command to run when container starts
CMD ["python", "pjrapp.py"]
