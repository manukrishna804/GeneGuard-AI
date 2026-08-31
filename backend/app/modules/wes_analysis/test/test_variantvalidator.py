import requests


def validate_variant(hgvs):

    url = (
        "https://rest.variantvalidator.org/"
        "VariantValidator/variantvalidator/"
        "GRCh38/"
        f"{hgvs}/"
        "all"
    )

    response = requests.get(
        url,
        headers={
            "Accept": "application/json"
        },
        timeout=30
    )

    print("HTTP status:", response.status_code)

    print("\nResponse:")
    print(response.text)

    response.raise_for_status()

    return response.json()


# ==========================================
# TEST
# ==========================================

hgvs = "NM_001844.4:c.3559C>T"

result = validate_variant(hgvs)

print("\n==========================================")
print("VARIANTVALIDATOR RESULT")
print("==========================================")

print(result)