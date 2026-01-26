SHELL := /bin/bash

test:
	@echo "Running unit tests..."
	uv run coverage run -m pytest ${module} && \
	uv run coverage html && \
	uv run coverage report
	@echo
	@echo "Ruff errors in code ----------------"
	@echo
	@echo "--------------------------------------"
	uvx ruff check
	@echo "OK, no ruff errors in code"
	@echo "--------------------------------------"