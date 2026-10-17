FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ELM369_DB_PATH=/data/elm369_transactions.sqlite3

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt \
    && addgroup --system app \
    && adduser --system --ingroup app app \
    && mkdir /data \
    && chown app:app /data

COPY elm369_api.py elm369_db.py elm369_matrix_engine.py /app/

USER app
EXPOSE 8000

CMD ["uvicorn", "elm369_api:app", "--host", "0.0.0.0", "--port", "8000"]
