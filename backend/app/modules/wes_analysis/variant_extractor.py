import re

from .pdf_extractor import extract_text_from_pdf


# ==========================================
# STAGE 2.1: EXTRACT SNVs
# ==========================================

def extract_snv_variants(text):
    """
    Extract SNV cDNA changes such as:

        c.3559C>T
        c.123A>G
    """

    pattern = r'\bc\.\d+[ACGT]>[ACGT]\b'

    return re.findall(
        pattern,
        text
    )


# ==========================================
# STAGE 2.2: EXTRACT CNVs
# ==========================================

def extract_cnv_variants(text):
    """
    Extract genomic CNV notations such as:

        chr17:g.(81936194_81936747)_(81937239_?)del
        chr1:g.(100000_100500)_(101000_?)dup

    Supports chromosomes 1-22, X, and Y,
    and both deletion (del) and duplication (dup).
    """

    pattern = (
        r'chr(?:[0-9]+|X|Y):g\.'
        r'\([^)]*\)'
        r'\s*_\s*'
        r'\([^)]*\)'
        r'(?:del|dup)'
    )

    return re.findall(
        pattern,
        text
    )


# ==========================================
# STAGE 2.3: EXTRACT STRUCTURED RECORDS
# ==========================================

def extract_variant_records(text):
    """
    Convert extracted variants into structured records.

    Example output:

        {
            "gene": "COL2A1",
            "variant": "c.3559C>T",
            "type": "SNV"
        }

        {
            "gene": "PYCR1",
            "variant": "chr17:g.(81936194_81936747)_(81937239_?)del",
            "type": "CNV"
        }
    """

    records = []

    # ======================================
    # SNVs
    # ======================================

    snv_pattern = r'\bc\.\d+[ACGT]>[ACGT]\b'

    for match in re.finditer(
        snv_pattern,
        text
    ):

        variant = match.group()

        # ----------------------------------
        # Look backward for context
        # ----------------------------------

        # Current report structure is approximately:
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

        # ----------------------------------
        # Find gene
        # ----------------------------------

        gene_matches = re.findall(
            r'\b[A-Z0-9]{2,15}\b\s*\(-\)',
            context
        )

        # ----------------------------------
        # Find Ensembl transcript
        # ----------------------------------

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

            records.append(
                record
            )

    # ======================================
    # CNVs
    # ======================================

        # ======================================
    # CNVs
    # ======================================

    cnv_pattern = (
        r'chr(?:[0-9]+|X|Y):g\.'
        r'\([^)]*\)'
        r'\s*_\s*'
        r'\([^)]*\)'
        r'(?:del|dup)'
    )

    for match in re.finditer(
        cnv_pattern,
        text
    ):

        variant = match.group()

        # Look around the CNV to find the associated gene.
        # The current report contains text like:
        #
        # "... comprising exons 1 to 2 of the PYCR1 gene ..."
        #
        # so search a wider context around the variant.

        context_start = max(
            0,
            match.start() - 500
        )

        context_end = min(
            len(text),
            match.end() + 500
        )

        context = text[
            context_start:
            context_end
        ]

        # ----------------------------------
        # Find "<GENE> gene"
        # ----------------------------------

        gene_matches = re.findall(
            r'\b([A-Z0-9]{2,15})\s+gene\b',
            context
        )

        if gene_matches:

            gene = gene_matches[-1]

            records.append({
                "gene": gene,
                "variant": variant,
                "type": "CNV"
            })

    return records


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    pdf_path = "medgenome_report.pdf"

    # --------------------------------------
    # Extract PDF text
    # --------------------------------------

    text = extract_text_from_pdf(
        pdf_path
    )

    # --------------------------------------
    # SNVs
    # --------------------------------------

    print("\nSNV variants:")

    print(
        extract_snv_variants(
            text
        )
    )

    # --------------------------------------
    # CNVs
    # --------------------------------------

    print("\nCNV variants:")

    print(
        extract_cnv_variants(
            text
        )
    )

    # --------------------------------------
    # Structured records
    # --------------------------------------

    print("\nVariant records:")

    records = extract_variant_records(
        text
    )

    for record in records:

        print(
            record
        )