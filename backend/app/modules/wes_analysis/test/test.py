from backend.app.modules.wes_analysis.test.variant_lookup import get_variant_evidence

print("=== BRCA1 (known, should be FOUND) ===")
r1 = get_variant_evidence("BRCA1", "c.68_69delAG")
print(r1.to_dict())

print("=== COL2A1 (real report case, should be NOT_FOUND both) ===")
r2 = get_variant_evidence("COL2A1", "c.3559C>T", chrom="12", pos="47976001", ref="G", alt="A")
print(r2.to_dict())