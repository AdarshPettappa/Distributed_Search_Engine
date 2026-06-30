FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python -m search_engine.cli ingest --corpus data/sample_corpus --output data/index --shards 4

EXPOSE 8000
CMD ["uvicorn", "search_engine.api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]

