# Base image
FROM python:3.12-slim

# Set workdir
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app and templates/static
COPY app.py .
COPY templates ./templates
COPY static ./static
RUN mkdir -p uploads

# Expose port
EXPOSE 8000

# Run app with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
