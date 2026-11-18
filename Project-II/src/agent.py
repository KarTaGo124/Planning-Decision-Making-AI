import json
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import requests

from src.evaluator import evaluate_explanation_fidelity

DEFAULT_GEMINI_MODEL = "gemini-3.5-flash-lite"
GEMINI_FALLBACK_MODELS = ("gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-flash-lite-latest", "gemini-3.8-flash")
GEMINI_ATTEMPTS_PER_MODEL = 2
GEMINI_RETRY_DELAY_SECONDS = 2
RETRYABLE_STATUS_CODES = (429, 500, 502, 503, 504)
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
API_TIMEOUT_SECONDS = 25


class AgentModel(str, Enum):
    EXPERT_RULES = "Agente Analítico Grupo 7 (Determinista Experto)"
    GEMINI_FLASH = "Google Gemini Flash (API)"
    OPENAI_MINI = "OpenAI GPT (API)"


@dataclass
class ExplanationResult:
    model_name: str
    summary: str
    accepted_patterns: List[str]
    rejected_patterns: List[str]
    recommendations: List[str]
    narrative: str
    factual_consistency_score: float


class ExplanationAgent:
    def __init__(self, preferred_model: AgentModel = AgentModel.EXPERT_RULES):
        self.preferred_model = preferred_model
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.gemini_model = os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)
        self.openai_model = os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
        self.last_api_error = ""
        self.last_model_used = ""

    def _generate_expert_rule_explanation(self, decisions: List[Dict[str, Any]]) -> ExplanationResult:
        if not decisions:
            return ExplanationResult(
                model_name=AgentModel.EXPERT_RULES.value,
                summary="No se han registrado decisiones suficientes para generar una explicación.",
                accepted_patterns=[],
                rejected_patterns=[],
                recommendations=["Evalúe y marque al menos 2 variaciones para obtener un análisis detallado."],
                narrative="El registro de retroalimentación se encuentra vacío. Seleccione 'Aceptar' o 'Rechazar' en las imágenes generadas para activar la síntesis analítica.",
                factual_consistency_score=1.0,
            )

        accepted = [d for d in decisions if d.get("accepted") is True]
        rejected = [d for d in decisions if d.get("accepted") is False]
        total = len(decisions)
        acceptance_rate = (len(accepted) / total) * 100 if total > 0 else 0

        acc_platforms = [d.get("platform", "General") for d in accepted]
        acc_formalities = [d.get("formality", "No especificado") for d in accepted]
        rej_formalities = [d.get("formality", "No especificado") for d in rejected]

        fav_platform = max(set(acc_platforms), key=acc_platforms.count) if acc_platforms else "Ninguna"
        fav_formality = max(set(acc_formalities), key=acc_formalities.count) if acc_formalities else "No concluyente"

        accepted_patterns: List[str] = []
        if accepted:
            accepted_patterns.append(
                f"Preferencia por la plataforma '{fav_platform}' con un nivel de formalidad predominante de tipo '{fav_formality}'."
            )
            lighting_styles = [d.get("recommended_lighting") for d in accepted if d.get("recommended_lighting")]
            if lighting_styles:
                fav_light = max(set(lighting_styles), key=lighting_styles.count)
                accepted_patterns.append(f"Inclinación favorable hacia esquemas de iluminación: '{fav_light}'.")

        rejected_patterns: List[str] = []
        if rejected:
            if rej_formalities:
                disliked_formality = max(set(rej_formalities), key=rej_formalities.count)
                rejected_patterns.append(
                    f"Mayor tasa de descarte en configuraciones con formalidad '{disliked_formality}'."
                )
            rejected_notes = [d.get("user_notes") for d in rejected if d.get("user_notes")]
            if rejected_notes:
                rejected_patterns.append(f"Observaciones del usuario en descartes: '{rejected_notes[0]}'.")
            else:
                rejected_patterns.append("Descartes orientados a estilos que se alejan del objetivo profesional inmediato.")

        recommendations: List[str] = [
            f"Concentrar las siguientes iteraciones en el segmento '{fav_platform}' con vestimenta '{fav_formality}'.",
            "Mantener la fidelidad de rasgos faciales mediante ControlNet Canny en umbrales de 100-200.",
            "Probar ajustes menores en el prompt libre especificando texturas de tela o color de terno.",
        ]

        summary = (
            f"El usuario evaluó un total de {total} variaciones con una tasa de aceptación del {acceptance_rate:.1f}%. "
            f"Se evidencia una marcada inclinación hacia estilos para {fav_platform} con formalidad {fav_formality}."
        )

        narrative_lines = [
            "### Resumen Analítico de Decisiones del Usuario",
            "",
            self._build_decision_record(decisions),
        ]

        if accepted_patterns:
            narrative_lines.append("")
            narrative_lines.append("#### Patrones en las elecciones")
            for p in accepted_patterns:
                narrative_lines.append(f"- {p}")

        if rejected_patterns:
            narrative_lines.append("")
            narrative_lines.append("#### Patrones en los descartes")
            for r in rejected_patterns:
                narrative_lines.append(f"- {r}")

        narrative_lines.append("")
        narrative_lines.append("#### Recomendaciones para la siguiente generación")
        for position, rec in enumerate(recommendations, start=1):
            narrative_lines.append(f"{position}. {rec}")

        narrative = "\n".join(narrative_lines)

        return ExplanationResult(
            model_name=AgentModel.EXPERT_RULES.value,
            summary=summary,
            accepted_patterns=accepted_patterns,
            rejected_patterns=rejected_patterns,
            recommendations=recommendations,
            narrative=narrative,
            factual_consistency_score=evaluate_explanation_fidelity(narrative, decisions),
        )

    def _format_decision_line(self, decision: Dict[str, Any]) -> str:
        line = f"- {decision.get('title', decision.get('variation_id', 'Variación'))}"
        rating = decision.get("rating")
        if rating is not None:
            line += f" (calificación {rating}/5)"
        notes = str(decision.get("user_notes") or "").strip()
        if notes:
            line += f" «{notes}»"
        return line

    def _build_decision_record(self, decisions: List[Dict[str, Any]]) -> str:
        accepted = [d for d in decisions if d.get("accepted") is True]
        rejected = [d for d in decisions if d.get("accepted") is False]
        total = len(accepted) + len(rejected)
        rate = (len(accepted) / total) * 100 if total > 0 else 0.0

        lines = [
            f"**Resultado:** {total} variaciones evaluadas, con una tasa de aprobación de {rate:.1f}%.",
            "",
            f"#### Variaciones aceptadas ({len(accepted)})",
        ]
        lines.extend(self._format_decision_line(d) for d in accepted)
        if not accepted:
            lines.append("- Ninguna.")

        lines.append("")
        lines.append(f"#### Variaciones rechazadas ({len(rejected)})")
        lines.extend(self._format_decision_line(d) for d in rejected)
        if not rejected:
            lines.append("- Ninguna.")

        return "\n".join(lines)

    def _gemini_candidates(self) -> List[str]:
        return [self.gemini_model] + [m for m in GEMINI_FALLBACK_MODELS if m != self.gemini_model]

    def _request_gemini(self, model_id: str, prompt: str) -> Tuple[Optional[str], bool]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent"
        headers = {"x-goog-api-key": self.gemini_api_key, "Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 4096},
        }
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=API_TIMEOUT_SECONDS)
        except requests.Timeout:
            self.last_api_error = f"{model_id}: sin respuesta en {API_TIMEOUT_SECONDS} s"
            return None, False
        except Exception as exc:
            self.last_api_error = f"{model_id}: {type(exc).__name__}: {exc}"[:200]
            return None, False

        if resp.status_code != 200:
            try:
                message = resp.json().get("error", {}).get("message", "")
            except Exception:
                message = resp.text
            self.last_api_error = f"{model_id} respondió {resp.status_code}: {message[:160]}"
            return None, resp.status_code in RETRYABLE_STATUS_CODES

        try:
            candidate = resp.json()["candidates"][0]
        except Exception:
            self.last_api_error = f"{model_id}: respuesta sin candidatos"
            return None, False
        parts = candidate.get("content", {}).get("parts", [])
        text = "".join(part.get("text", "") for part in parts if not part.get("thought")).strip()
        if not text:
            self.last_api_error = f"{model_id} no devolvió texto (finishReason: {candidate.get('finishReason')})"
            return None, False
        return text, False

    def _call_gemini_api(self, prompt: str) -> Optional[str]:
        self.last_model_used = ""
        if not self.gemini_api_key:
            self.last_api_error = "falta GEMINI_API_KEY"
            return None
        for model_id in self._gemini_candidates():
            for attempt in range(GEMINI_ATTEMPTS_PER_MODEL):
                text, retryable = self._request_gemini(model_id, prompt)
                if text:
                    self.last_model_used = model_id
                    return text
                if not retryable:
                    break
                if attempt + 1 < GEMINI_ATTEMPTS_PER_MODEL:
                    time.sleep(GEMINI_RETRY_DELAY_SECONDS * (attempt + 1))
        return None

    def _call_openai_api(self, prompt: str) -> Optional[str]:
        if not self.openai_api_key:
            self.last_api_error = "falta OPENAI_API_KEY"
            return None
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.openai_model,
            "messages": [
                {
                    "role": "system",
                    "content": "Eres un agente analítico de IA especializado en explicar la toma de decisiones y feedback de usuarios en sistemas generativos.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 1500,
        }
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=API_TIMEOUT_SECONDS)
            if resp.status_code != 200:
                self.last_api_error = f"OpenAI respondió {resp.status_code}: {resp.text[:200]}"
                return None
            return resp.json()["choices"][0]["message"]["content"]
        except Exception as exc:
            self.last_api_error = f"OpenAI: {type(exc).__name__}: {exc}"[:200]
            return None

    def explain_decisions(
        self,
        decisions: List[Dict[str, Any]],
        model_choice: Optional[AgentModel] = None,
    ) -> ExplanationResult:
        active_model = model_choice or self.preferred_model
        fallback_result = self._generate_expert_rule_explanation(decisions)

        if active_model == AgentModel.EXPERT_RULES:
            return fallback_result

        decisions_summary_str = json.dumps(
            [
                {
                    "id": d.get("variation_id"),
                    "titulo": d.get("title"),
                    "plataforma": d.get("platform"),
                    "formalidad": d.get("formality"),
                    "aceptada": d.get("accepted"),
                    "calificacion": d.get("rating"),
                    "iluminacion": d.get("recommended_lighting"),
                    "fondo": d.get("recommended_background"),
                    "notas": d.get("user_notes"),
                }
                for d in decisions
            ],
            indent=2,
            ensure_ascii=False,
        )

        prompt = (
            "Analiza las siguientes decisiones de un usuario frente a variaciones de fotos profesionales generadas por IA:\n"
            f"{decisions_summary_str}\n\n"
            "Redacta una explicación en español con estas secciones, en este orden:\n"
            "1. Cuántas variaciones se evaluaron, cuántas fueron aceptadas y cuántas rechazadas.\n"
            "2. 'Variaciones aceptadas': lista cada una por su título exacto y explica por qué se aceptó (iluminación, vestimenta, formalidad, notas del usuario).\n"
            "3. 'Variaciones rechazadas': lista cada una por su título exacto y explica por qué se rechazó.\n"
            "4. Recomendaciones accionables para la siguiente tanda de generación.\n"
            "Usa solo los datos entregados, no inventes preferencias y no omitas ninguna variación."
        )

        llm_response: Optional[str] = None
        model_id = ""
        if active_model == AgentModel.GEMINI_FLASH:
            llm_response = self._call_gemini_api(prompt)
            model_id = self.last_model_used
        elif active_model == AgentModel.OPENAI_MINI:
            model_id = self.openai_model
            llm_response = self._call_openai_api(prompt)

        if not llm_response:
            fallback_result.model_name = f"{active_model.value} (Modo Contingencia Local: {self.last_api_error})"
            return fallback_result

        return ExplanationResult(
            model_name=f"{active_model.value} · {model_id}",
            summary=f"Explicación analítica generada mediante {active_model.value}.",
            accepted_patterns=fallback_result.accepted_patterns,
            rejected_patterns=fallback_result.rejected_patterns,
            recommendations=fallback_result.recommendations,
            narrative=(
                f"{self._build_decision_record(decisions)}\n\n"
                f"#### Explicación generada por {active_model.value}\n\n"
                f"{llm_response}"
            ),
            factual_consistency_score=evaluate_explanation_fidelity(llm_response, decisions),
        )
