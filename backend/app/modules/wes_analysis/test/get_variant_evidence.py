import requests


# ==========================================
# VARIANTVALIDATOR
# ==========================================

def validate_variant(hgvs):

    url = (
        "https://rest.variantvalidator.org/"
        "VariantValidator/variantvalidator/"
        "GRCh38/"
        f"{hgvs}/"
        "all"
    )

    response = requests.get(
        url,
        headers={
            "Accept": "application/json"
        },
        timeout=30
    )

    response.raise_for_status()

    return response.json()


# ==========================================
# EXTRACT VARIANTVALIDATOR INFORMATION
# ==========================================

def extract_validator_evidence(data, hgvs):

    result = data.get(hgvs)

    if not result:
        return {
            "validated": False,
            "error": "VariantValidator returned no result"
        }

    evidence = {
        "validated": True,
        "input_hgvs": result.get("submitted_variant"),
        "gene": result.get("gene_symbol"),
        "assembly": result.get("selected_assembly"),
        "transcript": result.get("hgvs_transcript_variant"),
        "protein": result.get(
            "hgvs_predicted_protein_consequence",
            {}
        ).get("tlr"),
        "genomic": None,
        "exon": None,
        "warnings": result.get(
            "validation_warnings",
            []
        )
    }

    # --------------------------------------
    # GRCh38 genomic representation
    # --------------------------------------

    loci = result.get(
        "primary_assembly_loci",
        {}
    )

    grch38 = loci.get("grch38")

    if grch38:

        evidence["genomic"] = grch38.get(
            "hgvs_genomic_description"
        )

        vcf = grch38.get("vcf", {})

        evidence["vcf"] = {
            "chromosome": vcf.get("chr"),
            "position": vcf.get("pos"),
            "reference": vcf.get("ref"),
            "alternate": vcf.get("alt")
        }


    # --------------------------------------
    # Exon
    # --------------------------------------

    exon_data = result.get(
        "variant_exonic_positions",
        {}
    )

    grch38_exon = exon_data.get(
        "NC_000012.12"
    )

    if grch38_exon:

        evidence["exon"] = {
            "start": grch38_exon.get(
                "start_exon"
            ),
            "end": grch38_exon.get(
                "end_exon"
            )
        }


    return evidence


# ==========================================
# MYVARIANT.INFO
# ==========================================

def lookup_myvariant(genomic_variant):

    url = (
        "https://myvariant.info/v1/variant/"
        f"{genomic_variant}"
    )

    params = {
        "assembly": "hg38"
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


# ==========================================
# EXTRACT MYVARIANT EVIDENCE
# ==========================================

def extract_myvariant_evidence(data, target_hgvsc):

    evidence = {
        "clingen_caid": None,
        "gene": None,
        "consequence": None,
        "cadd": None,
        "sift": [],
        "polyphen": {},
        "revel": [],
        "conservation": {}
    }


    # ======================================
    # ClinGen
    # ======================================

    clingen = data.get("clingen", {})

    if clingen:
        evidence["clingen_caid"] = clingen.get(
            "caid"
        )


    # ======================================
    # dbNSFP
    # ======================================

    dbnsfp = data.get("dbnsfp", {})


    # Gene
    genes = dbnsfp.get("genename", [])

    if isinstance(genes, str):
        genes = [genes]

    if genes:
        evidence["gene"] = genes[0]


    # ======================================
    # CADD
    # ======================================

    cadd = dbnsfp.get("cadd", {})

    if cadd:
        evidence["cadd"] = cadd.get(
            "phred"
        )


    # ======================================
    # SIFT
    # ======================================

    sift = dbnsfp.get("sift", {})

    if sift:

        predictions = sift.get(
            "pred",
            []
        )

        if isinstance(predictions, str):
            predictions = [predictions]

        evidence["sift"] = predictions


    # ======================================
    # PolyPhen
    # ======================================

    polyphen = dbnsfp.get(
        "polyphen2",
        {}
    )

    if polyphen:

        hdiv = polyphen.get(
            "hdiv",
            {}
        )

        hvar = polyphen.get(
            "hvar",
            {}
        )

        hdiv_pred = hdiv.get(
            "pred",
            []
        )

        hvar_pred = hvar.get(
            "pred",
            []
        )

        if isinstance(hdiv_pred, str):
            hdiv_pred = [hdiv_pred]

        if isinstance(hvar_pred, str):
            hvar_pred = [hvar_pred]

        evidence["polyphen"] = {
            "hdiv": hdiv_pred,
            "hvar": hvar_pred
        }


    # ======================================
    # REVEL
    # ======================================

    revel = dbnsfp.get(
        "revel",
        {}
    )

    if revel:

        scores = revel.get(
            "score",
            []
        )

        if isinstance(scores, (int, float)):
            scores = [scores]

        evidence["revel"] = scores


    # ======================================
    # Conservation
    # ======================================

    phylop = dbnsfp.get(
        "phylop",
        {}
    )

    if phylop:
        evidence["conservation"]["phylop"] = phylop


    phastcons = dbnsfp.get(
        "phastcons",
        {}
    )

    if phastcons:
        evidence["conservation"]["phastcons"] = phastcons


    # ======================================
    # SNPEFF
    # ======================================

    snpeff = data.get(
        "snpeff",
        {}
    )

    annotations = snpeff.get(
        "ann",
        []
    )


    # Find the annotation matching
    # the actual cDNA variant.

    for annotation in annotations:

        if annotation.get(
            "hgvs_c"
        ) == target_hgvsc:

            evidence["consequence"] = {

                "transcript":
                    annotation.get(
                        "feature_id"
                    ),

                "effect":
                    annotation.get(
                        "effect"
                    ),

                "impact":
                    annotation.get(
                        "putative_impact"
                    ),

                "hgvsc":
                    annotation.get(
                        "hgvs_c"
                    ),

                "hgvsp":
                    annotation.get(
                        "hgvs_p"
                    )
            }

            break


    return evidence


# ==========================================
# MAIN FUNCTION
# ==========================================

def get_variant_evidence(
    gene,
    variant,
    genomic_variant,
    transcript_hgvs
):

    # --------------------------------------
    # 1. Validate / normalize
    # --------------------------------------

    validator_raw = validate_variant(
        transcript_hgvs
    )

    validator = extract_validator_evidence(
        validator_raw,
        transcript_hgvs
    )


    # --------------------------------------
    # 2. MyVariant lookup
    # --------------------------------------

    myvariant_raw = lookup_myvariant(
        genomic_variant
    )

    myvariant = extract_myvariant_evidence(
        myvariant_raw,
        variant
    )


    # --------------------------------------
    # 3. Combine
    # --------------------------------------

    return {

        "gene": gene,

        "variant": variant,

        "type": "SNV",

        "validator": validator,

        "myvariant": myvariant
    }


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    result = get_variant_evidence(

        gene="COL2A1",

        variant="c.3559C>T",

        genomic_variant="chr12:g.47976001G>A",

        transcript_hgvs=
            "NM_001844.4:c.3559C>T"
    )


    print("\n==========================================")
    print("VARIANT EVIDENCE")
    print("==========================================")

    print(result)