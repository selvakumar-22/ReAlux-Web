import os
import shutil
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from core.ml_model import load_dataset, is_demo_dataset, DATA_PATH
from core.data_processing import check_dataset_quality
from api.dependencies import get_current_user

router = APIRouter()

@router.get("/")
async def get_dataset(current_user: dict = Depends(get_current_user)):
    df = load_dataset()
    stats = check_dataset_quality(df)
    return {
        "rows": df.head(100).to_dict(orient="records"),
        "columns": list(df.columns),
        "stats": stats,
        "is_demo": is_demo_dataset(df)
    }

@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    file_location = DATA_PATH
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"message": "Dataset replaced successfully"}
