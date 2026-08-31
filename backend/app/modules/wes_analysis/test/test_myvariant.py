import requests


# ==========================================
# STAGE 4.2: MYVARIANT CLEAN EVIDENCE
# ==========================================

def lookup_variant(variant):

    url = f"https://myvariant.info/v1/variant/{variant}"

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
# EXTRACT CLEAN EVIDENCE
# ==========================================

def extract_myvariant_evidence(data):

    evidence = {
        "variant": data.get("_id"),
        "chromosome": data.get("chrom"),
        "clingen_caid": None,
        "gene": None,
        "transcripts": [],
        "hgvsc": [],
        "hgvsp": [],
        "consequence": None,
        "cadd": None,
        "sift": [],
        "polyphen": {},
        "revel": [],
        "conservation": {}
    }

    # ==========================================
    # ClinGen
    # ==========================================

    clingen = data.get("clingen", {})

    if clingen:
        evidence["clingen_caid"] = clingen.get("caid")


    # ==========================================
    # dbNSFP
    # ==========================================

    dbnsfp = data.get("dbnsfp", {})


    # ------------------------------------------
    # Gene
    # ------------------------------------------

    genes = dbnsfp.get("genename", [])

    if isinstance(genes, str):
        genes = [genes]

    if genes:
        evidence["gene"] = genes[0]


    # ------------------------------------------
    # HGVS cDNA
    # ------------------------------------------

    hgvsc = dbnsfp.get("hgvsc", [])

    if isinstance(hgvsc, str):
        hgvsc = [hgvsc]

    evidence["hgvsc"] = hgvsc


    # ------------------------------------------
    # HGVS Protein
    # ------------------------------------------

    hgvsp = dbnsfp.get("hgvsp", [])

    if isinstance(hgvsp, str):
        hgvsp = [hgvsp]

    evidence["hgvsp"] = hgvsp


    # ------------------------------------------
    # Ensembl transcripts
    # ------------------------------------------

    ensembl = dbnsfp.get("ensembl", {})

    transcript_ids = ensembl.get("transcriptid", [])

    if isinstance(transcript_ids, str):
        transcript_ids = [transcript_ids]

    for transcript in transcript_ids:

        if transcript not in evidence["transcripts"]:
            evidence["transcripts"].append(transcript)


    # ==========================================
    # CADD
    # ==========================================

    cadd = dbnsfp.get("cadd", {})

    if cadd:
        evidence["cadd"] = cadd.get("phred")


    # ==========================================
    # SIFT
    # ==========================================

    sift = dbnsfp.get("sift", {})

    if sift:
        predictions = sift.get("pred", [])

        if isinstance(predictions, str):
            predictions = [predictions]

        evidence["sift"] = predictions


    # ==========================================
    # PolyPhen
    # ==========================================

    polyphen = dbnsfp.get("polyphen2", {})

    if polyphen:

        hdiv = polyphen.get("hdiv", {})
        hvar = polyphen.get("hvar", {})

        hdiv_predictions = hdiv.get("pred", [])
        hvar_predictions = hvar.get("pred", [])

        if isinstance(hdiv_predictions, str):
            hdiv_predictions = [hdiv_predictions]

        if isinstance(hvar_predictions, str):
            hvar_predictions = [hvar_predictions]

        evidence["polyphen"] = {
            "hdiv": hdiv_predictions,
            "hvar": hvar_predictions
        }


    # ==========================================
    # REVEL
    # ==========================================

    revel = dbnsfp.get("revel", {})

    if revel:

        scores = revel.get("score", [])

        if isinstance(scores, (int, float)):
            scores = [scores]

        evidence["revel"] = scores


    # ==========================================
    # Conservation
    # ==========================================

    phylop = dbnsfp.get("phylop", {})

    if phylop:
        evidence["conservation"]["phylop"] = phylop


    phastcons = dbnsfp.get("phastcons", {})

    if phastcons:
        evidence["conservation"]["phastcons"] = phastcons


    # ==========================================
    # SNPEFF
    # ==========================================

    snpeff = data.get("snpeff", {})

    annotations = snpeff.get("ann", [])


    # ==========================================
    # IMPORTANT:
    # Find the annotation corresponding to
    # OUR actual cDNA change.
    # ==========================================

    target_hgvsc = "c.3559C>T"

    for annotation in annotations:

        annotation_hgvsc = annotation.get("hgvs_c")

        if annotation_hgvsc == target_hgvsc:

            evidence["consequence"] = {
                "transcript": annotation.get("feature_id"),
                "effect": annotation.get("effect"),
                "impact": annotation.get("putative_impact"),
                "hgvsc": annotation.get("hgvs_c"),
                "hgvsp": annotation.get("hgvs_p")
            }

            break


    return evidence


# ==========================================
# TEST
# ==========================================

variant = "chr12:g.47976001G>A"

print("Looking up variant:")
print(variant)

print("\nFetching MyVariant data...")

raw_data = lookup_variant(variant)

print("Lookup successful!")


# ==========================================
# CLEAN THE RESPONSE
# ==========================================

clean_evidence = extract_myvariant_evidence(raw_data)


# ==========================================
# PRINT RESULT
# ==========================================

print("\n==========================================")
print("CLEAN MYVARIANT EVIDENCE")
print("==========================================")

print(clean_evidence)