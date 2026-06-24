.PHONY: all format lint test deps run build

all: format lint

format:
	@uvx ruff format src tests

lint:
	@uvx ruff check src tests

fix:
	@uvx ruff check src tests --fix

test:
	@uvx pytest

deps:
	@uvx pydeps src/DiploGM -T png -o dependencies.png --config pyproject.toml

run: format lint
	@echo --- Starting Program ---
	@uvx run main

build: format lint test deps

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete
	rm -rf build dist

clean-win:
	powershell -Command "Get-ChildItem -Recurse -Include __pycache__ | Remove-Item -Recurse -Force"
	powershell -Command "if (Test-Path '.mypy_cache') { Remove-Item '.mypy_cache' -Recurse -Force }"
	powershell -Command "if (Test-Path '.pytest_cache') { Remove-Item '.pytest_cache' -Recurse -Force }"
	powershell -Command "if (Test-Path '.ruff_cache') { Remove-Item '.ruff_cache' -Recurse -Force }"
	powershell -Command "Get-ChildItem -Recurse -Include *.egg-info | Remove-Item -Recurse -Force"
	powershell -Command "Remove-Item *.pyc -Recurse -Force"
	powershell -Command "Remove-Item *.coverage -Recurse -Force"
