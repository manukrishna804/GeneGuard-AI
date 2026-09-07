import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import httpx

from app.modules.pharmacogenomics.config import pgx_settings


def load_local_guideline_rules() -> List[Dict[str, Any]]:
    rules_file = pgx_settings.DATA_DIR / "guideline_rules.json"
    if rules_file.exists():
        with open(rules_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("guidelines", [])
    return []


def load_local_fda_biomarkers() -> List[Dict[str, Any]]:
    fda_file = pgx_settings.DATA_DIR / "fda_biomarkers.json"
    if fda_file.exists():
        with open(fda_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


LOCAL_GUIDELINES = load_local_guideline_rules()
LOCAL_FDA_BIOMARKERS = load_local_fda_biomarkers()


def find_local_cpic_guideline(drug: str, gene: str, phenotype: str) -> Optional[Dict[str, Any]]:
    """
    Find matching guideline rule from local curated CPIC dataset.
    """
    clean_drug = drug.strip().lower()
    clean_gene = gene.strip().upper()
    
    for g in LOCAL_GUIDELINES:
        if g["drug"].lower() == clean_drug and g["gene"].upper() == clean_gene:
            for pheno_pattern in g.get("phenotypes", []):
                if (pheno_pattern.lower() in phenotype.lower() or 
                    phenotype.lower() in pheno_pattern.lower()):
                    return g
                    
    for g in LOCAL_GUIDELINES:
        if g["drug"].lower() == clean_drug and g["gene"].upper() == clean_gene:
            return g
            
    return None


def find_local_fda_biomarker(drug: str, gene: str) -> Optional[Dict[str, Any]]:
    clean_drug = drug.strip().lower()
    clean_gene = gene.strip().upper()
    for item in LOCAL_FDA_BIOMARKERS:
        if item["drug"].lower() == clean_drug and clean_gene in item["gene"].upper():
            return item
    return None


async def fetch_cpic_live_guideline(
    client: httpx.AsyncClient,
    drug: str,
    gene: str,
    phenotype: str
) -> Dict[str, Any]:
    """
    Query the real CPIC PostgREST API (https://api.cpicpgx.org/v1/) live for:
    1. /drug (RxNorm ID, ClinPGx ID, DrugBank ID, Guideline ID)
    2. /pair (CPIC Level, ClinPGx Level, testing status)
    3. /recommendation (clinical recommendations, implications, classification)
    """
    try:
        # Step 1: Find drug in CPIC database
        drug_url = f"{pgx_settings.CPIC_API_BASE_URL}/drug"
        drug_resp = await client.get(
            drug_url,
            params={"name": f"ilike.*{drug.strip()}*"},
            timeout=pgx_settings.EXTERNAL_API_TIMEOUT_SECONDS
        )
        
        if drug_resp.status_code != 200 or not drug_resp.json():
            return {"status": "not_found", "message": f"Drug {drug} not found in CPIC API"}
            
        drug_data = drug_resp.json()[0]
        drug_id = drug_data.get("drugid")
        guideline_id = drug_data.get("guidelineid")
        drugbank_id = drug_data.get("drugbankid")
        clinpgx_id = drug_data.get("clinpgxid")
        
        # Step 2: Fetch gene-drug pair metadata (CPIC Level, ClinPGx Level)
        pair_data = {}
        if drug_id:
            pair_url = f"{pgx_settings.CPIC_API_BASE_URL}/pair"
            pair_resp = await client.get(
                pair_url,
                params={"genesymbol": f"eq.{gene}", "drugid": f"eq.{drug_id}"},
                timeout=pgx_settings.EXTERNAL_API_TIMEOUT_SECONDS
            )
            if pair_resp.status_code == 200 and pair_resp.json():
                pair_data = pair_resp.json()[0]

        # Step 3: Fetch CPIC recommendation matching guideline and phenotype
        recommendation_obj = None
        if drug_id and guideline_id:
            rec_url = f"{pgx_settings.CPIC_API_BASE_URL}/recommendation"
            rec_resp = await client.get(
                rec_url,
                params={"drugid": f"eq.{drug_id}", "guidelineid": f"eq.{guideline_id}"},
                timeout=pgx_settings.EXTERNAL_API_TIMEOUT_SECONDS
            )
            
            if rec_resp.status_code == 200 and rec_resp.json():
                recs = rec_resp.json()
                # Find matching phenotype recommendation
                for r in recs:
                    p_map = r.get("phenotypes", {})
                    gene_p = p_map.get(gene, "")
                    lk_map = r.get("lookupkey", {})
                    gene_lk = lk_map.get(gene, "")
                    
                    if (gene_p and (gene_p.lower() in phenotype.lower() or phenotype.lower() in gene_p.lower())) or \
                       (gene_lk and (gene_lk.lower() in phenotype.lower() or phenotype.lower() in gene_lk.lower())):
                        recommendation_obj = r
                        break
                        
                if not recommendation_obj and recs:
                    recommendation_obj = recs[0]

        return {
            "status": "success",
            "source": "CPIC_LIVE_REST_API",
            "drug_data": drug_data,
            "pair_data": pair_data,
            "recommendation_obj": recommendation_obj,
            "drugbank_id": drugbank_id,
            "clinpgx_id": clinpgx_id,
            "cpic_level": pair_data.get("cpiclevel", "A"),
            "clinpgx_level": pair_data.get("clinpgxlevel", "1A")
        }
    except Exception as exc:
        return {"status": "fallback", "error": str(exc)}


async def fetch_guidelines_for_pair(
    drug: str, 
    gene: str, 
    phenotype: str, 
    client: Optional[httpx.AsyncClient] = None
) -> Dict[str, Any]:
    """
    Stage 6: Query real CPIC PostgREST API live with seamless fallback to curated local datasets.
    """
    local_cpic = find_local_cpic_guideline(drug, gene, phenotype)
    local_fda = find_local_fda_biomarker(drug, gene)
    
    live_cpic_result = None
    if client:
        try:
            live_cpic_result = await fetch_cpic_live_guideline(client, drug, gene, phenotype)
        except Exception:
            pass

    # Extract recommendation text and implications from live CPIC API if available
    rec_text = None
    implication_text = None
    evidence_level = "CPIC Level A"
    pharmgkb_level = "1A"
    
    if live_cpic_result and live_cpic_result.get("status") == "success":
        rec_obj = live_cpic_result.get("recommendation_obj")
        if rec_obj:
            rec_text = rec_obj.get("drugrecommendation")
            implications = rec_obj.get("implications", {})
            if isinstance(implications, dict):
                implication_text = implications.get(gene)
        
        if live_cpic_result.get("cpic_level"):
            evidence_level = f"CPIC Level {live_cpic_result['cpic_level']}"
        if live_cpic_result.get("clinpgx_level"):
            pharmgkb_level = str(live_cpic_result["clinpgx_level"])

    # Fallback to local CPIC guideline if live field is empty
    if not rec_text and local_cpic:
        rec_text = local_cpic.get("recommendation")
    if not implication_text and local_cpic:
        implication_text = local_cpic.get("clinical_implication")
    if not rec_text:
        rec_text = "Standard dosing recommended with regular monitoring."
    if not implication_text:
        implication_text = "Standard therapeutic response expected."

    guideline_payload = {
        "drug": drug,
        "gene": gene,
        "phenotype": phenotype,
        "local_cpic": local_cpic,
        "local_fda": local_fda,
        "live_cpic_api": live_cpic_result,
        "evidence_level": (local_cpic.get("evidence_level") if local_cpic else evidence_level),
        "pharmgkb_level": (local_cpic.get("pharmgkb_level") if local_cpic else pharmgkb_level),
        "recommendation": rec_text,
        "clinical_implication": implication_text,
        "actionability": (local_cpic.get("actionability") if local_cpic else "Standard Dosing"),
        "source": (local_cpic.get("source") if local_cpic else "CPIC Clinical Practice Guidelines"),
        "specialist": (local_cpic.get("specialist") if local_cpic else "Clinical Pharmacist"),
        "requires_review": (local_cpic.get("requires_review") if local_cpic else False),
        "drugbank_id": (live_cpic_result.get("drugbank_id") if live_cpic_result else None),
        "clinpgx_id": (live_cpic_result.get("clinpgx_id") if live_cpic_result else None)
    }

    return guideline_payload
