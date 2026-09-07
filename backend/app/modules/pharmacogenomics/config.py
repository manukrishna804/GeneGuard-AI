import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load .env file if available
load_dotenv()


class PGxSettings:
    MODULE_NAME: str = os.getenv("PGX_MODULE_NAME", "GeneGuard Pharmacogenomics CDS")
    VERSION: str = os.getenv("PGX_VERSION", "1.0.0")
    
    # API endpoints
    CPIC_API_BASE_URL: str = os.getenv("CPIC_API_BASE_URL", "https://api.cpicpgx.org/v1")
    PHARMGKB_API_BASE_URL: str = os.getenv("PHARMGKB_API_BASE_URL", "https://api.pharmgkb.org/v1")
    
    # Request timeouts
    EXTERNAL_API_TIMEOUT_SECONDS: float = float(os.getenv("EXTERNAL_API_TIMEOUT_SECONDS", "8.0"))
    
    # LLM Settings (optional AI explanation layer)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    DEFAULT_LLM_MODEL: str = os.getenv("DEFAULT_LLM_MODEL", "llama-3.3-70b-versatile")
    
    # Data directory
    DATA_DIR: Path = Path(__file__).resolve().parent / "data"


pgx_settings = PGxSettings()
