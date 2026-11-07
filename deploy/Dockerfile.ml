FROM python:3.11-slim

WORKDIR /app/ml

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY ml/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY ml .

EXPOSE 8001

CMD ["python", "serve.py"]
