from typing import List


def prs_to_score_100(
    raw_prs: float,
    reference_scores: List[float],
) -> float:
    """
    Convert a raw PRS to a 0-100 percentile-style score
    using a reference PRS distribution.

    Returns a value from 0 to 100.
    """

    if not reference_scores:
        raise ValueError("Reference PRS scores are required.")

    reference_scores = sorted(reference_scores)

    count_below_or_equal = sum(
        score <= raw_prs
        for score in reference_scores
    )

    percentile = (
        count_below_or_equal
        / len(reference_scores)
    ) * 100

    return round(
        max(0.0, min(100.0, percentile)),
        2,
    )