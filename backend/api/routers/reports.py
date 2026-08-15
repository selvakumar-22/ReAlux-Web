import os
import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from core.database import (
    get_analysis_by_id,
    save_report_record,
    get_user_reports,
    get_report_by_id,
)

from core.report_generator import generate_report
from api.dependencies import get_current_user


router = APIRouter()


# ============================================================
# GENERATE REPORT
# ============================================================

@router.post("/generate")
async def generate_report_endpoint(
    analysis_id: int,
    current_user: dict = Depends(get_current_user),
):
    # --------------------------------------------------------
    # 1. Get analysis
    # --------------------------------------------------------

    analysis = get_analysis_by_id(analysis_id)

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found",
        )

    # --------------------------------------------------------
    # 2. Check ownership
    # --------------------------------------------------------

    if analysis["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )

    # --------------------------------------------------------
    # 3. Prepare report data
    # --------------------------------------------------------

    composition = {}

    if analysis.get("composition_json"):
        try:
            composition = json.loads(
                analysis["composition_json"]
            )
        except Exception:
            composition = {}

    data = {
        "sample_id": analysis.get("sample_id"),
        "sample_type": analysis.get("sample_type"),
        "source": analysis.get("source"),

        "date": datetime.now().strftime("%Y-%m-%d"),

        "test_method": analysis.get("test_method"),
        "input_method": analysis.get("input_method"),

        "data_source_label": analysis.get("input_method"),

        "composition": composition,

        # ----------------------------------------------------
        # Recovery results
        # ----------------------------------------------------

        "metal_recovery": analysis.get("metal_recovery"),
        "alumina_recovery": analysis.get("alumina_recovery"),
        "recovery_category": analysis.get("recovery_category"),

        # ----------------------------------------------------
        # Recommended method
        # ----------------------------------------------------

        "best_method": analysis.get("best_method"),
        "method_reason": analysis.get("method_reason"),

        # ----------------------------------------------------
        # Model information
        # ----------------------------------------------------

        "model_used": analysis.get("model_used"),
        "model_type": analysis.get("model_type"),

        "demo_mode": analysis.get("model_type")
        in ["DEMO dataset", "Rule-based"],

        "sufficient_data": analysis.get("r2_metal") is not None,

        "n_samples": None,

        # ----------------------------------------------------
        # Metal model metrics
        # ----------------------------------------------------

        "r2_metal": analysis.get("r2_metal"),
        "mae_metal": analysis.get("mae_metal"),
        "rmse_metal": analysis.get("rmse_metal"),

        # ----------------------------------------------------
        # Alumina model metrics
        # ----------------------------------------------------

        "r2_alumina": analysis.get("r2_alumina"),
        "mae_alumina": analysis.get("mae_alumina"),
        "rmse_alumina": analysis.get("rmse_alumina"),

        # ----------------------------------------------------
        # Safety information
        # ----------------------------------------------------

        "safety_summary": {
            "risk_level": analysis.get("risk_level"),

            "classification_note": (
                "Safety classification requires verified "
                "SDS/laboratory data."
            ),

            "composition_concerns": [],

            "handling_advice": (
                "Avoid generating or breathing dust. "
                "Use non-sparking tools. "
                "Keep away from ignition sources."
            ),

            "storage_advice": (
                "Store in a dry, cool, well-ventilated area, "
                "away from moisture, in closed containers."
            ),

            "ppe_advice": (
                "Safety glasses, protective gloves, and "
                "dust-appropriate respiratory protection "
                "where ventilation is insufficient."
            ),

            "detox_treatment_advice": (
                "Rinse skin/eyes with water for at least "
                "15 minutes; seek medical attention if "
                "irritation persists."
            ),

            "disposal_advice": (
                "Dispose in accordance with local, regional, "
                "and national waste regulations."
            ),

            "sds_available": False,

            "sds_hazards_text": (
                "Information not available."
            ),
        },

        # ----------------------------------------------------
        # Additional report sections
        # ----------------------------------------------------

        "industrial_apps": [],

        "environmental_benefits": [],

        "sds_sections": None,

        "sds_product_name": None,
    }

    # ========================================================
    # 4. Create reports folder
    # ========================================================

    reports_dir = "reports"

    os.makedirs(
        reports_dir,
        exist_ok=True,
    )

    # ========================================================
    # 5. Create PDF filename
    # ========================================================

    sample_id = (
        analysis.get("sample_id")
        or "sample"
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d%H%M%S"
    )

    filename = (
        f"ReAlux_Report_"
        f"{sample_id}_"
        f"{timestamp}.pdf"
    )

    filepath = os.path.join(
        reports_dir,
        filename,
    )

    # ========================================================
    # 6. Generate PDF
    # ========================================================

    try:
        generate_report(
            filepath,
            data,
        )

    except Exception as e:
        print(
            "REPORT GENERATION ERROR:",
            str(e),
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Report generation failed: {str(e)}"
            ),
        )

    # ========================================================
    # 7. Save report record
    # ========================================================

    try:
        report_id = save_report_record(
            analysis_id,
            current_user["id"],
            filepath,
        )

    except Exception as e:
        print(
            "REPORT DATABASE ERROR:",
            str(e),
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Report record could not be saved: {str(e)}"
            ),
        )

    # ========================================================
    # 8. If save_report_record doesn't return ID,
    #    find the newly-created report from history
    # ========================================================

    if report_id is None:

        try:
            reports = get_user_reports(
                current_user["id"]
            )

            # Search newest matching report
            for report in reversed(reports):

                report_analysis_id = report.get(
                    "analysis_id"
                )

                report_filepath = report.get(
                    "filepath"
                )

                if (
                    report_analysis_id == analysis_id
                    and report_filepath == filepath
                ):
                    report_id = (
                        report.get("id")
                        or report.get("report_id")
                    )

                    break

        except Exception as e:
            print(
                "REPORT HISTORY ERROR:",
                str(e),
            )

    # ========================================================
    # 9. Final check
    # ========================================================

    if report_id is None:

        print(
            "WARNING: PDF generated successfully "
            "but report_id was not returned/found."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Report PDF generated, "
                "but report_id could not be found."
            ),
        )

    # ========================================================
    # 10. Return report_id to frontend
    # ========================================================

    return {
        "report_id": report_id,
        "filepath": filepath,
        "filename": filename,
    }


# ============================================================
# DOWNLOAD REPORT
# ============================================================

@router.get("/download/{report_id}")
async def download_report(
    report_id: int,
    current_user: dict = Depends(get_current_user),
):

    # --------------------------------------------------------
    # 1. Get report
    # --------------------------------------------------------

    report = get_report_by_id(
        report_id
    )

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )

    # --------------------------------------------------------
    # 2. Check ownership
    # --------------------------------------------------------

    if report["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )

    # --------------------------------------------------------
    # 3. Get filepath
    # --------------------------------------------------------

    filepath = report.get(
        "filepath"
    )

    if not filepath:
        raise HTTPException(
            status_code=404,
            detail="Report filepath not found",
        )

    # --------------------------------------------------------
    # 4. Check file exists
    # --------------------------------------------------------

    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=404,
            detail="Report file not found",
        )

    # --------------------------------------------------------
    # 5. Return PDF
    # --------------------------------------------------------

    return FileResponse(
        filepath,
        media_type="application/pdf",
        filename=os.path.basename(filepath),
    )


# ============================================================
# REPORT HISTORY
# ============================================================

@router.get("/history")
async def list_reports(
    current_user: dict = Depends(get_current_user),
):

    return get_user_reports(
        current_user["id"]
    )