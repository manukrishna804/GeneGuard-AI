import requests


# ==========================================
# CNV LOOKUP TEST
# ==========================================

def lookup_cnv(variant):

    url = f"https://myvariant.info/v1/variant/{variant}"

    params = {
        "assembly": "hg38"
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    print("HTTP status:", response.status_code)
    print("\nResponse:")
    print(response.text)

    response.raise_for_status()

    return response.json()


# ==========================================
# ACTUAL MEDGENOME CNV
# ==========================================

variant = "chr17:g.(81936194_81936747)_(81937239_?)del"

result = lookup_cnv(variant)

print("\n==========================================")
print("CNV RESULT")
print("==========================================")

print(result)