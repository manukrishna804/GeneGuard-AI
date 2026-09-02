# ==========================================
# STAGE 3: BASIC VARIANT VALIDATION
# ==========================================


VALID_TYPES = {
    "SNV",
    "CNV"
}


def validate_variant(record):
    """
    Perform basic sanity checks on one extracted
    variant record.

    Returns:
        dict: validation result
    """

    errors = []
    warnings = []

    # ==========================================
    # 1. Required fields
    # ==========================================

    required_fields = [
        "gene",
        "variant",
        "type"
    ]

    for field in required_fields:

        if field not in record:
            errors.append(
                f"Missing field: {field}"
            )

        elif not record[field]:
            errors.append(
                f"Empty field: {field}"
            )


    # ==========================================
    # 2. Variant type
    # ==========================================

    variant_type = record.get("type")

    if variant_type not in VALID_TYPES:

        errors.append(
            f"Invalid variant type: {variant_type}"
        )


    # ==========================================
    # 3. Gene
    # ==========================================

    gene = record.get("gene")

    if gene is not None and not isinstance(gene, str):

        errors.append(
            "Gene must be a string"
        )


    # ==========================================
    # 4. Variant
    # ==========================================

    variant = record.get("variant")

    if variant is not None and not isinstance(variant, str):

        errors.append(
            "Variant must be a string"
        )


    # ==========================================
    # 5. SNV warning
    # ==========================================


    # ==========================================
    # FINAL RESULT
    # ==========================================

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    from pdf_extractor import extract_text_from_pdf
    from variant_extractor import extract_variant_records


    # --------------------------------------
    # Extract PDF text
    # --------------------------------------

    pdf_path = "medgenome_report.pdf"

    text = extract_text_from_pdf(
        pdf_path
    )


    # --------------------------------------
    # Extract variants
    # --------------------------------------

    records = extract_variant_records(
        text
    )


    # --------------------------------------
    # Validate
    # --------------------------------------

    print("\n==========================================")
    print("VARIANT VALIDATION")
    print("==========================================")


    for record in records:

        result = validate_variant(
            record
        )

        print("\nVariant:")
        print(record)

        print("\nValidation:")
        print(result)

        print("-" * 50)