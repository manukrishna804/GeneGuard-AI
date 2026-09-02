import requests


# ============================================================
# HELPER: HTTP GET JSON
# ============================================================

def get_json(url, params=None):
    """
    Perform a GET request and return JSON.
    """

    response = requests.get(
        url,
        params=params,
        headers={
            "Accept": "application/json"
        },
        timeout=30
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# 4.1 VARIANTVALIDATOR
# ============================================================

def validate_with_variantvalidator(hgvs):
    """
    Validate an HGVS variant using VariantValidator.

    Example:
        NM_001844.4:c.3559C>T
    """

    url = (
        "https://rest.variantvalidator.org/"
        "VariantValidator/variantvalidator/"
        "GRCh38/"
        f"{hgvs}/"
        "all"
    )

    return get_json(url)


def extract_validation_evidence(data, hgvs):
    """
    Extract useful information from VariantValidator.
    """

    result = data.get(hgvs)

    if not result:
        return {
            "validated": False,
            "error": "No VariantValidator result returned"
        }

    evidence = {
        # 'flag' is at the top level of the response
        "validated": data.get("flag") == "gene_variant",

        "input_hgvs": result.get(
            "submitted_variant"
        ),

        "gene": result.get(
            "gene_symbol"
        ),

        "assembly": result.get(
            "selected_assembly"
        ),

        "transcript": result.get(
            "hgvs_transcript_variant"
        ),

        "protein": result.get(
            "hgvs_predicted_protein_consequence",
            {}
        ).get("tlr"),

        "genomic": None,

        "exon": None,

        "warnings": result.get(
            "validation_warnings",
            []
        ),

        "vcf": None
    }

    # --------------------------------------------------------
    # GRCh38 genomic representation
    # --------------------------------------------------------

    loci = result.get(
        "primary_assembly_loci",
        {}
    )

    grch38 = loci.get("grch38")

    if grch38:

        evidence["genomic"] = grch38.get(
            "hgvs_genomic_description"
        )

        vcf = grch38.get("vcf")

        if vcf:

            evidence["vcf"] = {
                "chromosome": vcf.get("chr"),
                "position": vcf.get("pos"),
                "reference": vcf.get("ref"),
                "alternate": vcf.get("alt")
            }

    # --------------------------------------------------------
    # Exon information
    # --------------------------------------------------------

    exon_data = result.get(
        "variant_exonic_positions",
        {}
    )

    for _, exon_info in exon_data.items():

        if exon_info:

            evidence["exon"] = {
                "start": exon_info.get(
                    "start_exon"
                ),
                "end": exon_info.get(
                    "end_exon"
                )
            }

            break

    return evidence


# ============================================================
# 4.2 MYVARIANT.INFO
# ============================================================

def lookup_myvariant(genomic_variant):
    """
    Query MyVariant.info using genomic HGVS.

    Example:
        chr12:g.47976001G>A
    """

    url = (
        "https://myvariant.info/v1/variant/"
        f"{genomic_variant}"
    )

    params = {
        "assembly": "hg38"
    }

    return get_json(
        url,
        params=params
    )


def extract_myvariant_evidence(
    data,
    target_hgvsc
):
    """
    Extract the useful MyVariant annotations
    for the requested cDNA change.
    """

    evidence = {
        "found": True,

        "clingen_caid": None,

        "gene": None,

        "consequence": None,

        "computational_predictions": {
            "cadd": None,
            "sift": [],
            "polyphen": {},
            "revel": []
        },

        "conservation": {}
    }

    # --------------------------------------------------------
    # ClinGen
    # --------------------------------------------------------

    clingen = data.get(
        "clingen",
        {}
    )

    if clingen:

        evidence["clingen_caid"] = clingen.get(
            "caid"
        )

    # --------------------------------------------------------
    # dbNSFP
    # --------------------------------------------------------

    dbnsfp = data.get(
        "dbnsfp",
        {}
    )

    # Gene
    genes = dbnsfp.get(
        "genename",
        []
    )

    if isinstance(genes, str):

        genes = [genes]

    if genes:

        evidence["gene"] = genes[0]

    # --------------------------------------------------------
    # CADD
    # --------------------------------------------------------

    cadd = dbnsfp.get(
        "cadd",
        {}
    )

    if cadd:

        evidence[
            "computational_predictions"
        ]["cadd"] = cadd.get(
            "phred"
        )

    # --------------------------------------------------------
    # SIFT
    # --------------------------------------------------------

    sift = dbnsfp.get(
        "sift",
        {}
    )

    if sift:

        predictions = sift.get(
            "pred",
            []
        )

        if isinstance(
            predictions,
            str
        ):

            predictions = [predictions]

        evidence[
            "computational_predictions"
        ]["sift"] = predictions

    # --------------------------------------------------------
    # PolyPhen
    # --------------------------------------------------------

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

        if isinstance(
            hdiv_pred,
            str
        ):

            hdiv_pred = [
                hdiv_pred
            ]

        if isinstance(
            hvar_pred,
            str
        ):

            hvar_pred = [
                hvar_pred
            ]

        evidence[
            "computational_predictions"
        ]["polyphen"] = {

            "hdiv": hdiv_pred,

            "hvar": hvar_pred
        }

    # --------------------------------------------------------
    # REVEL
    # --------------------------------------------------------

    revel = dbnsfp.get(
        "revel",
        {}
    )

    if revel:

        scores = revel.get(
            "score",
            []
        )

        if isinstance(
            scores,
            (int, float)
        ):

            scores = [scores]

        evidence[
            "computational_predictions"
        ]["revel"] = scores

    # --------------------------------------------------------
    # Conservation
    # --------------------------------------------------------

    phylop = dbnsfp.get(
        "phylop",
        {}
    )

    if phylop:

        evidence[
            "conservation"
        ]["phylop"] = phylop

    phastcons = dbnsfp.get(
        "phastcons",
        {}
    )

    if phastcons:

        evidence[
            "conservation"
        ]["phastcons"] = phastcons

    # --------------------------------------------------------
    # SnpEff
    # --------------------------------------------------------

    snpeff = data.get(
        "snpeff",
        {}
    )

    annotations = snpeff.get(
        "ann",
        []
    )

    # Find the annotation matching our
    # actual cDNA variant.
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


# ============================================================
# 4.3 dbVar
# ============================================================

def search_dbvar_cnv(
    gene,
    chromosome,
    start,
    end
):
    """
    Search dbVar for structural-variant candidates
    around a genomic region.
    """

    url = (
        "https://eutils.ncbi.nlm.nih.gov/"
        "entrez/eutils/esearch.fcgi"
    )

    query = (
        f'{gene}[Gene] AND '
        f'{chromosome}[Chr] AND '
        f'('
        f'{start}:{end}[ChrPos] OR '
        f'{start}:{end}[ChrEnd]'
        f') AND '
        f'"deletion"[variant_type]'
    )

    params = {
        "db": "dbvar",
        "term": query,
        "retmode": "json",
        "retmax": 50
    }

    data = get_json(
        url,
        params=params
    )

    return data[
        "esearchresult"
    ][
        "idlist"
    ]


def get_dbvar_summaries(ids):
    """
    Retrieve summary information for dbVar IDs.
    """

    if not ids:
        return []

    url = (
        "https://eutils.ncbi.nlm.nih.gov/"
        "entrez/eutils/esummary.fcgi"
    )

    params = {
        "db": "dbvar",
        "id": ",".join(ids),
        "retmode": "json"
    }

    data = get_json(
        url,
        params=params
    )

    results = []

    for dbvar_id in ids:

        record = data[
            "result"
        ].get(
            dbvar_id
        )

        if not record:
            continue

        results.append({

            "dbvar_id":
                dbvar_id,

            "placements":
                record.get(
                    "dbvarplacementlist",
                    []
                ),

            "genes":
                record.get(
                    "dbvargenelist",
                    []
                ),

            "variant_type":
                record.get(
                    "dbvarvarianttypelist",
                    []
                ),

            "clinical_significance":
                record.get(
                    "dbvarclinicalsignificancelist",
                    []
                ),

            "method":
                record.get(
                    "dbvarmethodlist",
                    []
                ),

            "study":
                record.get(
                    "st"
                ),

            "structural_variant":
                record.get(
                    "sv"
                )
        })

    return results


def get_cnv_evidence(record):
    """
    Build dbVar evidence for the current PYCR1
    CNV test case.
    """

    gene = record.get(
        "gene"
    )

    variant = record.get(
        "variant"
    )

    # --------------------------------------------------------
    # Current MedGenome CNV
    # --------------------------------------------------------

    if (
        gene == "PYCR1"
        and "81936194" in variant
    ):

        chromosome = "17"

        start = 81936194

        # The report's second endpoint is uncertain.
        end = 81937239

    else:

        return {
            "status": "unsupported",
            "message": (
                "CNV lookup is not yet "
                "implemented for this variant."
            )
        }

    print(
        "\nRunning dbVar..."
    )

    ids = search_dbvar_cnv(
        gene,
        chromosome,
        start,
        end
    )

    print(
        f"dbVar candidates found: {len(ids)}"
    )

    candidates = get_dbvar_summaries(
        ids
    )

    return {

        "status": "success",

        "source_variant": record,

        "search_region": {
            "chromosome": chromosome,
            "start": start,
            "end": end
        },

        "dbvar_candidates": candidates
    }

def normalize_snv(record):
    """
    Resolve an SNV into a transcript-level and genomic representation.

    Current supported test case:
        COL2A1 c.3559C>T
    """

    gene = record.get("gene")
    variant = record.get("variant")

    if (
        gene == "COL2A1"
        and variant == "c.3559C>T"
    ):
        return {
            "status": "success",
            "input_variant": variant,
            "gene": gene,
            "transcript": "NM_001844.4",
            "transcript_hgvs": "NM_001844.4:c.3559C>T",
            "genomic": "NC_000012.12:g.47976001G>A",
            "genomic_variant": "chr12:g.47976001G>A",
            "assembly": "GRCh38",
        }

    return {
        "status": "unsupported",
        "message": (
            "SNV normalization is not yet implemented "
            "for this variant."
        ),
    }
# ============================================================
# 4.4 SNV EVIDENCE
# ============================================================

def get_snv_evidence(record):
    """
    Build evidence for the current SNV.

    The current test case is:
        COL2A1 c.3559C>T
    """

    normalization = normalize_snv(record)

    if normalization["status"] != "success":
        return normalization

    transcript_hgvs = normalization["transcript_hgvs"]
    genomic_variant = normalization["genomic_variant"]
    variant = record.get("variant")


    # --------------------------------------------------------
    # VariantValidator
    # --------------------------------------------------------

    print(
        "\nRunning VariantValidator..."
    )

    validator_raw = (
        validate_with_variantvalidator(
            transcript_hgvs
        )
    )

    validator = (
        extract_validation_evidence(
            validator_raw,
            transcript_hgvs
        )
    )

    # --------------------------------------------------------
    # MyVariant
    # --------------------------------------------------------

    print(
        "Running MyVariant.info..."
    )

    myvariant_raw = lookup_myvariant(
        genomic_variant
    )

    myvariant = (
        extract_myvariant_evidence(
            myvariant_raw,
            variant
        )
    )

    return {
    "status": "success",
    "source_variant": record,
    "normalization": normalization,
    "variantvalidator": validator,
    "myvariant": myvariant
}


# ============================================================
# 4.5 MAIN ENTRY POINT
# ============================================================

def get_variant_evidence(record):
    """
    Main Stage 4 function.

    Automatically chooses the correct evidence
    pipeline based on variant type.
    """

    variant_type = record.get(
        "type"
    )

    if variant_type == "SNV":

        return get_snv_evidence(
            record
        )

    if variant_type == "CNV":

        return get_cnv_evidence(
            record
        )

    return {
        "status": "error",
        "message": (
            f"Unsupported variant type: "
            f"{variant_type}"
        )
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # TEST 1: SNV
    # --------------------------------------------------------

    snv_record = {
        "gene": "COL2A1",
        "variant": "c.3559C>T",
        "type": "SNV"
    }

    print(
        "\n=========================================="
    )

    print(
        "TEST 1: SNV"
    )

    print(
        "=========================================="
    )

    snv_result = get_variant_evidence(
        snv_record
    )

    print(
        "\nSNV EVIDENCE:"
    )

    print(snv_result)


    # --------------------------------------------------------
    # TEST 2: CNV
    # --------------------------------------------------------

    cnv_record = {

        "gene": "PYCR1",

        "variant":
            "chr17:g.(81936194_81936747)"
            "_(81937239_?)del",

        "type": "CNV"
    }

    print(
        "\n=========================================="
    )

    print(
        "TEST 2: CNV"
    )

    print(
        "=========================================="
    )

    cnv_result = get_variant_evidence(
        cnv_record
    )

    print(
        "\nCNV EVIDENCE:"
    )

    print(cnv_result)