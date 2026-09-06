from pathlib import Path


PRS_MODELS = {
    "Type 2 diabetes": {
        "pgs_id": "PGS005336",
        "path": Path(
            "app/modules/wes_analysis/prs/models/"
            "PGS005336.txt.gz"
        ),
        "match_type": "position",
        "published_variant_count": 1297046,
        "development_limit": 5000,
    },

    "CAD": {
        "pgs_id": "PGS000019",
        "path": Path(
            "app/modules/wes_analysis/prs/models/"
            "PGS000019.txt.gz"
        ),
        "match_type": "rsid",
        "published_variant_count": 192,
        "development_limit": 192,
    },

    "Hypertension": {
        "pgs_id": "PGS003020",
        "path": Path(
            "app/modules/wes_analysis/prs/models/"
            "PGS003020.txt.gz"
        ),
        "match_type": "position",
        "published_variant_count": 24,
        "development_limit": 24,
    },

    "Alzheimer's disease": {
        "pgs_id": "PGS000025",
        "path": Path(
            "app/modules/wes_analysis/prs/models/"
            "PGS000025.txt.gz"
        ),
        "match_type": "rsid",
        "published_variant_count": 19,
        "development_limit": 19,
    },

    "Breast Cancer": {
        "pgs_id": "PGS000004",
        "path": Path(
            "app/modules/wes_analysis/prs/models/"
            "PGS000004.txt.gz"
        ),
        "match_type": "position",
        "published_variant_count": 313,
        "development_limit": 313,
    },
}