import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.modules.pharmacogenomics.config import pgx_settings


def load_allele_definitions() -> Dict[str, Any]:
    """
    Load PharmVar star-allele definitions from local storage.
    """
    allele_file = pgx_settings.DATA_DIR / "allele_definitions.json"
    if allele_file.exists():
        with open(allele_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


ALLELE_DEFINITIONS = load_allele_definitions()


def match_variant_to_star_allele(gene: str, variant: Dict[str, Any]) -> Optional[str]:
    """
    Match an observed variant (rsID, HGVS, explicit star allele) to a known PharmVar star allele.
    """
    gene_def = ALLELE_DEFINITIONS.get(gene)
    if not gene_def:
        return None

    # Explicit star allele provided
    if variant.get("star_allele"):
        allele_name = variant["star_allele"].strip()
        if not allele_name.startswith("*") and not allele_name.startswith("HLA"):
            allele_name = f"*{allele_name}"
        if allele_name in gene_def.get("alleles", {}):
            return allele_name

    rsid = (variant.get("rsid") or "").strip().lower()
    hgvs_c = (variant.get("hgvs_c") or "").strip().lower()
    hgvs_p = (variant.get("hgvs_p") or "").strip().lower()

    for allele_key, allele_data in gene_def.get("alleles", {}).items():
        var_list = [v.lower() for v in allele_data.get("variants", [])]
        
        if rsid and any(rsid == v for v in var_list):
            return allele_key
        if hgvs_c and any(hgvs_c in v or v in hgvs_c for v in var_list):
            return allele_key
        if hgvs_p and any(hgvs_p in v or v in hgvs_p for v in var_list):
            return allele_key

    return None


def call_diplotype_for_gene(gene: str, variants: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Determine diplotype for a specific pharmacogene given its observed variants.
    """
    gene_def = ALLELE_DEFINITIONS.get(gene, {})
    ref_allele = gene_def.get("reference_allele", "*1")
    
    # Specific handling for HLA genes
    if gene.startswith("HLA"):
        risk_alleles = []
        for v in variants:
            matched = match_variant_to_star_allele(gene, v)
            if matched:
                risk_alleles.append(matched)
                
        if risk_alleles:
            return {
                "gene": gene,
                "diplotype": f"{risk_alleles[0]} (Positive)",
                "allele1": risk_alleles[0],
                "allele2": "Negative",
                "evidence_alleles": risk_alleles,
                "is_risk_positive": True
            }
        else:
            return {
                "gene": gene,
                "diplotype": "Negative / Low Risk",
                "allele1": "Negative",
                "allele2": "Negative",
                "evidence_alleles": [],
                "is_risk_positive": False
            }

    # Specific handling for VKORC1 (-1639G>A)
    if gene == "VKORC1":
        has_a = False
        is_homozygous = False
        for v in variants:
            matched = match_variant_to_star_allele(gene, v)
            if matched == "A" or "rs9923231" in (v.get("rsid") or "") or "1639" in (v.get("hgvs_c") or ""):
                has_a = True
                zyg = str(v.get("zygosity", "")).lower()
                if "homo" in zyg:
                    is_homozygous = True
        
        if is_homozygous:
            return {
                "gene": gene,
                "diplotype": "-1639A/A",
                "allele1": "A",
                "allele2": "A",
                "evidence_alleles": ["A", "A"]
            }
        elif has_a:
            return {
                "gene": gene,
                "diplotype": "-1639G/A",
                "allele1": "G",
                "allele2": "A",
                "evidence_alleles": ["A"]
            }
        else:
            return {
                "gene": gene,
                "diplotype": "-1639G/G",
                "allele1": "G",
                "allele2": "G",
                "evidence_alleles": []
            }

    # General star-allele diplotype caller (CYPs, DPYD, TPMT, NUDT15, SLCO1B1, UGT1A1, G6PD)
    identified_alleles: List[str] = []
    
    for v in variants:
        matched = match_variant_to_star_allele(gene, v)
        if matched:
            zyg = str(v.get("zygosity", "")).lower()
            if "homo" in zyg:
                identified_alleles.extend([matched, matched])
            else:
                identified_alleles.append(matched)

    if not identified_alleles:
        # Wild-type reference diplotype
        diplotype_str = f"{ref_allele}/{ref_allele}"
        return {
            "gene": gene,
            "diplotype": diplotype_str,
            "allele1": ref_allele,
            "allele2": ref_allele,
            "evidence_alleles": []
        }
    elif len(identified_alleles) == 1:
        # Heterozygous single variant: *1 / *variant
        diplotype_str = f"{ref_allele}/{identified_alleles[0]}"
        return {
            "gene": gene,
            "diplotype": diplotype_str,
            "allele1": ref_allele,
            "allele2": identified_alleles[0],
            "evidence_alleles": [identified_alleles[0]]
        }
    else:
        # Two or more variants called (e.g. *2/*2 or *2/*3)
        a1 = identified_alleles[0]
        a2 = identified_alleles[1]
        diplotype_str = f"{a1}/{a2}"
        return {
            "gene": gene,
            "diplotype": diplotype_str,
            "allele1": a1,
            "allele2": a2,
            "evidence_alleles": identified_alleles
        }


def call_all_diplotypes(filtered_variants: List[Dict[str, Any]], target_genes: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
    """
    Stage 3: Call diplotypes for all relevant pharmacogenes.
    If target_genes is provided, ensures diplotypes are called for every target gene (defaulting to *1/*1 if no variants).
    """
    # Group variants by gene
    gene_to_variants: Dict[str, List[Dict[str, Any]]] = {}
    for v in filtered_variants:
        g = v.get("gene", "").upper()
        if g:
            gene_to_variants.setdefault(g, []).append(v)

    genes_to_process = set(target_genes) if target_genes else set(gene_to_variants.keys()).union(ALLELE_DEFINITIONS.keys())
    
    results = {}
    for gene in genes_to_process:
        vars_for_gene = gene_to_variants.get(gene, [])
        results[gene] = call_diplotype_for_gene(gene, vars_for_gene)
        
    return results
