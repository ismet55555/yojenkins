.PHONY: install install-dev build serve dev clean help

PYTHON ?= python3
NPM ?= npm

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install Python package with web extras
	$(PYTHON) -m pip install -e ".[web]"

install-dev: install  ## Install all deps including frontend node_modules
	cd webapp && $(NPM) ci

build:  ## Build the frontend
	cd webapp && $(NPM) run build

serve:  ## Start production server (auto-builds frontend if needed)
	$(PYTHON) -m yojenkins serve

dev:  ## Start dev servers (API with reload + Vite hot-reload)
	@echo "Starting backend (API-only) and Vite dev server..."
	@$(PYTHON) -m yojenkins serve --reload --no-frontend & cd webapp && $(NPM) run dev

clean:  ## Remove build artifacts
	rm -rf webapp/dist webapp/node_modules
