# CVE.ICU Makefile
# Task runner for common build and development operations

.PHONY: help build quick test lint clean serve install

# Default target
help:
	@echo "CVE.ICU Build System"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Local Development:"
	@echo "  build     - Full site build (data + templates)"
	@echo "  quick     - Quick template-only build (no data regeneration)"
	@echo "  test      - Run test suite"
	@echo "  lint      - Run linters (flake8)"
	@echo "  clean     - Clean build artifacts"
	@echo "  serve     - Start local development server"
	@echo "  install   - Install Python dependencies"
	@echo "  dev       - Quick build + serve (development workflow)"
	@echo ""
	@echo "Data Rebuild Targets:"
	@echo "  rebuild-cna       - Rebuild CNA analysis only"
	@echo "  rebuild-cpe       - Rebuild CPE analysis only"
	@echo "  rebuild-cvss      - Rebuild CVSS analysis only"
	@echo "  rebuild-cwe       - Rebuild CWE analysis only"
	@echo "  rebuild-growth    - Rebuild growth analysis only"
	@echo "  rebuild-quality   - Rebuild data quality analysis only"
	@echo "  rebuild-nvd-status - Rebuild NVD status analysis only"
	@echo "  rebuild-all       - Rebuild all analysis files"
	@echo ""
	@echo "Docker Targets:"
	@echo "  docker-build   - Build Docker image"
	@echo "  docker-run     - Run container (detached)"
	@echo "  docker-up      - Run container (foreground with logs)"
	@echo "  docker-stop    - Stop container"
	@echo "  docker-logs    - View container logs"
	@echo "  docker-shell   - Shell into container"
	@echo "  docker-update  - Trigger manual update in container"
	@echo "  docker-rebuild - Full rebuild in container"
	@echo "  docker-quick   - Quick rebuild in container"
	@echo "  docker-clean   - Remove Docker resources"
	@echo "  docker         - Build + run (full Docker workflow)"

# Install dependencies
install:
	pip install -r requirements.txt

# Full build
build:
	python build.py

# Quick template-only build
quick:
	python data/scripts/quick_build.py

# Run tests
test:
	python -m pytest tests/ -v

# Run tests with coverage
test-coverage:
	python -m pytest tests/ -v --cov=data --cov-report=term-missing

# Run linters
lint:
	python -m flake8 data/ --max-line-length=120 --ignore=E501,W503

# Clean build artifacts
clean:
	rm -rf web/*.html
	rm -rf web/data/*.json
	rm -rf __pycache__
	rm -rf data/__pycache__
	rm -rf data/scripts/__pycache__
	rm -rf tests/__pycache__
	rm -rf .pytest_cache
	rm -rf .coverage

# Start local development server
serve:
	@echo "Starting local server at http://localhost:8000"
	cd web && python -m http.server 8000

# Individual rebuild targets
rebuild-cna:
	python data/scripts/rebuild_cna.py

rebuild-cpe:
	python data/scripts/rebuild_cpe.py

rebuild-cvss:
	python data/scripts/rebuild_cvss.py

rebuild-cwe:
	python data/scripts/rebuild_cwe.py

rebuild-growth:
	python data/scripts/rebuild_growth.py

rebuild-quality:
	python data/scripts/rebuild_data_quality.py

rebuild-nvd-status:
	python data/scripts/rebuild_nvd_status.py

# Rebuild all analysis files without full build
rebuild-all: rebuild-cna rebuild-cpe rebuild-cvss rebuild-cwe rebuild-growth rebuild-quality rebuild-nvd-status
	@echo "All analysis files rebuilt"

# Validate JSON schemas
validate:
	python -m pytest tests/test_schemas.py -v

# Development workflow: quick build + serve
dev: quick serve

# ============================================
# Docker targets
# ============================================

.PHONY: docker-build docker-run docker-stop docker-logs docker-shell docker-clean

# Build Docker image
docker-build:
	docker-compose build

# Run Docker container (detached)
docker-run:
	docker-compose up -d

# Run Docker container (foreground with logs)
docker-up:
	docker-compose up

# Stop Docker container
docker-stop:
	docker-compose down

# View Docker logs
docker-logs:
	docker-compose logs -f

# Shell into running container
docker-shell:
	docker-compose exec cveicu /bin/bash

# Trigger manual update in container
docker-update:
	docker-compose exec cveicu /docker-entrypoint.sh update

# Full rebuild in container
docker-rebuild:
	docker-compose exec cveicu /docker-entrypoint.sh build full

# Quick rebuild in container
docker-quick:
	docker-compose exec cveicu /docker-entrypoint.sh build quick

# Remove Docker resources
docker-clean:
	docker-compose down -v --rmi local
	rm -rf logs/

# Full Docker workflow: build + run
docker: docker-build docker-run
	@echo "CVE.ICU container running at http://localhost:8090"
