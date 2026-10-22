FROM python:3.14.8-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN useradd --create-home appuser \
    && mkdir -p /app/results \
    && chown -R appuser:appuser /app

COPY src/ ./src/
COPY prompts/ ./prompts/

USER appuser

ENV RESULTS_DIR=/app/results

ENTRYPOINT ["python", "src/inference.py"]