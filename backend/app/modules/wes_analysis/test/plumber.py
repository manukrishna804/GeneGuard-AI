import pdfplumber
import re

# ==========================================
# STAGE 1: EXTRACT TEXT
# ==========================================
text = ""
with pdfplumber.open("medgenome_report.pdf") as pdf:
    for page in pdf.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

# ==========================================
# STAGE 2.1: EXTRACT SNVs
# ==========================================
def extract_snv_variants(text):
    pattern = r'\bc\.\d+[ACGT]>[ACGT]\b'
    return re.findall(pattern, text)

# ==========================================
# STAGE 2.2: EXTRACT CNVs
# ==========================================
def extract_cnv_variants(text):
    # pdfplumber may insert spaces into the CNV
    # because of the table layout.
    pattern = r'chr17:g\.\([^)]*\)\s*_\s*\([^)]*\)del'
    return re.findall(pattern, text)

# ==========================================
# TEST BASIC EXTRACTION
# ==========================================
snv_variants = extract_snv_variants(text)
cnv_variants = extract_cnv_variants(text)

print("SNV variants:")
print(snv_variants)
print("\nCNV variants:")
print(cnv_variants)

# ==========================================
# STAGE 2.4: EXTRACT GENE + VARIANT
# ==========================================
def extract_variant_records(text):
    records = []

    # --------------------------------------
    # SNVs
    # --------------------------------------
    snv_pattern = r'\bc\.\d+[ACGT]>[ACGT]\b'
    for match in re.finditer(snv_pattern, text):
        variant = match.group()
        # Look at the text immediately before
        # the variant to find the gene.
        context = text[max(0, match.start() - 50):match.start()]
        gene_match = re.search(r'\b[A-Z0-9]{2,15}\b\s*\(-\)\s*$', context)
        if gene_match:
            gene = gene_match.group().split()[0]
            records.append({
                "gene": gene,
                "variant": variant,
                "type": "SNV"
            })

    # --------------------------------------
    # CNVs
    # --------------------------------------
    # NOTE: in the interpretation paragraph, the gene name (PYCR1)
    # appears AFTER the CNV coordinates, not before
    # ("...chr17:g.(...)del], comprising exons 1 to 2 of the PYCR1 gene...").
    # So we search a window spanning both before AND after the match.
    cnv_pattern = r'chr17:g\.\([^)]*\)\s*_\s*\([^)]*\)del'
    for match in re.finditer(cnv_pattern, text):
        variant = match.group()
        window_start = max(0, match.start() - 250)
        window_end = min(len(text), match.end() + 250)
        context = text[window_start:window_end]

        gene_match = re.search(r'\bPYCR1\b', context)
        if gene_match:
            records.append({
                "gene": "PYCR1",
                "variant": variant,
                "type": "CNV"
            })

    return records

# ==========================================
# TEST STRUCTURED RECORDS
# ==========================================
variant_records = extract_variant_records(text)
print("\nVariant records:")
for record in variant_records:
    print(record)


def validate_variant(record):

    if not record["gene"]:
        return False

    if not record["variant"]:
        return False

    if record["type"] not in ["SNV", "CNV"]:
        return False

    return True

print("\nValidation:")

for record in variant_records:
    print(record, "->", validate_variant(record))