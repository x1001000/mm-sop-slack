# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Environment variables will be set in HF Spaces settings
# They are: GEMINI_API_KEY, SLACK_APP_TOKEN, SLACK_BOT_TOKEN

# Expose port (optional, mainly for HF Spaces compatibility)
EXPOSE 7860

# Run the application
CMD ["python", "app.py"]
