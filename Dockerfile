FROM python:3.11-slim

RUN useradd -u 1000 -m appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py agent_executor.py ./

USER appuser

EXPOSE 8000

CMD ["python", "main.py"]
