# AI Agent

A professional, modular AI Agent built with Python.

## Status
- [x] Phase 1 - Environment & project structure
- [ ] Phase 2 - Data analysis engine
- [ ] Phase 3 - LLM integration
- [ ] Phase 4 - Agent loop
- [ ] Phase 5 - CSV/Excel upload & auto-analysis
- [ ] Phase 6 - Charts, reports, dashboard
- [ ] Phase 7 - Memory & error handling
- [ ] Phase 8 - Security, logging, testing
- [ ] Phase 9 - Professional UI
- [ ] Phase 10 - Deployment

## Setup (Windows PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
python -m src.main

## Structure
ai-agent/
  src/           App source
  tests/         Tests
  data/          Local data
  reports/       Generated reports
  logs/          Logs
  docs/          Documentation
  .streamlit/    Streamlit config
