from app.core.database.session import SessionLocal
from app.modules.patient.model import Patient
from app.modules.wes_analysis.model import WESReport


def main():
    db = SessionLocal()

    try:
        # Create a test patient
        patient = Patient(
            full_name="WES DB Test",
            age=30,
            gender="Unknown",
            email="wes-db-test@example.com",
        )

        db.add(patient)
        db.flush()

        # Create a WES report
        report = WESReport(
            patient_id=patient.id,
            report_name="medgenome_report.pdf",
            file_path="app/modules/wes_analysis/medgenome_report.pdf",
            status="completed",
            analysis_result={
                "test": True,
                "variant_count": 2,
            },
        )

        db.add(report)
        db.commit()
        db.refresh(report)

        print("Patient ID:", patient.id)
        print("WES Report ID:", report.id)
        print("Status:", report.status)
        print("Analysis result:", report.analysis_result)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()