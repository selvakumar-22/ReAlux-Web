# ReAlux Web

Modern React + Vite frontend with a FastAPI backend for aluminium dross recovery analysis.

## Run on Windows / VS Code

### Terminal 1 — backend
```bat
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app:app --reload --port 8000
```

### Terminal 2 — frontend
```bat
cd frontend
npm install
npm run dev
```

Open: http://localhost:5173

Backend API: http://localhost:8000
API docs: http://localhost:8000/docs

The backend creates a demo dataset and SQLite database automatically.

## Important
The original Streamlit `app.py` is preserved as `legacy_streamlit_app.py` for reference. The new web app uses FastAPI + React instead.
