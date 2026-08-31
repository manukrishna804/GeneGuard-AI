import re

from pdf_extractor import extract_text_from_pdf


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
    pattern = r'chr17:g\.\([^)]*\)\s*_\s*\([^)]*\)del'
    return re.findall(pattern, text)


# ==========================================
# STAGE 2.3: EXTRACT STRUCTURED RECORDS
# ==========================================

def extract_variant_records(text):

    records = []

    # ======================================
    # SNVs
    # ======================================

    snv_pattern = r'\bc\.\d+[ACGT]>[ACGT]\b'

    for match in re.finditer(snv_pattern, text):

        variant = match.group()

        # Look further back because the report has:
        #
        # COL2A1 (-)
        # (ENST00000380518.8)
        # Exon 50
        # c.3559C>T

        context_start = max(
            0,
            match.start() - 200
        )

        context = text[
            context_start:
            match.start()
        ]

        # Find gene names
        gene_matches = re.findall(
            r'\b[A-Z0-9]{2,15}\b\s*\(-\)',
            context
        )

        # Find Ensembl transcript
        transcript_matches = re.findall(
            r'ENST\d+(?:\.\d+)?',
            context
        )

        if gene_matches:

            gene = gene_matches[-1].split()[0]

            record = {
                "gene": gene,
                "variant": variant,
                "type": "SNV"
            }

            if transcript_matches:
                record["transcript"] = (
                    transcript_matches[-1]
                )

            records.append(record)


    # ======================================
    # CNVs
    # ======================================

    cnv_pattern = (
        r'chr17:g\.\([^)]*\)\s*_\s*\([^)]*\)del'
    )

    for match in re.finditer(
        cnv_pattern,
        text
    ):

        variant = match.group()

        window_start = max(
            0,
            match.start() - 250
        )

        window_end = min(
            len(text),
            match.end() + 250
        )

        context = text[
            window_start:
            window_end
        ]

        if re.search(r'\bPYCR1\b', context):

            records.append({
                "gene": "PYCR1",
                "variant": variant,
                "type": "CNV"
            })

    return records


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    pdf_path = "medgenome_report.pdf"

    text = extract_text_from_pdf(
        pdf_path
    )

    print("\nSNV variants:")
    print(
        extract_snv_variants(text)
    )

    print("\nCNV variants:")
    print(
        extract_cnv_variants(text)
    )

    print("\nVariant records:")

    records = extract_variant_records(text)

    for record in records:
        print(record)