import json
import math
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass
class MetricsSummary:
    total_evaluated: int
    accepted_count: int
    rejected_count: int
    acceptance_rate_percent: float
    average_rating: float
    average_latency_seconds: float
    platform_distribution: Dict[str, int]
    formality_distribution: Dict[str, int]
    visual_diversity_score: float
    explanation_fidelity_score: float


def compute_diversity_score(decisions: List[Dict[str, Any]]) -> float:
    if not decisions:
        return 0.0
    formalities = [d.get("formality", "general") for d in decisions]
    total = len(formalities)
    counts = {}
    for f in formalities:
        counts[f] = counts.get(f, 0) + 1

    entropy = 0.0
    for count in counts.values():
        p = count / total
        entropy -= p * math.log2(p)

    max_entropy = math.log2(len(counts)) if len(counts) > 1 else 1.0
    normalized_diversity = entropy / max_entropy if max_entropy > 0 else 0.5
    return round(normalized_diversity, 3)


def evaluate_explanation_fidelity(narrative: str, decisions: List[Dict[str, Any]]) -> float:
    if not decisions or not narrative:
        return 1.0

    accepted = [d for d in decisions if d.get("accepted") is True]
    rejected = [d for d in decisions if d.get("accepted") is False]

    checks = 0
    passed = 0

    if accepted:
        checks += 1
        acc_platform = accepted[0].get("platform", "")
        if acc_platform.lower() in narrative.lower():
            passed += 1

    if rejected:
        checks += 1
        rej_formality = rejected[0].get("formality", "")
        if rej_formality.lower() in narrative.lower() or "rechaz" in narrative.lower() or "descarte" in narrative.lower():
            passed += 1

    checks += 1
    total_str = str(len(decisions))
    if total_str in narrative or "100" in narrative or "%" in narrative:
        passed += 1

    return round(passed / checks if checks > 0 else 1.0, 3)


def compute_metrics(decisions: List[Dict[str, Any]], explanation_narrative: Optional[str] = None) -> MetricsSummary:
    if not decisions:
        return MetricsSummary(
            total_evaluated=0,
            accepted_count=0,
            rejected_count=0,
            acceptance_rate_percent=0.0,
            average_rating=0.0,
            average_latency_seconds=0.0,
            platform_distribution={},
            formality_distribution={},
            visual_diversity_score=0.0,
            explanation_fidelity_score=1.0,
        )

    total = len(decisions)
    accepted = [d for d in decisions if d.get("accepted") is True]
    rejected = [d for d in decisions if d.get("accepted") is False]

    acc_rate = (len(accepted) / total) * 100.0

    ratings = [d.get("rating", 3) for d in decisions if d.get("rating") is not None]
    avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else 0.0

    latencies = [d.get("latency_seconds", 2.0) for d in decisions if d.get("latency_seconds") is not None]
    avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else 2.0

    plat_dist: Dict[str, int] = {}
    for d in decisions:
        p = d.get("platform", "Otro")
        plat_dist[p] = plat_dist.get(p, 0) + 1

    form_dist: Dict[str, int] = {}
    for d in decisions:
        f = d.get("formality", "Otro")
        form_dist[f] = form_dist.get(f, 0) + 1

    diversity = compute_diversity_score(decisions)
    fidelity = evaluate_explanation_fidelity(explanation_narrative or "", decisions)

    return MetricsSummary(
        total_evaluated=total,
        accepted_count=len(accepted),
        rejected_count=len(rejected),
        acceptance_rate_percent=round(acc_rate, 2),
        average_rating=avg_rating,
        average_latency_seconds=avg_latency,
        platform_distribution=plat_dist,
        formality_distribution=form_dist,
        visual_diversity_score=diversity,
        explanation_fidelity_score=fidelity,
    )


def save_decisions_json(decisions: List[Dict[str, Any]], filepath: str) -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(decisions, f, indent=2, ensure_ascii=False)


def load_decisions_json(filepath: str) -> List[Dict[str, Any]]:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []
