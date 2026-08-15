import os
import json
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from core.database import save_analysis, get_user_analyses, get_analysis_by_id
from core import data_processing as dp
from core import ml_model as ml
from core import safety_analysis as sa
from core import pdf_extraction as pe
from core import report_generator as rg
from api.dependencies import get_current_user

router = APIRouter()

class CompositionInput(BaseModel):
    Al: Optional[float] = 0
    Al2O3: Optional[float] = 0
    Si: Optional[float] = 0
    Fe: Optional[float] = 0
    Mg: Optional[float] = 0
    Cu: Optional[float] = 0
    Zn: Optional[float] = 0
    Mn: Optional[float] = 0
    Ni: Optional[float] = 0
    Ca: Optional[float] = 0
    Na: Optional[float] = 0
    K: Optional[float] = 0
    Ti: Optional[float] = 0

class AnalysisRunRequest(BaseModel):
    sample_id: str
    sample_type: str
    source: str
    test_method: str
    input_method: str
    composition: CompositionInput

class AnalysisResultResponse(BaseModel):
    analysis_id: int
    metal_recovery: float
    alumina_recovery: float
    recovery_category: str
    best_method: str
    method_reason: str
    model_used: str
    model_type: str
    sufficient_data: bool
    n_samples: int
    r2_metal: Optional[float]
    mae_metal: Optional[float]
    rmse_metal: Optional[float]
    r2_alumina: Optional[float]
    mae_alumina: Optional[float]
    rmse_alumina: Optional[float]
    safety_summary: dict
    industrial_apps: list
    environmental_benefits: list
    composition: dict
    sds_sections: Optional[dict] = None
    sds_product_name: Optional[str] = None

@router.post("/upload", response_model=dict)
async def upload_file(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    # Save file temporarily
    file_location = f"uploads/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Determine file type and extract data
    ext = file.filename.split(".")[-1].lower()
    extracted = {}
    sds_sections = None
    sds_product_name = None

    if ext == "pdf":
        with open(file_location, "rb") as f:
            pdf_bytes = f.read()
        extracted = pe.extract_composition_from_pdf(pdf_bytes)
        sds_sections = pe.extract_sds_sections(pdf_bytes)
        sds_product_name = pe.get_sds_product_name(pdf_bytes)
    elif ext == "csv":
        import pandas as pd
        df = pd.read_csv(file_location)
        extracted = dp.map_uploaded_columns_to_composition(df)
    elif ext in ["xlsx", "xls"]:
        import pandas as pd
        df = pd.read_excel(file_location)
        extracted = dp.map_uploaded_columns_to_composition(df)
    else:
        os.remove(file_location)
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Cleanup: delete uploaded file after extraction
    os.remove(file_location)

    return {
        "extracted_composition": extracted,
        "sds_sections": sds_sections,
        "sds_product_name": sds_product_name,
    }

@router.post("/run", response_model=AnalysisResultResponse)
async def run_analysis(request: AnalysisRunRequest, current_user: dict = Depends(get_current_user)):
    # Validate composition
    comp_dict = request.composition.dict()
    is_valid, cleaned, errors = dp.validate_composition(comp_dict)
    if not is_valid:
        raise HTTPException(status_code=400, detail={"errors": errors})

    # Load dataset and train model
    dataset = ml.load_dataset()
    demo_mode = ml.is_demo_dataset(dataset)
    trained = ml.train_and_evaluate(dataset, model_type="Random Forest")  # default

    # Predict
    if trained["sufficient"]:
        metal_pred, alumina_pred = ml.predict_recovery(trained, cleaned)
        model_used = "Random Forest"
        model_type = "DEMO dataset" if demo_mode else "User-provided dataset"
    else:
        # Rule-based fallback
        al = cleaned.get("Al", 0)
        al2o3 = cleaned.get("Al2O3", 0)
        metal_pred = min(95.0, al * 0.8)
        alumina_pred = min(95.0, al2o3 * 0.8)
        model_used = "Rule-based estimate (DEMO - insufficient data)"
        model_type = "Rule-based"

    category = ml.recovery_category(metal_pred, alumina_pred)
    best_method, reason = ml.recommend_method(cleaned, metal_pred, alumina_pred)

    # Safety (no SDS here)
    safety = sa.build_safety_summary(cleaned, None)

    industrial_apps = sa.industrial_applications(cleaned, metal_pred, alumina_pred)
    env_benefits = sa.environmental_benefits()

    # Save to database
    analysis_id = save_analysis(current_user["id"], {
        "sample_id": request.sample_id,
        "sample_type": request.sample_type,
        "source": request.source,
        "test_method": request.test_method,
        "input_method": request.input_method,
        "composition_json": json.dumps(cleaned),
        "metal_recovery": metal_pred,
        "alumina_recovery": alumina_pred,
        "recovery_category": category,
        "best_method": best_method,
        "method_reason": reason,
        "risk_level": safety["risk_level"],
        "model_used": model_used,
        "model_type": model_type,
        "r2_metal": trained["metal"]["r2"] if trained["sufficient"] else None,
        "mae_metal": trained["metal"]["mae"] if trained["sufficient"] else None,
        "rmse_metal": trained["metal"]["rmse"] if trained["sufficient"] else None,
        "r2_alumina": trained["alumina"]["r2"] if trained["sufficient"] else None,
        "mae_alumina": trained["alumina"]["mae"] if trained["sufficient"] else None,
        "rmse_alumina": trained["alumina"]["rmse"] if trained["sufficient"] else None,
    })

    return {
        "analysis_id": analysis_id,
        "metal_recovery": metal_pred,
        "alumina_recovery": alumina_pred,
        "recovery_category": category,
        "best_method": best_method,
        "method_reason": reason,
        "model_used": model_used,
        "model_type": model_type,
        "sufficient_data": trained["sufficient"],
        "n_samples": trained["n_samples"],
        "r2_metal": trained["metal"]["r2"] if trained["sufficient"] else None,
        "mae_metal": trained["metal"]["mae"] if trained["sufficient"] else None,
        "rmse_metal": trained["metal"]["rmse"] if trained["sufficient"] else None,
        "r2_alumina": trained["alumina"]["r2"] if trained["sufficient"] else None,
        "mae_alumina": trained["alumina"]["mae"] if trained["sufficient"] else None,
        "rmse_alumina": trained["alumina"]["rmse"] if trained["sufficient"] else None,
        "safety_summary": safety,
        "industrial_apps": industrial_apps,
        "environmental_benefits": env_benefits,
        "composition": cleaned,
        "sds_sections": None,
        "sds_product_name": None,
    }

@router.get("/history", response_model=List[dict])
async def get_analysis_history(current_user: dict = Depends(get_current_user)):
    rows = get_user_analyses(current_user["id"])
    for row in rows:
        row["created_at"] = str(row["created_at"])
    return rows

@router.get("/{analysis_id}", response_model=dict)
async def get_analysis(analysis_id: int, current_user: dict = Depends(get_current_user)):
    analysis = get_analysis_by_id(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    if analysis["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    analysis["created_at"] = str(analysis["created_at"])
    return analysis
