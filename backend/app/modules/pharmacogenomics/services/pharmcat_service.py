import asyncio
import json
import shutil
from pathlib import Path
from uuid import uuid4


# backend/ directory
BACKEND_DIR = Path(__file__).resolve().parents[4]

# Shared with the PharmCAT container at /data/jobs
JOBS_DIR = BACKEND_DIR / "jobs"

PHARMCAT_TIMEOUT_SECONDS = 300


async def run_pharmcat(vcf_content: bytes) -> dict:
    """
    Submit a VCF to the separate PharmCAT worker and return its JSON report.
    """

    if not vcf_content:
        raise ValueError("The uploaded VCF file is empty.")

    JOBS_DIR.mkdir(parents=True, exist_ok=True)

    job_dir = JOBS_DIR / uuid4().hex
    output_dir = job_dir / "output"

    job_dir.mkdir()
    output_dir.mkdir()

    try:
        # Write the input before signalling the worker.
        (job_dir / "input.vcf").write_bytes(vcf_content)

        # The worker starts processing after this file appears.
        (job_dir / "ready").write_text("ready", encoding="utf-8")

        loop = asyncio.get_running_loop()
        deadline = loop.time() + PHARMCAT_TIMEOUT_SECONDS

        while loop.time() < deadline:
            status_file = job_dir / "status"

            if status_file.exists():
                status = status_file.read_text(
                    encoding="utf-8"
                ).strip()

                if status != "success":
                    error_file = job_dir / "stderr.log"
                    error_text = (
                        error_file.read_text(
                            encoding="utf-8",
                            errors="replace",
                        )
                        if error_file.exists()
                        else "No error log was generated."
                    )

                    raise RuntimeError(
                        f"PharmCAT failed: {error_text[-3000:]}"
                    )

                reports = list(output_dir.glob("*.report.json"))

                if not reports:
                    raise RuntimeError(
                        "PharmCAT finished but produced no report JSON."
                    )

                try:
                    return json.loads(
                        reports[0].read_text(encoding="utf-8")
                    )
                except json.JSONDecodeError as exc:
                    raise RuntimeError(
                        "PharmCAT produced invalid JSON."
                    ) from exc

            await asyncio.sleep(1)

        raise TimeoutError(
            "PharmCAT did not finish within "
            f"{PHARMCAT_TIMEOUT_SECONDS} seconds."
        )

    finally:
        # Do not delete a job while the worker may still be using it.
        if not (job_dir / "processing").exists():
            shutil.rmtree(job_dir, ignore_errors=True)