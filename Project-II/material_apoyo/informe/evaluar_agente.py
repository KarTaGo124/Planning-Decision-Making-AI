import json
import os
import random
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

for env_path in (PROJECT_ROOT / ".env", PROJECT_ROOT.parent / ".env"):
    load_dotenv(env_path)

from src.agent import AgentModel, ExplanationAgent
from src.config import get_package, get_preset

RUNS = int(sys.argv[1]) if len(sys.argv) > 1 else 10
OUTPUT = Path(__file__).resolve().parent / "datos" / "evaluacion_agente.json"
NOTES_ACCEPTED = ["se ve serio y profesional", "buena luz", "me gusta el fondo", ""]
NOTES_REJECTED = ["muy informal para mi", "el fondo se ve falso", "no me reconozco", ""]


def build_decisions(rng: random.Random) -> list:
    decisions = []
    for preset_id in get_package("package_corporate_mix").preset_ids:
        preset = get_preset(preset_id)
        accepted = rng.random() < 0.6
        decisions.append(
            {
                "variation_id": f"eval_{preset_id}",
                "title": preset.title,
                "platform": preset.platform.value,
                "formality": preset.formality.value,
                "accepted": accepted,
                "rating": rng.randint(4, 5) if accepted else rng.randint(1, 3),
                "recommended_lighting": preset.recommended_lighting,
                "recommended_background": preset.recommended_background,
                "user_notes": rng.choice(NOTES_ACCEPTED if accepted else NOTES_REJECTED),
            }
        )
    return decisions


def main() -> None:
    rng = random.Random(7)
    rows = []
    for run in range(RUNS):
        decisions = build_decisions(rng)
        rules = ExplanationAgent().explain_decisions(decisions, AgentModel.EXPERT_RULES)
        agent = ExplanationAgent()
        start = time.time()
        llm = agent.explain_decisions(decisions, AgentModel.GEMINI_FLASH)
        elapsed = time.time() - start
        rows.append(
            {
                "run": run + 1,
                "accepted": sum(d["accepted"] for d in decisions),
                "rejected": sum(not d["accepted"] for d in decisions),
                "rules_fidelity": rules.factual_consistency_score,
                "llm_model": llm.model_name,
                "llm_used_fallback": "Contingencia" in llm.model_name,
                "llm_fidelity": llm.factual_consistency_score,
                "llm_seconds": round(elapsed, 2),
                "llm_narrative": llm.narrative,
            }
        )
        print(f"corrida {run + 1}: reglas={rules.factual_consistency_score} llm={llm.factual_consistency_score} {elapsed:.1f}s {llm.model_name}")

    llm_rows = [r for r in rows if not r["llm_used_fallback"]]
    summary = {
        "runs": RUNS,
        "llm_successful_runs": len(llm_rows),
        "rules_mean_fidelity": round(sum(r["rules_fidelity"] for r in rows) / len(rows), 3),
        "llm_mean_fidelity": round(sum(r["llm_fidelity"] for r in llm_rows) / len(llm_rows), 3) if llm_rows else None,
        "llm_min_fidelity": min((r["llm_fidelity"] for r in llm_rows), default=None),
        "llm_perfect_runs": sum(r["llm_fidelity"] == 1.0 for r in llm_rows),
        "llm_mean_seconds": round(sum(r["llm_seconds"] for r in llm_rows) / len(llm_rows), 2) if llm_rows else None,
        "llm_max_seconds": max((r["llm_seconds"] for r in llm_rows), default=None),
        "date": time.strftime("%Y-%m-%d"),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps({"summary": summary, "runs": rows}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
