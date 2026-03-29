FROM python:3.11-slim

WORKDIR /app
COPY mock_ai.py .

RUN pip install fastapi uvicorn

CMD ["uvicorn", "mock_ai:app", "--host", "0.0.0.0", "--port", "8000"]