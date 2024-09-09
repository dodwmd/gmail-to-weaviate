.PHONY: build run test lint

build:
	docker build -t gmail-to-weaviate .

run:
	docker run --rm -it gmail-to-weaviate

test:
	python -m pytest tests/

lint:
	flake8 .

setup:
	pip install -r requirements.txt
