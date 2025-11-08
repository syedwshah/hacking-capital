PYTHON ?= python
UVICORN ?= uvicorn
STREAMLIT ?= streamlit

.PHONY: run-api run-ui test fmt env

run-api:
	$(UVICORN) app.main:app --reload --host 0.0.0.0 --port 8000

run-ui:
	$(STREAMLIT) run ui/App.py

test:
	$(PYTHON) -m pytest

fmt:
	ruff check --fix .

# Generate a .env file in project root (avoids committing secrets)
# Includes the hackathon-provided key under both OPENAI_API_KEY and OPENAL_API_KEY.
env:
	@echo "DATABASE_URL=sqlite:///./hacking_capital.db" > .env
	@echo "REDIS_URL=redis://localhost:6379/0" >> .env
	@echo "ALPHAVANTAGE_API_KEY=replace_with_key" >> .env
	@echo "OPENAI_API_KEY=Im_01423b64/22®233b3244911c19dab5c" >> .env
	@echo "OPENAL_API_KEY=Im_01423b64/22®233b3244911c19dab5c" >> .env
	@echo "Wrote .env with defaults"


