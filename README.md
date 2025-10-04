# Customer Feedback Prioritizer (Offline Streamlit Demo)
This is an **offline** Streamlit demonstration of the Customer Feedback Prioritizer multi-agent system.  
Everything runs locally — **no API keys** required. The app simulates the 5 agents using sample CSVs and rule-based / TF-IDF methods.

## Features
- Collect & deduplicate feedback (TF-IDF + cosine similarity)
- Enrich feedback with sample CRM / revenue data
- Categorize feedback (keyword-based)
- Score priority using revenue-weighted formula from the spec
- Generate a weekly report (Markdown & CSV) and "deliver" locally into `deliveries/`
- Export everything as CSV/JSON for integration
- Streamlit UI to run each step and inspect outputs

## Requirements
Create a virtual environment and install dependencies:
```
python -m venv venv
venv\Scripts\activate    # Windows
# OR
source venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
```

## Run
From the project root in a command prompt:
```
streamlit run app.py
```
This opens the app in your browser (or shows a local URL in the terminal).

## Project structure
```
feedback_prioritizer_project/
├─ app.py               # Streamlit app (entry)
├─ agents/              # Agent modules (collector, enricher, categorizer, scorer, reporter)
├─ data/                # sample CSVs (feedback + crm)
├─ deliveries/          # weekly reports and simulated Notion/Slack/Email outputs
├─ requirements.txt
├─ README.md
```
All outputs and exports are placed under `deliveries/` so you can inspect them without any external service.

## Notes
- This is a demo: LLM tasks are simulated using rule-based logic & heuristics so no LLM/API required.
- You can replace or extend algorithms in `agents/` with ML models later.
