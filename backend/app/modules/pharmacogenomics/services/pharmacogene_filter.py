import json
from pathlib import Path
from typing import Any, Dict, List, Set

from app.modules.pharmacogenomics.config import pgx_settings


def load_known_pharmacogenes() -> Set[str]:
    """
    Load the set of established pharmacogenes supported by GeneGuard PGx.
    """
    allele_file = pgx_settings.DATA_DIR / "allele_definitions.json"
    pairs_file = pgx_settings.DATA_DIR / "gene_drug_pairs.json"
    
    genes: Set[str] = set()
    
    if allele_file.exists():
        with open(allele_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            genes.update(data.keys())
            
    if pairs_file.exists():
        with open(pairs_file, "r", encoding="utf-8") as f:
            pairs = json.load(f)
            for item in pairs:
                if item.get("primary_gene"):
                    genes.add(item["primary_gene"].upper())
                for sec in item.get("secondary_genes", []):
                    genes.add(sec.upper())
                    
    return genes


KNOWN_PHARMACOGENES = load_known_pharmacogenes()


def filter_pharmacogene_variants(variant_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Stage 2: Filter input variants to isolate pharmacogenes.
    Accepts raw variant records from WES Analysis / Module 1 or normalized dictionaries.
    """
    filtered = []
    
    for rec in variant_records:
        gene = None
        
        # Handle dict formats from WES module or VariantInput
        if isinstance(rec, dict):
            gene = (
                rec.get("gene") or 
                rec.get("gene_symbol") or 
                rec.get("variant", {}).get("gene") or
                rec.get("variant", {}).get("gene_symbol")
            )
        elif hasattr(rec, "gene"):
            gene = getattr(rec, "gene")
            
        if not gene:
            continue
            
        gene_upper = str(gene).strip().upper()
        
        if gene_upper in KNOWN_PHARMACOGENES:
            # Normalize record
            norm_rec = {
                "gene": gene_upper,
                "hgvs_c": (rec.get("hgvs_c") or rec.get("c_dot") or rec.get("variant", {}).get("hgvs_c") or ""),
                "hgvs_p": (rec.get("hgvs_p") or rec.get("p_dot") or rec.get("variant", {}).get("hgvs_p") or ""),
                "rsid": (rec.get("rsid") or rec.get("rs_id") or rec.get("variant", {}).get("rsid") or ""),
                "zygosity": (rec.get("zygosity") or rec.get("genotype") or "heterozygous").lower(),
                "star_allele": (rec.get("star_allele") or rec.get("allele") or None)
            }
            filtered.append(norm_rec)
            
    return filtered
