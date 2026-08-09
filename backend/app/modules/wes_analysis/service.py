"""
WES Analysis service — Module 1 MVP pipeline.

Pipeline (all steps live in this file intentionally):

    1. extract_text_from_pdf()   — pdfplumber text extraction
    2. extract_variants()        — regex-based field extraction
    3. validate_variant()        — basic sanity checks
    4. query_ensembl()           — Ensembl REST API
    5. query_clinvar()           — NCBI E-utilities (ClinVar)
    6. build_evidence()          — assemble per-variant result
    7. analyze_wes_report()      — orchestrate the full pipeline

External sources used in this MVP:
    • Ensembl REST API   — https://rest.ensembl.org
    • NCBI E-utilities   — https://eutils.ncbi.nlm.nih.gov

Additional sources (gnomAD, HPO, OMIM, etc.) will be integrated in future sprints.
"""

import io
import os
import re
import logging
from typing import Any, Dict, List, Optional

import requests
import pdfplumber

from app.modules.wes_analysis.schema import (
    DatasourceResult,
    VariantInput,
    VariantResult,
    WESAnalysisResponse,
    EnsemblInfo,
    ClinVarInfo,
    ExtractionInfo,
    OMIMInfo,
    GnomADInfo,
    HPOInfo,
    PubMedArticle,
    OMIMPhenotype,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ENSEMBL_BASE_URL = "https://rest.ensembl.org"
NCBI_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

# Optional NCBI API key — raises request rate limit from 3 to 10 req/s.
# Set NCBI_API_KEY in your environment to use it.
NCBI_API_KEY: Optional[str] = os.getenv("NCBI_API_KEY")

REQUEST_TIMEOUT = 15  # seconds — applies to all external API calls


# ---------------------------------------------------------------------------
# Step 1 — PDF text extraction
# ---------------------------------------------------------------------------

def extract_text_from_pdf(file_bytes: bytes) -> tuple:
    """
    Extract raw text from a PDF using a multi-layer strategy:
      1. pdfplumber text extraction
      2. PyMuPDF (fitz) text extraction fallback
      3. OCR image rendering fallback for scanned/image PDFs

    Args:
        file_bytes: Raw PDF file content.

    Returns:
        (full_text: str, is_ocr: bool)

    Raises:
        ValueError: If the file is not a valid PDF or no text can be extracted.
    """
    if not file_bytes:
        raise ValueError("PDF file is empty.")

    # Basic PDF magic-byte check
    if not file_bytes[:4] == b"%PDF":
        raise ValueError("Uploaded file does not appear to be a valid PDF.")

    text_parts: List[str] = []
    is_ocr = False

    # Strategy 1: pdfplumber text extraction
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            if not pdf.pages:
                raise ValueError("PDF has no pages.")

            for page_number, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
                else:
                    logger.debug("Page %d: no text extracted via pdfplumber.", page_number)

    except pdfplumber.pdfminer.pdfpage.PDFTextExtractionNotAllowed:
        raise ValueError("PDF has text extraction disabled (encrypted/protected).")
    except Exception as exc:
        logger.debug("pdfplumber extraction failed: %s", exc)

    full_text = "\n".join(text_parts).strip()

    # Strategy 2: PyMuPDF (fitz) text fallback if pdfplumber extracted < 50 chars
    if len(full_text) < 50:
        try:
            import fitz
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            fitz_parts = [page.get_text() for page in doc if page.get_text()]
            fitz_text = "\n".join(fitz_parts).strip()
            if len(fitz_text) > len(full_text):
                full_text = fitz_text
        except Exception as exc:
            logger.debug("PyMuPDF text extraction failed: %s", exc)

    # Strategy 3: OCR fallback if text is still empty/minimal (<50 chars)
    if len(full_text) < 50:
        try:
            import fitz
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            ocr_parts = []
            for page in doc:
                pix = page.get_pixmap(dpi=150)
                try:
                    import pytesseract
                    from PIL import Image
                    img = Image.open(io.BytesIO(pix.tobytes("png")))
                    txt = pytesseract.image_to_string(img)
                    if txt:
                        ocr_parts.append(txt)
                except ImportError:
                    pass
            if ocr_parts:
                full_text = "\n".join(ocr_parts).strip()
                is_ocr = True
        except Exception as exc:
            logger.debug("OCR extraction failed: %s", exc)

    if not full_text:
        raise ValueError(
            "No text could be extracted from this PDF. "
            "It may be a scanned/image-based or protected report."
        )

    return full_text, is_ocr


# ---------------------------------------------------------------------------
# Step 2 — Variant extraction & helpers
# ---------------------------------------------------------------------------

def _clean_cdna(val: Optional[str]) -> Optional[str]:
    if not val:
        return None
    val = val.strip().replace(" ", "")
    # Check if it matches DNA change pattern but lacks 'c.' prefix
    if not val.startswith("c.") and re.match(r"^\d+|^(?=[ATCG])", val, re.IGNORECASE):
        if re.match(r"^\d+", val):
            val = "c." + val
    return val

def _clean_protein(val: Optional[str]) -> Optional[str]:
    if not val:
        return None
    val = val.strip().replace(" ", "")
    # Check if it matches protein change pattern but lacks 'p.' prefix
    if not val.startswith("p.") and re.match(r"^[A-Z][a-z]{2}\d+|^\d+", val):
        val = "p." + val
    return val

# Regex patterns for common WES report fields.
# These patterns intentionally err on the side of breadth — a short false-positive
# is much less harmful here than missing a real variant. Clinical NLP will be
# improved iteratively.

_PATTERNS = {
    # Gene symbol: e.g. "SHANK3" in "SHANK3 gene", "PAH" in "Gene: PAH", or "SHANK3" in "SHANK3 (NM_..."
    "gene": re.compile(
        r"\b([A-Z][A-Z0-9\-]{1,9})\b(?=\s+[gG][eE][nN][eE]\b)|"
        r"(?:[gG][eE][nN][eE](?:\s*[nN][aA][mM][eE])?(?:\(s\))?)\s*[:\-]?\s*\b([A-Z][A-Z0-9\-]{1,9})\b|"
        r"\b([A-Z][A-Z0-9\-]{1,9})\b(?=\s+\((?:[nN][mM]|[nN][rR]|[nN][pP]|[eE][nN][sS][tT]))"
    ),

    # Transcript accession: e.g. NM_033517.1, ENST00000333994 (with or without prefix)
    "transcript": re.compile(
        r"\b((?:NM|NR|NP|ENST)_\d+(?:\.\d+)?)\b",
        re.IGNORECASE,
    ),

    # HGVS cDNA notation: e.g. c.722G>A, c.SAMPLE
    "cdna": re.compile(
        r"\b(c\.[A-Za-z0-9_>\+\-\*]+)\b"
    ),

    # HGVS protein notation: e.g. p.Arg241His, p.SAMPLE
    "protein": re.compile(
        r"\b(p\.[A-Za-z0-9_>\+\-\*]+)\b"
    ),

    # dbSNP rsID
    "rsid": re.compile(r"\b(rs\d+)\b", re.IGNORECASE),

    # Zygosity: e.g. Heterozygous, Hom, Het, etc.
    "zygosity": re.compile(
        r"\b(Heterozygous|Homozygous|Hemizygous|HET|HOM|HEMIZYGOUS)\b",
        re.IGNORECASE,
    ),

    # Variant classification: e.g. Pathogenic, Likely Pathogenic, VUS, PV, LP, B, LB
    "classification": re.compile(
        r"\b(Pathogenic|Likely\s+Pathogenic|VUS|Variant\s+of\s+Uncertain\s+Significance|Benign|Likely\s+Benign|Pathogenic\s+Variant|PV|LP)\b",
        re.IGNORECASE,
    ),

    # Variant Type: e.g. SNV, Indel, Deletion, Duplication
    "variant_type": re.compile(
        r"\b(SNV|Indel|Deletion|Insertion|Duplication|Substitution|CNV|SV)\b",
        re.IGNORECASE,
    ),
}

# Common all-uppercase words that appear in WES reports but are NOT gene symbols.
# This blocklist prevents them from being mistakenly matched by the gene pattern.
_NON_GENE_WORDS: set = {
    # Molecular biology abbreviations
    "DNA", "RNA", "MRNA", "CDNA", "RRNA", "TRNA", "SNRNA", "PCR", "NGS", "WES", "WGS",
    # Variant classification terms
    "VUS", "SNV", "CNV", "SV", "INDEL", "LOH", "ROH",
    # HGVS notation abbreviations
    "DEL", "DUP", "INS", "INV", "FS", "EXT", "TER",
    # Report / clinical abbreviations
    "ACMG", "HGVS", "MLPA", "FISH", "CMA", "ISCN", "NMD",
    # Common English words that happen to be uppercase in headings
    "NA", "NOS", "NEC", "OR", "AND", "NOT", "DE", "ID", "NO",
    # Inheritance patterns
    "AD", "AR", "XL", "XLD", "XLR", "MT",
    # Zygosity tokens (handled separately)
    "HET", "HOM",
}

# Normalise raw zygosity strings to short uppercase tokens
_ZYGOSITY_MAP = {
    "heterozygous": "HET",
    "het": "HET",
    "homozygous": "HOM",
    "hom": "HOM",
    "hemizygous": "HEMIZYGOUS",
}

# Normalise raw classification strings to short standard codes
_CLASSIFICATION_MAP = {
    "pathogenic": "PV",
    "pathogenic variant": "PV",
    "pv": "PV",
    "likely pathogenic": "LP",
    "lp": "LP",
    "variant of uncertain significance": "VUS",
    "vus": "VUS",
    "benign": "B",
    "b": "B",
    "likely benign": "LB",
    "lb": "LB"
}


# ---------------------------------------------------------------------------
# Gene / ClinVar helper patterns (module-level, compiled once)
# ---------------------------------------------------------------------------

def _normalise_zygosity(raw: Optional[str]) -> Optional[str]:
    if raw is None:
        return None
    return _ZYGOSITY_MAP.get(raw.lower().strip(), raw.upper().strip())


def extract_structured_hgvs(text: str) -> List[Dict[str, Optional[str]]]:
    """
    Extract structured HGVS variants directly from report text expressions like:
      - GNAO1, NM_020988.3:c.118G>T (p.Gly40Trp)
      - NM_020988.3(GNAO1):c.118G>T (p.Gly40Trp)
      - GNAO1 c.118G>T p.Gly40Trp Het PV
    """
    variants = []
    
    # Compound pattern 1: Gene, Transcript:cDNA (protein)
    p1 = re.compile(
        r"\b(?P<gene>[A-Z][A-Z0-9\-]{1,9})[,\s:]+"
        r"(?P<transcript>(?:NM|NR|NP|ENST)_\d+(?:\.\d+)?):?"
        r"(?P<cdna>c\.[A-Za-z0-9_>\+\-\*]+)"
        r"(?:\s*\((?P<protein>p\.[A-Za-z0-9_>\+\-\*]+)\))?",
        re.IGNORECASE
    )

    # Compound pattern 2: Transcript(Gene):cDNA (protein)
    p2 = re.compile(
        r"\b(?P<transcript>(?:NM|NR|NP|ENST)_\d+(?:\.\d+)?)\("
        r"(?P<gene>[A-Z][A-Z0-9\-]{1,9})\):?"
        r"(?P<cdna>c\.[A-Za-z0-9_>\+\-\*]+)"
        r"(?:\s*\((?P<protein>p\.[A-Za-z0-9_>\+\-\*]+)\))?",
        re.IGNORECASE
    )

    # Compound pattern 3: Gene cDNA protein (e.g. table lines: GNAO1 c.118G>T p.Gly40Trp Het PV)
    p3 = re.compile(
        r"\b(?P<gene>[A-Z][A-Z0-9\-]{1,9})\s+"
        r"(?P<cdna>c\.[A-Za-z0-9_>\+\-\*]+)"
        r"(?:\s+(?P<protein>p\.[A-Za-z0-9_>\+\-\*]+))?",
        re.IGNORECASE
    )

    matches = []
    for p in [p1, p2, p3]:
        for m in p.finditer(text):
            d = m.groupdict()
            gene = d.get("gene")
            cdna = d.get("cdna")
            if gene and gene.upper() in _NON_GENE_WORDS:
                continue
            if cdna and cdna.startswith("c."):
                matches.append((m.start(), d))

    if not matches:
        return []

    cv_match = _CLINVAR_VAR_ID_RE.search(text)
    clinvar_var_id = cv_match.group(1) if cv_match else None

    for start_pos, d in matches:
        window = text[max(0, start_pos - 100):min(len(text), start_pos + 300)]
        
        zyg_m = re.search(r"\b(Heterozygous|Homozygous|Hemizygous|HET|HOM)\b", window, re.IGNORECASE)
        class_m = re.search(r"\b(Pathogenic\s+Variant|Pathogenic|Likely\s+Pathogenic|VUS|Benign|Likely\s+Benign|PV|LP)\b", window, re.IGNORECASE)
        tr_m = re.search(r"\b((?:NM|NR|NP|ENST)_\d+(?:\.\d+)?)\b", text[max(0, start_pos - 300):min(len(text), start_pos + 300)], re.IGNORECASE)

        raw_zyg = zyg_m.group(1) if zyg_m else None
        norm_zyg = _normalise_zygosity(raw_zyg) if raw_zyg else None

        raw_class = class_m.group(1) if class_m else None
        norm_class = _CLASSIFICATION_MAP.get(raw_class.lower(), raw_class) if raw_class else None

        v = {
            "gene": d.get("gene"),
            "transcript": d.get("transcript") or (tr_m.group(1) if tr_m else None),
            "cdna": _clean_cdna(d.get("cdna")),
            "protein": _clean_protein(d.get("protein")),
            "rsid": None,
            "zygosity": norm_zyg,
            "classification": norm_class,
            "variant_type": None,
            "clinvar_variation_id": clinvar_var_id,
        }
        variants.append(v)

    # Deduplicate
    seen = set()
    unique = []
    for v in variants:
        key = (v.get("gene"), v.get("transcript"), v.get("cdna"))
        if key not in seen:
            seen.add(key)
            unique.append(v)
    return unique


# Matches gene symbol in parentheses AFTER a transcript accession:
#   e.g. "Reference sequence: NM_020988.3(GNAO1)"
_GENE_FROM_TRANSCRIPT_RE = re.compile(
    r"(?:NM|NR|NP|ENST)_\d+(?:\.\d+)?\(([A-Z][A-Z0-9\-]{1,9})\)"
)

# Matches ClinVar Variation ID in text:
#   e.g. "ClinVar Variation ID: 280526" or "ClinVar Variation ID - 280526"
_CLINVAR_VAR_ID_RE = re.compile(
    r"(?i)clinvar\s+variation\s+id\s*[:\-]?\s*(\d+)"
)

# A valid gene symbol is a single uppercase token 2-10 chars, no spaces.
_GENE_SYMBOL_RE = re.compile(r"^[A-Z][A-Z0-9\-]{1,9}$")


def _normalise_zygosity(raw: Optional[str]) -> Optional[str]:
    if raw is None:
        return None
    return _ZYGOSITY_MAP.get(raw.lower().strip(), raw.upper().strip())


def _resolve_gene_from_transcript(transcript_id: Optional[str]) -> Optional[str]:
    """Return the gene symbol for a given Ensembl transcript ID.
    Uses the Ensembl REST lookup endpoint. If the request fails or the
    transcript does not map to a gene, returns None.
    """
    if not transcript_id:
        return None
    try:
        import httpx
        url = f"https://rest.ensembl.org/lookup/id/{transcript_id}?content-type=application/json"
        resp = httpx.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("display_name")
    except Exception as e:
        logger.debug(f"Failed to resolve gene from transcript {transcript_id}: {e}")
    return None


def _extract_gene_from_text(text: str) -> Optional[str]:
    """
    Extract a valid gene symbol from free text using two strategies:

    1. Transcript-parenthesis format: NM_020988.3(GNAO1)
       Common in "Reference sequence:" lines of WES reports.
    2. Existing gene regex patterns, with non-gene blocklist applied.

    Returns the first valid candidate, or None.
    """
    # Strategy 1: TRANSCRIPT(GENE) notation — gene in parens after accession
    for m in _GENE_FROM_TRANSCRIPT_RE.finditer(text):
        candidate = m.group(1)
        if candidate.upper() not in _NON_GENE_WORDS and len(candidate) >= 2:
            return candidate

    # Strategy 2: existing regex patterns with blocklist filtering
    for m in _PATTERNS["gene"].finditer(text):
        val = next((g for g in m.groups() if g is not None), None)
        if val and val.upper() not in _NON_GENE_WORDS and len(val) >= 2:
            return val

    return None


def extract_variants_from_table(pdf_bytes: bytes) -> List[Dict[str, Optional[str]]]:
    """Extract variant rows from the first table that looks like a variant table.

    The function scans each page for tables via pdfplumber, looks for a header row
    containing a superset of required fields (gene, transcript, cdna, protein,
    rsid, zygosity). If a matching table is found, each data row is mapped to a
    variant dict using the header mapping. Returns an empty list if no such table
    is present.
    """
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                page_text = page.extract_text() or ""
                # Find all transcript accessions on this page as a fallback for the table
                transcript_matches = re.findall(r"\b((?:NM|NR|NP|ENST)_\d+(?:\.\d+)?)\b", page_text, re.IGNORECASE)
                default_transcript = transcript_matches[0] if transcript_matches else None

                for table in tables:
                    if not table or len(table) < 2:
                        continue
                    # Find the row that looks like a header (requires multiple key columns)
                    header_row_idx = None
                    for i, row in enumerate(table):
                        if not any(row):
                            continue
                        # Collect lowercased cell texts
                        cell_texts = [str(cell).lower() for cell in row if cell]
                        # Count how many required keywords appear in the row
                        keyword_hits = sum(
                            any(key in cell for key in ["gene", "transcript", "cdna", "c.", "protein", "p.", "zygosity", "dna change", "aa change", "class", "inherit"])
                            for cell in cell_texts
                        )
                        # Consider it a header if at least two required columns are present
                        if keyword_hits >= 2:
                            header_row_idx = i
                            break
                    if header_row_idx is None:
                        continue
                    header = [h.strip().lower().replace("\n", " ").replace("\r", " ") for h in table[header_row_idx] if h]
                    # Determine if this table likely contains variant data.
                    has_gene = any('gene' in col for col in header)
                    has_other = any(key in col for col in header for key in ['cdna', 'c.', 'protein', 'p.', 'zygosity', 'change', 'class'])
                    if not (has_gene and has_other):
                        continue
                    # Build column index map based on the identified header row
                    col_map = {}
                    for idx, col in enumerate(header):
                        # Handle combined "Gene (Transcript)" header and case‑insensitive matching
                        col_low = col.lower()
                        if "gene (transcript)" in col_low:
                             col_map["gene"] = idx
                             col_map["transcript"] = idx
                        elif "gene" in col_low:
                             col_map["gene"] = idx
                        elif "transcript" in col_low or "nm_" in col_low:
                             col_map["transcript"] = idx
                        elif "cdna" in col_low or "c." in col_low or "dna change" in col_low:
                             col_map["cdna"] = idx
                        elif "protein" in col_low or "p." in col_low or "aa change" in col_low or "predicted aa" in col_low:
                             col_map["protein"] = idx
                        elif "rsid" in col_low or re.search(r"rs\d+", col_low):
                             col_map["rsid"] = idx
                        elif "zygosity" in col_low:
                             col_map["zygosity"] = idx
                        elif "class" in col_low:
                             col_map["classification"] = idx
                        elif "type" in col_low:
                             col_map["variant_type"] = idx

                    # Extract rows after the header row
                    variants: List[Dict[str, Optional[str]]] = []
                    for row in table[header_row_idx + 1 :]:
                        if len(row) < len(header):
                            continue
                        variant: Dict[str, Optional[str]] = {
                            "gene": None,
                            "transcript": default_transcript,
                            "cdna": None,
                            "protein": None,
                            "rsid": None,
                            "zygosity": None,
                            "classification": None,
                            "variant_type": None,
                        }
                        for field, idx in col_map.items():
                            cell = row[idx] if idx < len(row) else None
                            val = cell.strip() if isinstance(cell, str) else None
                            if field == "zygosity" and val:
                                val = _normalise_zygosity(val)
                            # Handle combined "Gene (Transcript)" cell, e.g., "GNAO1 (NM_020988.3)"
                            if field == "gene" and val and "(" in val and ")" in val:
                                # Split at the first '(' to separate gene name and transcript(s)
                                gene_part, rest = val.split('(', 1)
                                variant["gene"] = gene_part.strip() or None
                                transcript_part = rest.split(')', 1)[0].strip()
                                variant["transcript"] = transcript_part or None
                                continue
                            if field == "transcript" and val:
                                variant["transcript"] = val
                                continue
                            if field == "cdna" and val:
                                variant["cdna"] = _clean_cdna(val)
                                continue
                            if field == "protein" and val:
                                variant["protein"] = _clean_protein(val)
                                continue
                            if field == "rsid" and val:
                                variant["rsid"] = val
                                continue
                            if field == "gene" and val:
                                # Gene symbols are single uppercase tokens; take first word and validate.
                                # Multi-word values like "DNA change" are column headers, not gene names.
                                first_word = re.split(r'\s+', val.strip())[0] if val.strip() else None
                                if (
                                    first_word
                                    and _GENE_SYMBOL_RE.match(first_word)
                                    and first_word.upper() not in _NON_GENE_WORDS
                                ):
                                    variant["gene"] = first_word
                                # else: gene stays None; resolved from page text below
                                continue
                            if field in ["classification", "variant_type"] and val:
                                variant[field] = val
                                continue
                        # Residual safety: block any non-gene words or multi-word values
                        if variant["gene"] and (
                            variant["gene"].upper() in _NON_GENE_WORDS
                            or not _GENE_SYMBOL_RE.match(variant["gene"])
                        ):
                            variant["gene"] = None
                        # If gene is still None, extract from full page text
                        # (catches e.g. "Reference sequence: NM_020988.3(GNAO1)")
                        if not variant["gene"]:
                            variant["gene"] = _extract_gene_from_text(page_text)
                        # Extract ClinVar Variation ID from page text if present
                        cv_match = _CLINVAR_VAR_ID_RE.search(page_text)
                        variant["clinvar_variation_id"] = cv_match.group(1) if cv_match else None
                        variants.append(variant)
                    return variants
    except Exception as exc:
        logger.debug(f"Table extraction failed: {exc}")
    return []


def extract_variants(text: str) -> List[Dict[str, Optional[str]]]:
    """Legacy regex‑based variant extraction (fallback)."""
    # Collect all matches for each field type with their char offset
    hits: Dict[str, List[tuple]] = {k: [] for k in _PATTERNS}
    for field, pattern in _PATTERNS.items():
        for match in pattern.finditer(text):
            val = next((g for g in match.groups() if g is not None), match.group(0))
            hits[field].append((match.start(), val))

    # Filter out known non-gene words from the gene hit list
    hits["gene"] = [
        (pos, val) for (pos, val) in hits["gene"]
        if val.upper() not in _NON_GENE_WORDS and len(val) >= 2
    ]

    if not hits["cdna"] and not hits["gene"]:
        logger.info("No variant signals found in extracted text.")
        return []

    # If there are multiple cDNA entries, use them as anchors.
    # Otherwise fall back to a single "best-guess" variant.
    anchor_field = "cdna" if hits["cdna"] else "gene"
    anchors = hits[anchor_field]

    variants: List[Dict[str, Optional[str]]] = []

    for idx, (anchor_pos, anchor_val) in enumerate(anchors):
        window_start = anchors[idx - 1][0] if idx > 0 else 0
        window_end = anchors[idx + 1][0] if idx + 1 < len(anchors) else len(text)
        window = text[window_start:window_end]

        def _pick(field: str) -> Optional[str]:
            """Return the match closest to the current anchor_pos."""
            pattern = _PATTERNS[field]
            all_matches = list(pattern.finditer(text))
            if not all_matches:
                return None
            # For gene field, filter out known non-gene words BEFORE picking closest.
            # This prevents column headers like "DNA" (from "DNA change") from being returned.
            if field == "gene":
                all_matches = [
                    m for m in all_matches
                    if (
                        next((g for g in m.groups() if g is not None), m.group(0)) or ""
                    ).upper() not in _NON_GENE_WORDS
                ]
                if not all_matches:
                    return None
            best_match = min(all_matches, key=lambda m: abs(m.start() - anchor_pos))
            return next((g for g in best_match.groups() if g is not None), best_match.group(0))

        cdna_val = anchor_val if anchor_field == "cdna" else _pick("cdna")
        gene_val = anchor_val if anchor_field == "gene" else _pick("gene")

        # If gene still not found via patterns, try the transcript(gene) text extraction
        # This catches formats like: "Reference sequence: NM_020988.3(GNAO1)"
        if not gene_val:
            gene_val = _extract_gene_from_text(text)

        # Try to extract ClinVar Variation ID from the full text
        cv_match = _CLINVAR_VAR_ID_RE.search(text)

        variant = {
            "gene": gene_val,
            "transcript": _pick("transcript"),
            "cdna": _clean_cdna(cdna_val),
            "protein": _clean_protein(_pick("protein")),
            "rsid": _pick("rsid"),
            "zygosity": _normalise_zygosity(_pick("zygosity")),
            "classification": _pick("classification"),
            "variant_type": _pick("variant_type"),
            "clinvar_variation_id": cv_match.group(1) if cv_match else None,
        }
        variants.append(variant)

    # De-duplicate: same gene + transcript + cDNA = same variant
    seen: set = set()
    unique: List[Dict[str, Optional[str]]] = []
    for v in variants:
        key = (v.get("gene"), v.get("transcript"), v.get("cdna"))
        if key not in seen:
            seen.add(key)
            unique.append(v)

    logger.info("Extracted %d unique variant(s) from text.", len(unique))
    return unique


# ---------------------------------------------------------------------------
# Step 3 — Variant validation
# ---------------------------------------------------------------------------

def validate_variant(variant: Dict[str, Optional[str]]) -> Dict[str, Any]:
    """
    Basic sanity checks on a raw variant dict.

    Returns the same dict with two extra keys:
        is_valid           (bool)
        validation_message (str | None)
    """
    issues: List[str] = []

    gene = variant.get("gene")
    cdna = variant.get("cdna")
    transcript = variant.get("transcript")

    if not gene:
        issues.append("Gene symbol is missing.")

    if not cdna and not transcript:
        issues.append("Neither cDNA notation nor transcript accession found.")

    if cdna and not re.match(r"^c\.", cdna):
        issues.append(f"cDNA value '{cdna}' does not start with 'c.' — may be incorrectly extracted.")

    variant["is_valid"] = len(issues) == 0
    variant["validation_message"] = "; ".join(issues) if issues else None
    return variant


# ---------------------------------------------------------------------------
# Step 4 — Ensembl REST API
# ---------------------------------------------------------------------------

def query_ensembl(
    gene: Optional[str],
    cdna: Optional[str],
    protein: Optional[str],
    transcript: Optional[str],
    rsid: Optional[str],
) -> DatasourceResult:
    """
    Query the Ensembl REST API for variant information.

    Strategy:
        1. Prioritize variant-specific annotations using Variant Recoder in order:
           - transcript:cdna
           - transcript:protein
           - gene:cdna
           - gene:protein
           - rsid
        2. If Variant Recoder succeeds, use VEP (Variant Effect Predictor) to query details.
        3. If no variant-specific info is available, fallback to xref symbol lookup for gene.
        4. Return a DatasourceResult with status and raw data.

    Docs: https://rest.ensembl.org/documentation/info/variant_recoder
    """
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    # Attempt Variant Recoder using prioritized notations
    notations: List[str] = []
    if transcript and cdna:
        notations.append(f"{transcript}:{cdna}")
    if transcript and protein:
        notations.append(f"{transcript}:{protein}")
    if gene and cdna:
        notations.append(f"{gene}:{cdna}")
    if gene and protein:
        notations.append(f"{gene}:{protein}")
    if rsid:
        notations.append(rsid)

    recoder_data = None
    vep_data = None
    successful_notation = None

    for notation in notations:
        url = f"{ENSEMBL_BASE_URL}/variant_recoder/human/{requests.utils.quote(notation)}"
        try:
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                if data:
                    recoder_data = data
                    successful_notation = notation
                    break
        except Exception as e:
            logger.debug("Ensembl recoder failed for notation %s: %s", notation, e)

    # If recoder succeeded, attempt VEP query using the notation or genomic coords
    if recoder_data:
        # Extract transcript notation or rsID to call VEP
        vep_input = successful_notation
        try:
            first = recoder_data[0]
            inner = first
            if isinstance(first, dict) and len(first) == 1:
                inner = next(iter(first.values()))
            
            # Prefer hgvsc notation from recoder if possible for VEP
            hgvsc_list = inner.get("hgvsc", [])
            hgvsg_list = inner.get("hgvsg", [])
            ids_list = inner.get("id", [])
            
            if hgvsc_list:
                vep_input = hgvsc_list[0]
            elif hgvsg_list:
                vep_input = hgvsg_list[0]
            elif ids_list:
                vep_input = ids_list[0]
        except Exception:
            pass

        if vep_input:
            vep_url = f"{ENSEMBL_BASE_URL}/vep/human/hgvs/{requests.utils.quote(vep_input)}?content-type=application/json"
            if vep_input.lower().startswith("rs") or re.match(r"^\d+$", vep_input):
                vep_url = f"{ENSEMBL_BASE_URL}/vep/human/id/{requests.utils.quote(vep_input)}?content-type=application/json"
                
            try:
                vep_response = requests.get(vep_url, headers=headers, timeout=REQUEST_TIMEOUT)
                if vep_response.status_code == 200:
                    vep_json = vep_response.json()
                    if vep_json and isinstance(vep_json, list):
                        vep_data = vep_json[0]
            except Exception as e:
                logger.debug("Ensembl VEP query failed for input %s: %s", vep_input, e)

        return DatasourceResult(
            status="success",
            data={
                "recoder": recoder_data,
                "vep": vep_data
            }
        )

    # Strategy 2: Gene symbol fallback lookup ONLY if no variant-specific identifiers are present
    if gene and not (cdna or protein or rsid):
        url = f"{ENSEMBL_BASE_URL}/xrefs/symbol/homo_sapiens/{requests.utils.quote(gene)}"
        try:
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                if data:
                    return DatasourceResult(status="success", data={"gene_xrefs": data})
                return DatasourceResult(status="not_found", message=f"No Ensembl xrefs found for gene: {gene}")
            if response.status_code == 404:
                return DatasourceResult(status="not_found", message=f"Gene not found in Ensembl: {gene}")
            return DatasourceResult(status="error", message=f"Ensembl xref lookup HTTP {response.status_code}")
        except requests.exceptions.Timeout:
            return DatasourceResult(status="error", message="Ensembl API timed out.")
        except Exception as exc:
            return DatasourceResult(status="error", message=str(exc))

    return DatasourceResult(status="skipped", message="No matching variant or gene identifier resolved in Ensembl.")


def query_clinvar(
    gene: Optional[str],
    cdna: Optional[str],
    protein: Optional[str],
    rsid: Optional[str],
    transcript: Optional[str] = None,
    variation_id: Optional[str] = None,
) -> DatasourceResult:
    """
    Query NCBI ClinVar via the official E-utilities API.

    Strategy (strongest identifier first — never query by cDNA alone):
        1. ClinVar Variation ID — direct, unambiguous esummary fetch
        2. rsID  — dbSNP identifier via esearch
        3. gene + transcript + cDNA — compound targeted search
        4. gene + cDNA / protein — gene-level compound search
        5. transcript + cDNA — transcript-level search (no gene available)
    """
    base_params: Dict[str, str] = {"db": "clinvar", "retmode": "json"}
    if NCBI_API_KEY:
        base_params["api_key"] = NCBI_API_KEY

    # --- Fast path: direct fetch by ClinVar Variation ID ---
    if variation_id:
        try:
            summary_params = {**base_params, "id": variation_id}
            summary_resp = requests.get(
                f"{NCBI_BASE_URL}/esummary.fcgi",
                params=summary_params,
                timeout=REQUEST_TIMEOUT,
            )
            summary_resp.raise_for_status()
            summary_data = summary_resp.json()
            result_set = summary_data.get("result", {})
            result_set.pop("uids", None)
            if result_set:
                return DatasourceResult(
                    status="success",
                    data={
                        "clinvar_ids": [variation_id],
                        "records": result_set,
                    },
                )
        except Exception as exc:
            logger.debug("ClinVar direct variation ID fetch failed for %s: %s", variation_id, exc)
        # Fall through to regular search if direct fetch failed

    # Build a targeted esearch term
    terms: List[str] = []
    if rsid:
        terms.append(f"{rsid}[Variant ID]")
    elif gene:
        sub_terms = []
        if transcript and cdna:
            sub_terms.append(f"({transcript}:{cdna}[All Fields])")
        if cdna:
            sub_terms.append(f"{cdna}[All Fields]")
        if protein:
            sub_terms.append(f"{protein}[All Fields]")
            # Also try without the 'p.' prefix
            if protein.startswith("p."):
                sub_terms.append(f"{protein[2:]}[All Fields]")
        if sub_terms:
            terms.append(f"({gene}[Gene] AND ({' OR '.join(sub_terms)}))")
    elif transcript and cdna:
        terms.append(f"({transcript}[All Fields] AND {cdna}[All Fields])")

    if not terms:
        return DatasourceResult(status="skipped", message="Insufficient variant-specific data to query ClinVar.")

    search_term = " OR ".join(terms)

    # --- Step A: esearch ---
    try:
        search_params = {
            **base_params,
            "term": search_term,
            "retmax": "5",
        }
        search_resp = requests.get(
            f"{NCBI_BASE_URL}/esearch.fcgi",
            params=search_params,
            timeout=REQUEST_TIMEOUT,
        )
        search_resp.raise_for_status()
        search_data = search_resp.json()

    except requests.exceptions.Timeout:
        return DatasourceResult(status="error", message="NCBI ClinVar esearch timed out.")
    except Exception as exc:
        logger.exception("Unexpected error during ClinVar esearch.")
        return DatasourceResult(status="error", message=str(exc))

    esearch_result = search_data.get("esearchresult", {})
    id_list: List[str] = esearch_result.get("idlist", [])

    if not id_list:
        return DatasourceResult(
            status="not_found",
            message=f"No ClinVar records found for search: {search_term}",
        )

    # --- Step B: esummary ---
    try:
        summary_params = {
            **base_params,
            "id": ",".join(id_list),
        }
        summary_resp = requests.get(
            f"{NCBI_BASE_URL}/esummary.fcgi",
            params=summary_params,
            timeout=REQUEST_TIMEOUT,
        )
        summary_resp.raise_for_status()
        summary_data = summary_resp.json()

    except requests.exceptions.Timeout:
        return DatasourceResult(
            status="partial",
            data={"clinvar_ids": id_list},
            message="ClinVar esummary timed out; returning UIDs only.",
        )
    except Exception as exc:
        return DatasourceResult(status="error", message=str(exc))

    result_set = summary_data.get("result", {})
    result_set.pop("uids", None)

    # Filter records to ensure gene matches if gene is known
    query_gene = gene.lower() if gene else None
    if query_gene:
        filtered = {}
        for uid, rec in result_set.items():
            genes_info = rec.get("genes", [])
            match = any(g.get("symbol", "").lower() == query_gene for g in genes_info)
            if match:
                filtered[uid] = rec
        result_set = filtered
        if not result_set:
            return DatasourceResult(status="not_found", message=f"ClinVar records found but none matched gene {gene}.")

    return DatasourceResult(
        status="success",
        data={
            "clinvar_ids": id_list,
            "records": result_set,
        },
    )


# ---------------------------------------------------------------------------
# Step 6 — PubMed helper & Assemble per-variant evidence
# ---------------------------------------------------------------------------

def fetch_pubmed_details(pmid_list: List[str]) -> List[PubMedArticle]:
    """
    Fetch article metadata (title, journal, year, authors) for a list of PubMed IDs
    via NCBI E-utilities esummary.
    """
    if not pmid_list:
        return []

    valid_pmids = [str(p).strip() for p in pmid_list if str(p).strip().isdigit()][:10]
    if not valid_pmids:
        return []

    url = f"{NCBI_BASE_URL}/esummary.fcgi"
    params: Dict[str, str] = {
        "db": "pubmed",
        "id": ",".join(valid_pmids),
        "retmode": "json",
    }
    if NCBI_API_KEY:
        params["api_key"] = NCBI_API_KEY

    articles: List[PubMedArticle] = []
    try:
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 200:
            data = resp.json()
            result_set = data.get("result", {})
            result_set.pop("uids", None)
            for pmid, item in result_set.items():
                if not isinstance(item, dict):
                    continue
                title = item.get("title", "").rstrip(".")
                journal = item.get("source")
                pubdate = item.get("pubdate", "")
                year = pubdate.split()[0] if pubdate else None

                authors_list = [a.get("name") for a in item.get("authors", []) if isinstance(a, dict) and a.get("name")]
                authors_str = (
                    ", ".join(authors_list[:3]) + (" et al." if len(authors_list) > 3 else "")
                    if authors_list else None
                )

                articles.append(
                    PubMedArticle(
                        pmid=pmid,
                        title=title or None,
                        journal=journal or None,
                        year=year or None,
                        authors=authors_str,
                    )
                )
    except Exception as exc:
        logger.debug("Failed to fetch PubMed article details: %s", exc)

    return articles


def build_evidence(
    raw_variant: Dict[str, Any],
    ensembl_result: DatasourceResult,
    clinvar_result: DatasourceResult,
) -> VariantResult:
    """Combine extracted variant fields with summarized datasource evidence.

    Returns a VariantResult including enriched genomic annotations like gnomAD,
    OMIM, HPO, and PubMed.
    """
    # Normalized HGVS (concatenation of transcript and cdna)
    normalized_hgvs = None
    if raw_variant.get("transcript") and raw_variant.get("cdna"):
        normalized_hgvs = f"{raw_variant['transcript']}:{raw_variant['cdna']}"

    # --- 1. Summarize Ensembl/VEP data ---
    ensembl_info = EnsemblInfo(
        status=ensembl_result.status,
        matched=ensembl_result.status == "success",
        variant_id=None,
        genomic_change=None,
        hgvs_g=None,
        consequence=None,
    )
    
    recoder = None
    vep_data = None
    if ensembl_result.status == "success" and ensembl_result.data:
        recoder = ensembl_result.data.get("recoder")
        vep_data = ensembl_result.data.get("vep")
        
        if isinstance(recoder, list) and recoder:
            first = recoder[0]
            inner = first
            if isinstance(first, dict) and len(first) == 1:
                inner = next(iter(first.values()))
            ids = inner.get("id")
            if isinstance(ids, list) and ids:
                ensembl_info.variant_id = ids[0]
            hgvsg = inner.get("hgvsg")
            if isinstance(hgvsg, list) and hgvsg:
                ensembl_info.genomic_change = hgvsg[0]
                ensembl_info.hgvs_g = hgvsg[0].replace("g.", "")

        if vep_data:
            ensembl_info.consequence = vep_data.get("most_severe_consequence")
            if not ensembl_info.variant_id:
                ensembl_info.variant_id = vep_data.get("id")

            # Enrich Ensembl positional and transcript details
            ensembl_info.chromosome = str(vep_data.get("seq_region_name")) if vep_data.get("seq_region_name") else None
            if vep_data.get("start") is not None:
                try:
                    ensembl_info.position = int(vep_data.get("start"))
                except (ValueError, TypeError):
                    pass

            allele_str = vep_data.get("allele_string", "")
            if "/" in allele_str:
                parts = allele_str.split("/")
                ensembl_info.ref_allele = parts[0]
                ensembl_info.alt_allele = parts[1] if len(parts) > 1 else None

            # Transcript consequence details
            tcs = vep_data.get("transcript_consequences", [])
            if tcs:
                best_tc = None
                raw_tr = (raw_variant.get("transcript") or "").split(".")[0]
                if raw_tr:
                    for tc in tcs:
                        if tc.get("transcript_id") and raw_tr in tc.get("transcript_id"):
                            best_tc = tc
                            break
                if not best_tc:
                    best_tc = tcs[0]

                ensembl_info.gene_id = best_tc.get("gene_id")
                ensembl_info.transcript_id = best_tc.get("transcript_id")
                ensembl_info.biotype = best_tc.get("biotype")
                ensembl_info.strand = best_tc.get("strand")
                ensembl_info.impact = best_tc.get("impact")
                ensembl_info.amino_acids = best_tc.get("amino_acids")
                ensembl_info.codons = best_tc.get("codons")
                ensembl_info.hgvsc = best_tc.get("hgvsc")
                ensembl_info.hgvsp = best_tc.get("hgvsp")

    # Additional variant identifiers from recoder / colocated variants
    add_ids = set()
    if isinstance(recoder, list) and recoder:
        first = recoder[0]
        inner = first
        if isinstance(first, dict) and len(first) == 1:
            inner = next(iter(first.values()))
        for item_id in inner.get("id", []):
            if item_id != ensembl_info.variant_id:
                add_ids.add(str(item_id))
        if not ensembl_info.hgvsc and inner.get("hgvsc"):
            ensembl_info.hgvsc = inner.get("hgvsc")[0]
        if not ensembl_info.hgvsp and inner.get("hgvsp"):
            ensembl_info.hgvsp = inner.get("hgvsp")[0]

    if vep_data:
        for colocated in vep_data.get("colocated_variants", []):
            col_id = colocated.get("id")
            if col_id and col_id != ensembl_info.variant_id:
                add_ids.add(str(col_id))
            for syn in colocated.get("var_synonyms", []):
                add_ids.add(str(syn))

    ensembl_info.additional_ids = sorted(list(add_ids))

    # --- 2. Summarize ClinVar data ---
    clinvar_info = ClinVarInfo(
        status=clinvar_result.status,
        matched=clinvar_result.status == "success",
        variation_id=None,
        accession=None,
        clinical_significance=None,
        review_status=None,
        condition=None,
    )
    
    omim_info = OMIMInfo(status="skipped", matched=False)
    pubmed_ids = set()
    hpo_list = []

    if clinvar_result.status == "success" and clinvar_result.data:
        records = clinvar_result.data.get("records", {})
        if isinstance(records, dict) and records:
            first_key = next(iter(records))
            rec = records[first_key]
            
            clinvar_info.variation_id = str(rec.get("uid") or rec.get("variation_id") or "") or None
            clinvar_info.accession = rec.get("accession")
            
            # Tri-partite classification details
            germline_info = rec.get("germline_classification", {})
            clinvar_info.clinical_significance = germline_info.get("description") or rec.get("clinical_significance")
            clinvar_info.review_status = germline_info.get("review_status") or rec.get("review_status")
            clinvar_info.last_evaluated = germline_info.get("last_evaluated")

            rev_stat = (clinvar_info.review_status or "").lower()
            if "no conflicts" in rev_stat:
                clinvar_info.conflict_status = "No conflicts"
            elif "conflicting" in rev_stat:
                clinvar_info.conflict_status = "Conflicting interpretations"
            else:
                clinvar_info.conflict_status = clinvar_info.review_status

            # Submissions count
            scvs = rec.get("supporting_submissions", {}).get("scv", [])
            if scvs:
                clinvar_info.submission_count = len(scvs)

            clinvar_info.classifications_summary = {
                "clinical_significance": clinvar_info.clinical_significance,
                "review_status": clinvar_info.review_status,
                "submission_count": clinvar_info.submission_count or 0,
            }

            # Traits & OMIM phenotypes
            assoc_conds = []
            omim_phenotypes = []
            primary_omim_id = None
            primary_omim_title = None

            trait_set = germline_info.get("trait_set", [])
            for trait in trait_set:
                tname = trait.get("trait_name")
                if tname and tname.lower() != "not provided" and tname not in assoc_conds:
                    assoc_conds.append(tname)

                for xref in trait.get("trait_xrefs", []):
                    if xref.get("db_source") == "OMIM":
                        m_id = str(xref.get("db_id"))
                        omim_phenotypes.append(
                            OMIMPhenotype(
                                mim_number=m_id,
                                title=tname,
                                inheritance=None,
                            )
                        )
                        if not primary_omim_id:
                            primary_omim_id = m_id
                            primary_omim_title = tname

            clinvar_info.associated_conditions = assoc_conds
            if assoc_conds and not clinvar_info.condition:
                clinvar_info.condition = assoc_conds[0]
            elif not clinvar_info.condition:
                clinvar_info.condition = rec.get("clinical_significance")

            if primary_omim_id:
                omim_info = OMIMInfo(
                    status="success",
                    matched=True,
                    mim_number=primary_omim_id,
                    title=primary_omim_title,
                    inheritance=None,
                    gene_mim_number=None,
                    phenotypes=omim_phenotypes,
                )

            # Parse ClinVar citations
            supp_pmids = set()
            for cit in rec.get("citations", []):
                pmid = str(cit.get("pubmed_id") or cit.get("id") or "")
                if pmid and pmid.isdigit():
                    supp_pmids.add(pmid)
                    pubmed_ids.add(pmid)

            clinvar_info.supporting_pmids = sorted(list(supp_pmids))

    # --- 3. Extract gnomAD population frequencies ---
    gnomad_info = GnomADInfo(status="skipped", matched=False)
    if vep_data:
        gnomad_af = None
        pop_freqs_map = {}
        for colocated in vep_data.get("colocated_variants", []):
            freqs = colocated.get("frequencies", {})
            for allele, p_freqs in freqs.items():
                for pop, freq in p_freqs.items():
                    if "gnomad" in pop.lower():
                        try:
                            f_val = float(freq)
                            pop_freqs_map[pop] = f_val
                            if gnomad_af is None:
                                gnomad_af = f_val
                        except (ValueError, TypeError):
                            pass

        if pop_freqs_map or gnomad_af is not None:
            gnomad_af_final = gnomad_af if gnomad_af is not None else 0.0
            gnomad_info = GnomADInfo(
                status="success",
                matched=True,
                allele_frequency=gnomad_af_final,
                pop_max_frequency=gnomad_af_final,
                allele_count=0 if gnomad_af_final == 0.0 else None,
                allele_number=None,
                homozygote_count=0 if gnomad_af_final == 0.0 else None,
                population_frequencies=pop_freqs_map or None,
            )

        # Extract PubMed citations from VEP
        for colocated in vep_data.get("colocated_variants", []):
            for pub in colocated.get("pubmed", []):
                pubmed_ids.add(str(pub))
            
            # Extract HPO Phenotypes from VEP
            for phen in colocated.get("phenotypes", []):
                hpo_id = phen.get("hpo_id") or phen.get("id")
                phen_name = phen.get("phenotype") or phen.get("name")
                if hpo_id and phen_name and hpo_id.upper().startswith("HP:"):
                    hpo_list.append(HPOInfo(hpo_id=hpo_id, phenotype=phen_name))

    pubmed_list = sorted(list(pubmed_ids))
    pubmed_details = fetch_pubmed_details(pubmed_list)

    return VariantResult(
        gene=raw_variant.get("gene"),
        transcript=raw_variant.get("transcript"),
        cdna=raw_variant.get("cdna"),
        protein=raw_variant.get("protein"),
        rsid=raw_variant.get("rsid"),
        zygosity=raw_variant.get("zygosity"),
        classification=raw_variant.get("classification"),
        variant_type=raw_variant.get("variant_type"),
        is_valid=raw_variant.get("is_valid", True),
        validation_message=raw_variant.get("validation_message"),
        normalized_hgvs=normalized_hgvs,
        ensembl=ensembl_info,
        clinvar=clinvar_info,
        gnomad=gnomad_info,
        omim=omim_info,
        hpo=hpo_list,
        pubmed=pubmed_list,
        pubmed_details=pubmed_details,
    )


# ---------------------------------------------------------------------------
# Step 7 — Full pipeline orchestrator
# ---------------------------------------------------------------------------

def analyze_wes_report(file_bytes: bytes) -> WESAnalysisResponse:
    """
    Orchestrate the full WES analysis pipeline for a PDF upload.

    Steps:
        1. Extract text from PDF (with PyMuPDF & OCR fallbacks).
        2. Extract variant fields using prioritized extraction layers:
           - Priority 1: Table extraction (variant_table)
           - Priority 2: Structured HGVS parsing (structured_hgvs / ocr_text)
           - Priority 3: Proximity anchor fallback (fallback_text / ocr_text)
        3. Validate each variant.
        4. Query Ensembl and ClinVar.
        5. Assemble structured response.

    Returns:
        WESAnalysisResponse with status, extraction info, and VariantResult list.
    """
    # --- PDF text & OCR extraction ---
    try:
        text, is_ocr = extract_text_from_pdf(file_bytes)
    except ValueError as exc:
        logger.warning("PDF extraction failed: %s", exc)
        return WESAnalysisResponse(
            status="error",
            extraction=ExtractionInfo(source="unknown", confidence="low"),
            message=str(exc),
        )

    # --- Prioritized extraction layers ---

    # Priority 1: Table-based extraction (from PDF table structures)
    raw_variants = extract_variants_from_table(file_bytes)
    if raw_variants:
        extraction_source = "variant_table"
        confidence = "high"
    else:
        # Priority 2: Structured HGVS compound regex extraction directly from report text
        raw_variants = extract_structured_hgvs(text)
        if raw_variants:
            extraction_source = "ocr_text" if is_ocr else "structured_hgvs"
            confidence = "high"
        else:
            # Priority 3: Proximity anchor fallback text extraction
            raw_variants = extract_variants(text)
            extraction_source = "ocr_text" if is_ocr else "fallback_text"
            confidence = "medium" if raw_variants else "low"

    if not raw_variants:
        return WESAnalysisResponse(
            status="success",
            extraction=ExtractionInfo(source=extraction_source, confidence="low"),
            variants=[],
            message="Text was extracted from the PDF but no variant patterns were detected. "
                    "The report may use a non‑standard format.",
        )

    results: List[VariantResult] = []
    for raw in raw_variants:
        validated = validate_variant(raw)
        ensembl_result = query_ensembl(
            gene=validated.get("gene"),
            cdna=validated.get("cdna"),
            protein=validated.get("protein"),
            transcript=validated.get("transcript"),
            rsid=validated.get("rsid"),
        )
        clinvar_result = query_clinvar(
            gene=validated.get("gene"),
            cdna=validated.get("cdna"),
            protein=validated.get("protein"),
            rsid=validated.get("rsid"),
            transcript=validated.get("transcript"),
            variation_id=validated.get("clinvar_variation_id"),
        )
        results.append(build_evidence(validated, ensembl_result, clinvar_result))

    return WESAnalysisResponse(
        status="success",
        extraction=ExtractionInfo(source=extraction_source, confidence=confidence),
        variants=results,
    )

def analyze_single_variant(variant_input: VariantInput) -> WESAnalysisResponse:
    """
    Run the datasource query pipeline for a single manually-supplied variant.
    Used by the /test-variant endpoint — no PDF required.
    """
    raw = {
        "gene": variant_input.gene,
        "transcript": variant_input.transcript,
        "cdna": variant_input.cdna,
        "protein": variant_input.protein,
        "rsid": variant_input.rsid,
        "zygosity": variant_input.zygosity,
        "classification": variant_input.classification,
        "variant_type": variant_input.variant_type,
    }

    validated = validate_variant(raw)

    ensembl_result = query_ensembl(
        gene=validated.get("gene"),
        cdna=validated.get("cdna"),
        protein=validated.get("protein"),
        transcript=validated.get("transcript"),
        rsid=validated.get("rsid"),
    )
    clinvar_result = query_clinvar(
        gene=validated.get("gene"),
        cdna=validated.get("cdna"),
        protein=validated.get("protein"),
        rsid=validated.get("rsid"),
        transcript=validated.get("transcript"),
        variation_id=validated.get("clinvar_variation_id"),
    )

    result = build_evidence(validated, ensembl_result, clinvar_result)
    
    return WESAnalysisResponse(
        status="success",
        extraction=ExtractionInfo(source="manual", confidence="high"),
        variants=[result]
    )
