.PHONY: venv install ingest serve test benchmark clean

venv:
	python3 -m venv .venv

install: venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt

ingest:
	.venv/bin/python -m search_engine.cli ingest --corpus data/sample_corpus --output data/index --shards 4

serve:
	.venv/bin/uvicorn search_engine.api.app:create_app --factory --reload --host 127.0.0.1 --port 8000

test:
	.venv/bin/pytest

benchmark:
	.venv/bin/python -m search_engine.cli benchmark --index data/index --queries "distributed search" "page rank" "python web api" --runs 30 --workers 4

clean:
	rm -rf data/index results/benchmark_results.json .pytest_cache __pycache__

