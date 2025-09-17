# PDF Validator Agent Makefile

.PHONY: help install test run-api run-cli clean setup

# Default target
help:
	@echo "PDF Validator Agent - Available Commands:"
	@echo ""
	@echo "  setup     - Setup the project (install dependencies, create .env)"
	@echo "  install   - Install Python dependencies"
	@echo "  test      - Run tests"
	@echo "  run-api   - Start the API server"
	@echo "  run-cli   - Show CLI help"
	@echo "  clean     - Clean temporary files"
	@echo "  config    - Show current configuration"
	@echo ""
	@echo "Examples:"
	@echo "  make setup"
	@echo "  make run-api"
	@echo "  python cli_validator.py document.pdf"

# Setup project
setup:
	@echo "Setting up PDF Validator Agent..."
	python setup.py

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

# Run tests
test:
	@echo "Running tests..."
	python test_validator.py

# Run tests with real PDF
test-real:
	@echo "Running tests with real PDF..."
	python test_validator.py --real-pdf

# Start API server
run-api:
	@echo "Starting API server..."
	python api_server.py

# Show CLI help
run-cli:
	@echo "CLI Usage:"
	python cli_validator.py --help

# Show configuration
config:
	@echo "Current configuration:"
	python cli_validator.py --config

# Clean temporary files
clean:
	@echo "Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.log" -delete
	rm -rf logs/*.log
	rm -rf temp/*
	rm -rf output/*.json

# Create directories
dirs:
	@echo "Creating directories..."
	mkdir -p logs temp output

# Run example
example:
	@echo "Running example usage..."
	python example_usage.py

# Validate single PDF (usage: make validate FILE=document.pdf)
validate:
	@if [ -z "$(FILE)" ]; then \
		echo "Usage: make validate FILE=document.pdf"; \
		exit 1; \
	fi
	python cli_validator.py --verbose --detailed $(FILE)

# Validate batch (usage: make validate-batch FOLDER=folder_with_pdfs)
validate-batch:
	@if [ -z "$(FOLDER)" ]; then \
		echo "Usage: make validate-batch FOLDER=folder_with_pdfs"; \
		exit 1; \
	fi
	python cli_validator.py --batch --verbose $(FOLDER)

# Development setup
dev-setup: install dirs
	@echo "Development setup complete"
	@echo "Don't forget to:"
	@echo "1. Copy env_example.txt to .env"
	@echo "2. Add your API keys to .env"
	@echo "3. Run 'make test' to verify setup"

# Production setup
prod-setup: install dirs
	@echo "Production setup complete"
	@echo "Make sure to:"
	@echo "1. Set proper environment variables"
	@echo "2. Configure logging"
	@echo "3. Set up monitoring"

# Show project status
status:
	@echo "PDF Validator Agent Status:"
	@echo "=========================="
	@python -c "from config import settings; print(f'App: {settings.app_name}'); print(f'Google API: {\"✓\" if settings.google_api_key else \"✗\"}'); print(f'Langfuse: {\"✓\" if settings.langfuse_public_key else \"✗\"}')"
	@echo ""
	@echo "Files:"
	@ls -la *.py | wc -l | xargs echo "Python files:"
	@echo ""
	@echo "Dependencies:"
	@pip list | grep -E "(google|langfuse|fastapi|pdf)" || echo "Dependencies not installed"
