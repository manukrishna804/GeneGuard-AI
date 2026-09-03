import requests


def get_canonical_variant(spdi):

    url = (
        "https://api.ncbi.nlm.nih.gov/variation/v0/"
        f"spdi/{spdi}/canonical"
    )

    response = requests.get(
        url,
        timeout=30
    )

    print("HTTP status:", response.status_code)
    print("Response:", response.text)

    response.raise_for_status()

    return response.json()


# ==========================================
# TEST
# ==========================================

spdi = "NC_000012.12:47976000:G:A"

result = get_canonical_variant(spdi)

print("\nParsed result:")
print(result)