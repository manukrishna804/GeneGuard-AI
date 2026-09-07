from fastapi import APIRouter

from app.modules.patient.router import router as patient_router
from app.modules.wes_analysis.router import router as wes_router
from app.modules.facial_phenotype.router import router as phenotype_router
from app.modules.lifestyle.router import router as lifestyle_router
from app.modules.consanguinity.router import router as consanguinity_router
from app.modules.family_pedigree.router import router as family_pedigree_router
from app.modules.pharmacogenomics.router import router as pharmacogenomics_router
from app.modules.report.router import router as report_router

router = APIRouter()

router.include_router(patient_router)
router.include_router(wes_router)
router.include_router(phenotype_router)
router.include_router(lifestyle_router)
router.include_router(consanguinity_router)
router.include_router(family_pedigree_router)
router.include_router(pharmacogenomics_router)
router.include_router(report_router)

@router.get("/ping", tags=["Health"])
def ping():
    return {
        "message": "GeneGuard API is working successfully 🚀"
    }