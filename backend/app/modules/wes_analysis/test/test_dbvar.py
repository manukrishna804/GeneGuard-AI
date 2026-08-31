import requests


# ==========================================
# STAGE 4.3: GET dbVar SUMMARIES
# ==========================================

def get_dbvar_summaries(ids):

    url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        "esummary.fcgi"
    )

    params = {
        "db": "dbvar",
        "id": ",".join(ids),
        "retmode": "json"
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    print("HTTP status:", response.status_code)

    response.raise_for_status()

    return response.json()


# ==========================================
# THE 4 RECORDS WE FOUND
# ==========================================

ids = [
    "55275186",
    "55156317",
    "55155265",
    "16822522"
]


# ==========================================
# LOOK THEM UP
# ==========================================

result = get_dbvar_summaries(ids)


# ==========================================
# PRINT RAW RESULT
# ==========================================

print("\n==========================================")
print("dbVar SUMMARIES")
print("==========================================")

print(result)