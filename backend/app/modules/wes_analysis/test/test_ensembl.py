import requests


def recode_variant(hgvs):
    url = "https://rest.ensembl.org/variant_recoder/human"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "ids": [hgvs]
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=30
    )

    print("HTTP status:", response.status_code)
    print("Response body:", response.text)

    response.raise_for_status()

    return response.json()


# ==========================================
# TEST
# ==========================================

hgvs = "ENST00000380518.8:c.3559C>T"

result = recode_variant(hgvs)

print("\nParsed response:")
print(result)