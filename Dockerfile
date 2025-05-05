# syntax=docker/dockerfile:1
FROM python:3.13-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --user -r requirements.txt

# Final image
FROM python:3.13-slim
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy project files
COPY . .

# Collect static files (optional, for production)
# RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "linked_ai.wsgi:application", "--bind", "0.0.0.0:8000"] 