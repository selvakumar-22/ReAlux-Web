import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import auth, analyses, reports, dataset
from core.database import init_db
from core.ml_model import ensure_dataset_exists

app = FastAPI(title="ReAlux API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(analyses.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(dataset.router, prefix="/api/dataset", tags=["dataset"])

os.makedirs("uploads", exist_ok=True)
os.makedirs("reports", exist_ok=True)
init_db()
ensure_dataset_exists()

@app.get("/")
async def root():
    return {"message": "ReAlux Backend is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
