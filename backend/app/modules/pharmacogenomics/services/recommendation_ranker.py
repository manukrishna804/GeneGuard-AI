from typing import Any, Dict, List


def get_actionability_rank(actionability: str) -> int:
    act_lower = actionability.lower()
    if any(keyword in act_lower for keyword in ["contraindicated", "fatal", "severe toxicity", "alternative recommended", "boxed warning"]):
        return 1
    if any(keyword in act_lower for keyword in ["major dose", "major toxicity"]):
        return 2
    if any(keyword in act_lower for keyword in ["moderate dose", "dose adjustment", "monitor"]):
        return 3
    return 4


def rank_recommendations(recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Stage 9: Sort and assign rank priority to all generated recommendations.
    """
    for item in recommendations:
        actionability = item.get("actionability", "")
        rank = get_actionability_rank(actionability)
        item["rank_priority"] = rank
        
    # Sort by rank_priority (1 is highest priority), then alphabetically by drug
    sorted_recs = sorted(
        recommendations, 
        key=lambda r: (r.get("rank_priority", 4), r.get("drug", ""))
    )
    
    return sorted_recs
