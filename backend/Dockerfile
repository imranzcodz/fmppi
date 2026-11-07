FROM python:3.12-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
WORKDIR /app/backend

ENV DATABASE_URL=mysql+pymysql://fmppi_user:fmppi_pass@localhost:3306/fmppi
ENV SECRET_KEY=change-me-in-production
ENV CORS_ORIGINS=*

RUN alembic -c alembic.ini upgrade head

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
