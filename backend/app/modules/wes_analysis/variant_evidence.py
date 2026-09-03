import requests
import re


# ============================================================
# HELPER: HTTP GET JSON
# ============================================================

def get_json(url, params=None):
    """
    Perform a GET request and return JSON.

    External evidence services are allowed to fail without
    crashing the entire WES pipeline.
    """

    try:
        response = requests.get(
            url,
            params=params,
            headers={
                "Accept": "application/json"
            },
            timeout=30
        )

        response.raise_for_status()

        return {
            "status": "success",
            "data": response.json()
        }

    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "error_type": "timeout",
            "message": "External service request timed out."
        }

    except requests.exceptions.RequestException as exc:
        return {
            "status": "error",
            "error_type": "request",
            "message": str(exc)
        }

    except ValueError:
        return {
            "status": "error",
            "error_type": "invalid_json",
            "message": "External service returned invalid JSON."
        }
# ============================================================
# 4.1 VARIANTVALIDATOR
# ============================================================

def validate_with_variantvalidator(hgvs):
    url = (
        "https://rest.variantvalidator.org/"
        "VariantValidator/variantvalidator/GRCh38/"
        f"{hgvs}/all"
    )

    result = get_json(url)

    if result.get("status") != "success":
        return result

    return result["data"]
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

    Returns a normalized response that distinguishes
    successful lookups from external-service failures.
    """

    url = (
        "https://myvariant.info/v1/variant/"
        f"{genomic_variant}"
    )

    params = {
        "assembly": "hg38"
    }

    result = get_json(
        url,
        params=params
    )

    if result.get("status") != "success":
        return result

    return result["data"]


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

def search_dbvar_cnv(gene, chromosome, start, end):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

    params = {
        "db": "dbvar",
        "term": (
            f"GRCh38[{chromosome}] AND "
            f"{gene}[Gene Name] AND "
            f"({start}:{end}[Base Position])"
        ),
        "retmode": "json",
    }

    data = get_json(url, params=params)

    if data.get("status") != "success":
        return data

    return data["data"]["esearchresult"]["idlist"]
# ============================================================
# 4.4 SNV EVIDENCE
# ============================================================

def get_snv_evidence(record):
    """
    Build SNV evidence using generic normalization.

    Flow:
        record
          ↓
        normalize_snv()
          ↓
        VariantValidator
          ↓
        MyVariant.info
    """

    # --------------------------------------------------------
    # Normalize SNV
    # --------------------------------------------------------

    normalization = normalize_snv(record)

    if normalization.get("status") != "success":
        return {
            "status": "normalization_failed",
            "source_variant": record,
            "normalization": normalization,
        }

    transcript_hgvs = normalization.get(
        "transcript_hgvs"
    )

    if not transcript_hgvs:
        return {
            "status": "normalization_failed",
            "source_variant": record,
            "normalization": normalization,
            "message": "Transcript HGVS is missing."
        }

    # --------------------------------------------------------
    # VariantValidator
    # --------------------------------------------------------

    print("\nRunning VariantValidator...")

    validator_raw = validate_with_variantvalidator(
        transcript_hgvs
    )

    validator = extract_validation_evidence(
        validator_raw,
        transcript_hgvs
    )

    # --------------------------------------------------------
    # Stop if VariantValidator did not validate
    # --------------------------------------------------------

    if not validator.get("validated"):
        return {
            "status": "validation_failed",
            "source_variant": record,
            "normalization": normalization,
            "variantvalidator": validator,
        }

    # --------------------------------------------------------
    # Get genomic representation
    # --------------------------------------------------------

    genomic = validator.get(
        "genomic"
    )

    vcf = validator.get(
        "vcf"
    )

    genomic_variant = None

    if (
        isinstance(vcf, dict)
        and vcf.get("chromosome") is not None
        and vcf.get("position") is not None
        and vcf.get("reference") is not None
        and vcf.get("alternate") is not None
    ):
        genomic_variant = (
            f"chr{vcf['chromosome']}:"
            f"g.{vcf['position']}"
            f"{vcf['reference']}>"
            f"{vcf['alternate']}"
        )

    # --------------------------------------------------------
    # MyVariant.info
    # --------------------------------------------------------

    myvariant = {
        "found": False,
        "message": "Genomic representation unavailable."
    }

    if genomic_variant:

        print(
            "Running MyVariant.info..."
        )

        myvariant_raw = lookup_myvariant(
            genomic_variant
        )

        if myvariant_raw.get("status") == "error":
            myvariant = {
                "found": False,
                "status": "unavailable",
                "error_type": myvariant_raw.get(
                    "error_type"
                ),
                "message": myvariant_raw.get(
                    "message"
                ),
            }
        else:
            myvariant = extract_myvariant_evidence(
                myvariant_raw,
                record.get("variant")
            )

    # --------------------------------------------------------
    # Final SNV evidence
    # --------------------------------------------------------

    return {
        "status": "success",
        "source_variant": record,
        "normalization": normalization,
        "variantvalidator": validator,
        "myvariant": myvariant,
    }

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

    data = get_json(url, params=params)

    if data.get("status") != "success":
        return data

    data = data["data"] 

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

def normalize_cnv(record):
    """
    Parse a genomic CNV representation into structured coordinates.

    Example:
        chr17:g.(81936194_81936747)_(81937239_?)del
    """

    variant = record.get("variant")

    if not variant:
        return {
            "status": "error",
            "message": "CNV variant is missing."
        }

    pattern = (
    r"^chr(?P<chromosome>[0-9]+|X|Y):g\."
    r"\((?P<left_start>\d+)_(?P<left_end>\d+)\)"
    r"\s*_\s*"
    r"\((?P<right_start>\d+)_\?\)"
    r"(?P<variant_type>del|dup)$"
    )

    match = re.match(
        pattern,
        variant
    )

    if not match:
        return {
            "status": "unsupported",
            "input_variant": variant,
            "message": (
                "CNV notation could not be parsed."
            )
        }

    chromosome = match.group("chromosome")
    start = int(match.group("left_start"))
    end = int(match.group("right_start"))
    variant_type = match.group("variant_type")

    return {
        "status": "success",
        "input_variant": variant,
        "chromosome": chromosome,
        "start": start,
        "end": end,
        "variant_type": variant_type,
        "assembly": "GRCh38"
    }
def classify_cnv_match(
    report_start,
    report_end,
    candidate_start,
    candidate_end
):
    """
    Classify the relationship between the reported CNV
    coordinates and a dbVar candidate.

    Returns:
        exact     -> same start and end
        overlap   -> regions overlap but are not identical
        no_match  -> no coordinate overlap
    """

    if (
        report_start == candidate_start
        and report_end == candidate_end
    ):
        return "exact"

    if (
        report_start <= candidate_end
        and candidate_start <= report_end
    ):
        return "overlap"

    return "no_match"
def get_cnv_evidence(record):
    """
    Build dbVar evidence for a normalized CNV.

    Candidates are matched by:
    1. GRCh38 placement coordinates
    2. Structural variant type relevance
    """

    gene = record.get("gene")

    normalization = normalize_cnv(record)

    if normalization["status"] != "success":
        return normalization

    chromosome = normalization["chromosome"]
    start = normalization["start"]
    end = normalization["end"]
    variant_type = normalization["variant_type"]

    print("\nRunning dbVar...")

    ids = search_dbvar_cnv(
        gene,
        chromosome,
        start,
        end
    )

    print(
        f"dbVar candidates found: {len(ids)}"
    )

    candidates = get_dbvar_summaries(ids)

    relevant_candidates = []

    for candidate in candidates:

        # Check coordinate match on GRCh38
        coordinate_match = "no_match"

        for placement in candidate.get("placements", []):

            if placement.get("assembly") != "GRCh38.p12":
                continue

            candidate_start = placement.get("chr_start")
            candidate_end = placement.get("chr_end")

            if (
                candidate_start is None
                or candidate_end is None
            ):
                continue

            coordinate_match = classify_cnv_match(
                start,
                end,
                candidate_start,
                candidate_end
            )

            break

        if coordinate_match == "no_match":
            continue

        # Check whether the dbVar record is structurally relevant
        dbvar_types = [
            str(value).lower()
            for value in candidate.get("variant_type", [])
        ]

        if variant_type == "del":
            type_relevant = any(
                value in dbvar_types
                for value in [
                    "copy number variation",
                    "deletion",
                    "copy number loss",
                ]
            )
        elif variant_type == "dup":
            type_relevant = any(
                value in dbvar_types
                for value in [
                    "copy number variation",
                    "duplication",
                    "copy number gain",
                ]
            )
        else:
            type_relevant = True

        candidate["coordinate_match_status"] = coordinate_match
        candidate["type_relevant"] = type_relevant

        if type_relevant:
            candidate["match_status"] = coordinate_match
        else:
            candidate["match_status"] = "type_mismatch"

        relevant_candidates.append(candidate)

    return {
        "status": "success",
        "source_variant": record,
        "normalization": normalization,
        "search_region": {
            "chromosome": chromosome,
            "start": start,
            "end": end
        },
        "dbvar_candidates": relevant_candidates
    }
def resolve_snv_transcript(gene, variant):
    gene_variant = f"{gene}:{variant}"

    data = validate_with_variantvalidator(gene_variant)

    # External service failure
    if data.get("status") == "error":
        return data

    warning = data.get("validation_warning_1", {})
    warnings = warning.get("validation_warnings", [])

    transcript_text = " ".join(warnings)

    transcript_pattern = r"\b(?:NM_|NR_|ENST)\d+(?:\.\d+)?\b"
    transcripts = re.findall(transcript_pattern, transcript_text)

    transcripts = list(dict.fromkeys(transcripts))

    return {
        "status": "success" if transcripts else "partial",
        "gene": gene,
        "variant": variant,
        "transcripts": transcripts,
    }
def select_valid_snv_transcript(gene, variant, transcripts):
    """
    Select a transcript that produces a valid VariantValidator result.

    Candidates are tested in the order returned by VariantValidator.
    """

    tested = []

    for transcript in transcripts:

        transcript_hgvs = (
            f"{transcript}:{variant}"
        )

        data = validate_with_variantvalidator(
            transcript_hgvs
        )

        flag = data.get(
            "flag"
        )

        tested.append({
            "transcript": transcript,
            "flag": flag
        })

        if flag == "gene_variant":
            return {
                "status": "success",
                "selected_transcript": transcript,
                "transcript_hgvs": transcript_hgvs,
                "tested": tested
            }

    return {
        "status": "not_found",
        "selected_transcript": None,
        "transcript_hgvs": None,
        "tested": tested
    }
def normalize_snv(record):
    """
    Normalize an SNV without hardcoding a specific gene/variant.

    Transcript resolution is performed through VariantValidator.
    """

    gene = record.get("gene")
    variant = record.get("variant")

    if not gene:
        return {
            "status": "error",
            "message": "SNV gene is missing."
        }

    if not variant:
        return {
            "status": "error",
            "message": "SNV variant is missing."
        }

    # --------------------------------------------------------
    # Use transcript supplied by the report when available
    # --------------------------------------------------------

    transcript = record.get("transcript")

    if transcript:

        return {
            "status": "success",
            "input_variant": variant,
            "gene": gene,
            "transcript": transcript,
            "transcript_hgvs": (
                f"{transcript}:{variant}"
            ),
            "assembly": "GRCh38"
        }

    # --------------------------------------------------------
    # Resolve transcript dynamically
    # --------------------------------------------------------

    resolution = resolve_snv_transcript(
        gene,
        variant
    )

    if resolution["status"] != "success":

        return {
            "status": "partial",
            "input_variant": variant,
            "gene": gene,
            "transcript": None,
            "transcript_hgvs": None,
            "assembly": "GRCh38",
            "message": (
                "No transcript could be resolved "
                "automatically."
            ),
            "transcript_candidates": (
                resolution.get(
                    "transcripts",
                    []
                )
            )
        }

    transcripts = resolution[
        "transcripts"
    ]

    # Use the first candidate initially.
    # We will improve transcript selection next.
    
    selection = select_valid_snv_transcript(
        gene,
        variant,
        transcripts
    )

    if selection["status"] != "success":
        return {
            "status": "partial",
            "input_variant": variant,
            "gene": gene,
            "transcript": None,
        "transcript_hgvs": None,
        "assembly": "GRCh38",
        "message": (
            "No candidate transcript produced "
            "a valid VariantValidator result."
        ),
        "transcript_candidates": transcripts,
        "transcript_tests": selection["tested"]
    }

    selected_transcript = selection[
        "selected_transcript"
    ]

    return {
        "status": "success",
        "input_variant": variant,
        "gene": gene,
        "transcript": selected_transcript,
        "transcript_hgvs": selection[
            "transcript_hgvs"
        ],
        "assembly": "GRCh38",
        "transcript_candidates": transcripts,
        "selected_by": "VariantValidator",
        "transcript_tests": selection["tested"]
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