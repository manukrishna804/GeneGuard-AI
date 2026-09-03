from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database.session import get_db
from app.modules.patient.model import Patient
from app.modules.wes_analysis.model import WESReport
from app.modules.wes_analysis.pipeline import analyze_wes_report


router = APIRouter(
    prefix="/wes",
    tags=["WES"],
)


@router.get("/ping")
def ping():
    return {"message": "WES analysis module is working"}


@router.get("/db-test")
def db_test(db: Session = Depends(get_db)):
    return {
        "database": "connected",
        "result": db.execute("SELECT 1").scalar(),
    }


@router.post("/analyze")
async def analyze_wes(
    patient_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # --------------------------------------------------
    # Validate file
    # --------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="A PDF file is required.",
        )

    if Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    # --------------------------------------------------
    # Verify patient
    # --------------------------------------------------

    patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id)
        .first()
    )

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail=f"Patient {patient_id} not found.",
        )

    # --------------------------------------------------
    # Save uploaded PDF temporarily
    # --------------------------------------------------

    temp_path = None

    try:
        contents = await file.read()

        if not contents:
            raise HTTPException(
                status_code=400,
                detail="Uploaded PDF is empty.",
            )

        with NamedTemporaryFile(
            suffix=".pdf",
            delete=False,
        ) as temp_file:
            temp_file.write(contents)
            temp_path = temp_file.name

        # --------------------------------------------------
        # Run existing WES pipeline
        # --------------------------------------------------

        results = analyze_wes_report(temp_path)

        # --------------------------------------------------
        # Save analysis to database
        # --------------------------------------------------

        report = WESReport(
            patient_id=patient_id,
            report_name=file.filename,
            status="completed",
            analysis_result=results,
        )

        db.add(report)
        db.commit()
        db.refresh(report)

        return {
            "report_id": report.id,
            "patient_id": report.patient_id,
            "report_name": report.report_name,
            "status": report.status,
            "variant_count": len(results),
            "results": results,
        }

    except HTTPException:
        raise

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"WES analysis failed: {str(exc)}",
        ) from exc

    finally:
        if temp_path:
            try:
                Path(temp_path).unlink(missing_ok=True)
            except Exception:
                pass