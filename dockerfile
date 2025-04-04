FROM python:3.12-bookworm

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt update \
    && apt install -y --no-install-recommends gcc libpq-dev \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy project
COPY . .

# Set up alembic
RUN mkdir -p migrations

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
