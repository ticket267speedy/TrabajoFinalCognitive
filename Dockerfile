FROM python:3.13-slim

# Prevents Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install build tools only if needed (kept minimal for slim images)
# RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . /app

# Environment for Flask CLI
ENV FLASK_APP=run.py \
    FLASK_ENV=production \
    PORT=5000

EXPOSE 5000

# Run DB migrations then start the app with gunicorn
CMD ["sh", "-c", "flask db upgrade && gunicorn -w 3 -b 0.0.0.0:${PORT} run:app"]