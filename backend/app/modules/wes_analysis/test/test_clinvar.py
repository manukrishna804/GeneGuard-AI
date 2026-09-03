import requests


def search_clinvar(term):

    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

    params = {
        "db": "clinvar",
        "term": term,
        "retmode": "json",
        "retmax": 50
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


# ==========================================
# TEST ACTUAL MEDGENOME VARIANT
# ==========================================

result = search_clinvar(
    "COL2A1 p.Pro1187Ser"
)

print("ClinVar response:")
print(result)

print("\nCount:")
print(result["esearchresult"]["count"])

print("\nIDs:")
print(result["esearchresult"]["idlist"])