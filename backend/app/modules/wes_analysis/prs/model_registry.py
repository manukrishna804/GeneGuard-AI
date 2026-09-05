from pathlib import Path


PRS_MODELS = {
    "Type 2 diabetes": {
        "pgs_id": "PGS005336",
        "path": Path(
            "app/modules/wes_analysis/prs/models/PGS005336.txt.gz"
        ),
        "match_type": "position",
    },

    "CAD": {
        "pgs_id": "PGS000019",
        "path": Path(
            "app/modules/wes_analysis/prs/models/PGS000019.txt.gz"
        ),
        "match_type": "rsid",
    },

    "Hypertension": {
        "pgs_id": "PGS004525",
        "path": Path(
            "app/modules/wes_analysis/prs/models/PGS004525.txt.gz"
        ),
        "match_type": "rsid",
    },

    "Alzheimer's disease": {
        "pgs_id": "PGS002249",
        "path": Path(
            "app/modules/wes_analysis/prs/models/PGS002249.txt.gz"
        ),
        "match_type": "rsid",
    },

    "Breast Cancer": {
        "pgs_id": "PGS004511",
        "path": Path(
            "app/modules/wes_analysis/prs/models/PGS004511.txt.gz"
        ),
        "match_type": "rsid",
    },
}