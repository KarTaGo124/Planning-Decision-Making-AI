import json
import math
import re
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


ACCEPT_STEM = "acept"
REJECT_STEM = "rechaz"


NEGATED_ACCEPT = re.compile(r"\bno\s+(?:fue\s+|se\s+|ha\s+sido\s+|era\s+)?acept\w*")
NEGATED_REJECT = re.compile(r"\bno\s+(?:fue\s+|se\s+|ha\s+sido\s+|era\s+)?rechaz\w*")


def _strip_quoted_notes(text: str) -> str:
    text = re.sub(r"«[^»]*»", "", text.lower())
    text = NEGATED_ACCEPT.sub("rechazada", text)
    return NEGATED_REJECT.sub("aceptada", text)


def _polarity_before(text: str, position: int) -> Optional[bool]:
    preceding = text[:position]
    last_accept = preceding.rfind(ACCEPT_STEM)
    last_reject = preceding.rfind(REJECT_STEM)
    if last_accept < 0 and last_reject < 0:
        return None
    return last_accept > last_reject


def _title_matches_decision(text: str, title: str, accepted: bool) -> bool:
    start = 0
    while True:
        position = text.find(title, start)
        if position < 0:
            return False
        if _polarity_before(text, position) is accepted:
            return True
        start = position + len(title)


SPANISH_NUMBER_WORDS = {
    0: ("cero", "ninguna", "ninguno"),
    1: ("una", "uno", "un"),
    2: ("dos",),
    3: ("tres",),
    4: ("cuatro",),
    5: ("cinco",),
    6: ("seis",),
    7: ("siete",),
}


def _states_count(text: str, value: int) -> bool:
    if re.search(rf"(?<!\d){value}(?!\d)", text):
        return True
    return any(re.search(rf"\b{word}\b", text) for word in SPANISH_NUMBER_WORDS.get(value, ()))


def evaluate_explanation_fidelity(narrative: str, decisions: List[Dict[str, Any]]) -> float:
    voted = [d for d in decisions if isinstance(d.get("accepted"), bool)]
    if not voted:
        return 1.0
    if not narrative:
        return 0.0

    text = _strip_quoted_notes(narrative).lower()
    accepted_count = sum(1 for d in voted if d["accepted"])
    rejected_count = len(voted) - accepted_count

    checks = len(voted) + 3
    passed = 0

    for d in voted:
        title = str(d.get("title", "")).lower()
        if title and _title_matches_decision(text, title, d["accepted"]):
            passed += 1

    for value in (len(voted), accepted_count, rejected_count):
        if _states_count(text, value):
            passed += 1

    return round(passed / checks, 3)


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

    latencies = [d["latency_seconds"] for d in decisions if d.get("latency_seconds") is not None]
    avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else 0.0

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
