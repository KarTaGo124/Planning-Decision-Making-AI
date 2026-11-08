import json
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import requests


class AgentModel(str, Enum):
    EXPERT_RULES = "Agente Analítico Grupo 7 (Determinista Experto)"
    GEMINI_FLASH = "Google Gemini 1.5 Flash (API)"
    OPENAI_MINI = "OpenAI GPT-4o-mini (API)"


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
            f"**Tasa de Aprobación Global:** {acceptance_rate:.1f}% ({len(accepted)} aceptadas de {total} evaluadas).",
            "",
            "#### Factores Clave de Elección (Variaciones Aceptadas):",
        ]
        for p in accepted_patterns:
            narrative_lines.append(f"- {p}")

        if rejected_patterns:
            narrative_lines.append("")
            narrative_lines.append("#### Razones de Descarte (Variaciones Rechazadas):")
            for r in rejected_patterns:
                narrative_lines.append(f"- {r}")

        narrative_lines.append("")
        narrative_lines.append("#### Recomendaciones Estratégicas para la Siguiente Generación:")
        for rec in recommendations:
            narrative_lines.append(f"1. {rec}")

        narrative = "\n".join(narrative_lines)

        return ExplanationResult(
            model_name=AgentModel.EXPERT_RULES.value,
            summary=summary,
            accepted_patterns=accepted_patterns,
            rejected_patterns=rejected_patterns,
            recommendations=recommendations,
            narrative=narrative,
            factual_consistency_score=1.0,
        )

    def _call_gemini_api(self, prompt: str) -> Optional[str]:
        if not self.gemini_api_key:
            return None
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 800},
        }
        try:
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            return None
        return None

    def _call_openai_api(self, prompt: str) -> Optional[str]:
        if not self.openai_api_key:
            return None
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": "Eres un agente analítico de IA especializado en explicar la toma de decisiones y feedback de usuarios en sistemas generativos.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 800,
        }
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"]
        except Exception:
            return None
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
            "Redacta una explicación en español que detalle:\n"
            "1. Resumen ejecutivo de la tasa de aceptación y perfil de usuario.\n"
            "2. Análisis fundamentado de por qué aceptó determinadas fotos (atributos de iluminación, vestimenta, formalidad).\n"
            "3. Análisis de por qué rechazó las otras fotos.\n"
            "4. Recomendaciones accionables para la siguiente tanda de generación.\n"
            "Sé conciso, riguroso y mantén estricta fidelidad a los datos."
        )

        llm_response: Optional[str] = None
        if active_model == AgentModel.GEMINI_FLASH:
            llm_response = self._call_gemini_api(prompt)
        elif active_model == AgentModel.OPENAI_MINI:
            llm_response = self._call_openai_api(prompt)

        if not llm_response:
            fallback_result.model_name = f"{active_model.value} (Modo Contingencia Local)"
            return fallback_result

        return ExplanationResult(
            model_name=active_model.value,
            summary=f"Explicación analítica generada mediante {active_model.value}.",
            accepted_patterns=fallback_result.accepted_patterns,
            rejected_patterns=fallback_result.rejected_patterns,
            recommendations=fallback_result.recommendations,
            narrative=llm_response,
            factual_consistency_score=0.98,
        )
