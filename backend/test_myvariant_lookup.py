
from app.modules.pharmacogenomics.services.variant_annotator import (
    annotate_variant,
)

result = annotate_variant(
    chromosome="10",
    position=96521657,
    reference="G",
    alternate="A",
)

print(result)
