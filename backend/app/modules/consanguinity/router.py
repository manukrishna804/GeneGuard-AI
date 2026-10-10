from __future__ import annotations

import json
import os
import tempfile

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from .schemas import (
    ConsanguinityInfo,
    ConsanguinityType,
    FamilyHistoryEntry,
)
from .service import assess_offspring_risk_from_vcfs


router = APIRouter(
    prefix="/consanguinity",
    tags=["consanguinity"],
)


@router.post("/assess-vcf")
async def assess_vcf(
    parent1_vcf: UploadFile = File(...),
    parent2_vcf: UploadFile = File(...),
    relationship: ConsanguinityType = Form(
        ConsanguinityType.UNKNOWN
    ),
    family_history: str = Form("[]"),
):
    """
    Assess offspring genetic risk using two parental VCF files,
    consanguinity information, and optional family history.
    """

    parent1_temp_path = None
    parent2_temp_path = None

    try:
        # -----------------------------------------------------
        # 1. Read uploaded VCF files
        # -----------------------------------------------------

        parent1_content = await parent1_vcf.read()
        parent2_content = await parent2_vcf.read()

        # -----------------------------------------------------
        # 2. Store VCFs temporarily
        # -----------------------------------------------------

        with tempfile.NamedTemporaryFile(
            mode="wb",
            suffix=".vcf",
            delete=False,
        ) as temp1:

            temp1.write(parent1_content)
            parent1_temp_path = temp1.name

        with tempfile.NamedTemporaryFile(
            mode="wb",
            suffix=".vcf",
            delete=False,
        ) as temp2:

            temp2.write(parent2_content)
            parent2_temp_path = temp2.name

        # -----------------------------------------------------
        # 3. Build consanguinity information
        # -----------------------------------------------------

        consanguinity = ConsanguinityInfo(
            relationship=relationship
        )

        # -----------------------------------------------------
        # 4. Parse family history JSON
        # -----------------------------------------------------

        try:
            family_history_data = json.loads(
                family_history
            )

            if not isinstance(
                family_history_data,
                list,
            ):
                raise ValueError(
                    "Family history must be a JSON list."
                )

            family_history_entries = [
                FamilyHistoryEntry.model_validate(entry)
                for entry in family_history_data
            ]

        except (json.JSONDecodeError, ValueError) as exc:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid family_history JSON: "
                    f"{str(exc)}"
                ),
            )

        # -----------------------------------------------------
        # 5. Run Module 4 assessment
        # -----------------------------------------------------

        result = assess_offspring_risk_from_vcfs(
            parent1_temp_path,
            parent2_temp_path,
            consanguinity,
            family_history_entries,
        )

        return result

    except UnicodeDecodeError:

        raise HTTPException(
            status_code=400,
            detail="VCF files must be valid UTF-8 text files.",
        )

    except HTTPException:

        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to assess parental VCFs: "
                f"{str(exc)}"
            ),
        )

    finally:

        if (
            parent1_temp_path
            and os.path.exists(parent1_temp_path)
        ):
            os.remove(parent1_temp_path)

        if (
            parent2_temp_path
            and os.path.exists(parent2_temp_path)
        ):
            os.remove(parent2_temp_path)