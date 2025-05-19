FROM python:3.11-slim

WORKDIR /app


RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    # netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

#Running
CMD ["sh", "-c", "python manage.py migrate && python create_superuser.py && python manage.py runserver 0.0.0.0:8000"]
