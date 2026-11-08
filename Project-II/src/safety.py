import re
import unicodedata
from dataclasses import dataclass
from typing import List, Optional, Pattern, Tuple


@dataclass
class SafetyCheckResult:
    is_safe: bool
    violation_category: Optional[str] = None
    violation_term: Optional[str] = None
    warning_message: Optional[str] = None


PROHIBITED_TERMS: List[Tuple[str, str]] = [
    ("sin ropa", "desnudez"),
    ("desnudo", "desnudez"),
    ("desnuda", "desnudez"),
    ("desnudez", "desnudez"),
    ("desvestido", "desnudez"),
    ("desvestida", "desnudez"),
    ("en toalla", "ropa inapropiada"),
    ("en ropa interior", "ropa inapropiada"),
    ("ropa interior", "ropa inapropiada"),
    ("lenceria", "ropa inapropiada"),
    ("lencería", "ropa inapropiada"),
    ("bikini", "ropa inapropiada"),
    ("traje de bano", "ropa inapropiada"),
    ("traje de baño", "ropa inapropiada"),
    ("topless", "desnudez"),
    ("nudity", "desnudez"),
    ("nude", "desnudez"),
    ("naked", "desnudez"),
    ("undressed", "desnudez"),
    ("nsfw", "contenido explícito"),
    ("erotico", "contenido explícito"),
    ("erótico", "contenido explícito"),
    ("sexual", "contenido explícito"),
    ("porn", "contenido explícito"),
    ("porno", "contenido explícito"),
    ("sensual explicito", "contenido explícito"),
    ("violencia", "violencia"),
    ("arma", "violencia"),
    ("pistola", "violencia"),
    ("cuchillo", "violencia"),
    ("sangre", "violencia"),
    ("drogas", "sustancias ilícitas"),
    ("droga", "sustancias ilícitas"),
    ("odio", "discurso de odio"),
    ("racismo", "discurso de odio"),
]

PROHIBITED_PATTERNS: List[Tuple[Pattern[str], str]] = [
    (re.compile(r"\bsin\s+(ropa|prendas?|vestir)\b", re.IGNORECASE), "desnudez"),
    (re.compile(r"\bquitar?(le)?\s+(la\s+)?ropa\b", re.IGNORECASE), "desnudez"),
    (re.compile(r"\bno\s+clothes\b", re.IGNORECASE), "desnudez"),
    (re.compile(r"\bwithout\s+clothes\b", re.IGNORECASE), "desnudez"),
    (re.compile(r"\btake\s+off\s+clothes\b", re.IGNORECASE), "desnudez"),
]


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    cleaned = "".join(c for c in normalized if not unicodedata.combining(c))
    return cleaned.lower()


def check_prompt_safety(prompt: Optional[str]) -> SafetyCheckResult:
    if not prompt or not prompt.strip():
        return SafetyCheckResult(is_safe=True)

    normalized_prompt = normalize_text(prompt)

    for pattern, category in PROHIBITED_PATTERNS:
        match = pattern.search(normalized_prompt)
        if match:
            return SafetyCheckResult(
                is_safe=False,
                violation_category=category,
                violation_term=match.group(0),
                warning_message=(
                    f"La solicitud fue bloqueada por infringir las directrices éticas del sistema "
                    f"(Categoría: {category.capitalize()}). No se permite la generación o modificación "
                    f"de imágenes profesionales con términos alusivos a '{match.group(0)}'."
                ),
            )

    for term, category in PROHIBITED_TERMS:
        norm_term = normalize_text(term)
        pattern = rf"\b{re.escape(norm_term)}\b"
        if re.search(pattern, normalized_prompt):
            return SafetyCheckResult(
                is_safe=False,
                violation_category=category,
                violation_term=term,
                warning_message=(
                    f"La solicitud fue bloqueada por infringir las directrices éticas del sistema "
                    f"(Categoría: {category.capitalize()}). Se detectó el término no profesional: '{term}'."
                ),
            )

    return SafetyCheckResult(is_safe=True)
