import json
import os
import re
import sys
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
import streamlit as st
from dotenv import load_dotenv
from PIL import Image, ImageOps

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

for env_path in (PROJECT_ROOT / ".env", PROJECT_ROOT.parent / ".env"):
    load_dotenv(env_path)

from src.agent import AgentModel, ExplanationAgent
from src.config import (
    PRESET_PACKAGES,
    STYLE_PRESETS,
    get_all_packages,
    get_all_presets,
    get_package,
    get_preset,
)
from src.evaluator import compute_metrics, load_decisions_json, save_decisions_json
from src.generator import EngineMode, GeneratedVariation, GenerationEngine
from src.safety import check_prompt_safety

st.set_page_config(
    page_title="Retratos profesionales, Grupo 7",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
DECISIONS_FILEPATH = str(DATA_PROCESSED_DIR / "user_decisions.json")
SESSIONS_DIR = DATA_PROCESSED_DIR / "sessions"
GENERATED_DIR = DATA_PROCESSED_DIR / "generated"


def initialize_session_state() -> None:
    if "variations" not in st.session_state:
        st.session_state.variations = []
    if "decisions" not in st.session_state:
        existing = load_decisions_json(DECISIONS_FILEPATH)
        st.session_state.decisions = {d["variation_id"]: d for d in existing} if existing else {}
    if "agent_explanation" not in st.session_state:
        st.session_state.agent_explanation = None
    if "engine" not in st.session_state:
        st.session_state.engine = GenerationEngine(mode=EngineMode.LOCAL)
    if "gpu_backend_url" not in st.session_state:
        st.session_state.gpu_backend_url = os.getenv("GPU_SERVER_URL", "")
    if "gpu_connected" not in st.session_state:
        st.session_state.gpu_connected = False
    if "gpu_device_name" not in st.session_state:
        st.session_state.gpu_device_name = ""
    if "latency_by_variation" not in st.session_state:
        st.session_state.latency_by_variation = {}
    if "last_archived_session" not in st.session_state:
        st.session_state.last_archived_session = ""


initialize_session_state()


def build_decision_record(
    var: GeneratedVariation,
    accepted: bool,
    previous: Dict[str, Any],
    default_rating: int,
    participant_code: str,
) -> Dict[str, Any]:
    return {
        "variation_id": var.variation_id,
        "preset_id": var.preset_id,
        "title": var.title,
        "platform": var.platform,
        "formality": var.formality,
        "accepted": accepted,
        "rating": previous.get("rating", default_rating),
        "recommended_lighting": var.recommended_lighting,
        "recommended_background": var.recommended_background,
        "user_notes": previous.get("user_notes", ""),
        "timestamp": time.time(),
        "latency_seconds": st.session_state.latency_by_variation.get(var.variation_id),
        "engine_mode": var.engine_mode,
        "participant": participant_code.strip(),
    }


GPU_MODES = (EngineMode.INTERMEDIATE, EngineMode.BASIC)


def save_generation_batch(
    source: Image.Image,
    variations: List[GeneratedVariation],
    mode: EngineMode,
    elapsed_seconds: float,
) -> Path:
    batch_dir = GENERATED_DIR / time.strftime("%Y%m%d_%H%M%S")
    batch_dir.mkdir(parents=True, exist_ok=True)
    source.save(batch_dir / "00_entrada.png")
    if variations[0].controlnet_edge_preview is not None:
        variations[0].controlnet_edge_preview.save(batch_dir / "01_canny.png")

    records = []
    for position, var in enumerate(variations, start=1):
        filename = f"var{position}_{var.preset_id}.png"
        var.image.save(batch_dir / filename)
        records.append(
            {
                "file": filename,
                "variation_id": var.variation_id,
                "title": var.title,
                "prompt_used": var.prompt_used,
                "guidance_scale": var.guidance_scale,
                "denoising_strength": var.denoising_strength,
            }
        )

    with open(batch_dir / "batch.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "engine_mode": mode.value,
                "total_elapsed_seconds": round(elapsed_seconds, 3),
                "seconds_per_image": round(elapsed_seconds / len(variations), 3),
                "variations": records,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )
    return batch_dir


def archive_participant_session(participant_code: str, participant_profile: str) -> Optional[Path]:
    decisions = list(st.session_state.decisions.values())
    if not decisions:
        return None

    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    explanation = st.session_state.agent_explanation
    metrics = asdict(compute_metrics(decisions, explanation.narrative if explanation else None))
    metrics.pop("explanation_fidelity_score", None)

    safe_code = re.sub(r"[^A-Za-z0-9_-]", "_", participant_code.strip()) or "participante"
    session_path = SESSIONS_DIR / f"{safe_code}_{time.strftime('%Y%m%d_%H%M%S')}.json"
    payload = {
        "participant": participant_code.strip(),
        "profile": participant_profile.strip(),
        "closed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "metrics": metrics,
        "agent": {
            "model": explanation.model_name,
            "fidelity_score": explanation.factual_consistency_score,
            "narrative": explanation.narrative,
        }
        if explanation
        else None,
        "decisions": decisions,
    }
    with open(session_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    st.session_state.decisions = {}
    st.session_state.variations = []
    st.session_state.agent_explanation = None
    st.session_state.latency_by_variation = {}
    save_decisions_json([], DECISIONS_FILEPATH)
    return session_path


def create_sample_portrait() -> Image.Image:
    import numpy as np
    import cv2
    canvas = np.zeros((512, 512, 3), dtype=np.uint8)
    for i in range(512):
        for j in range(512):
            canvas[i, j] = [min(255, 40 + i // 4), min(255, 50 + j // 4), min(255, 80 + (i + j) // 6)]
    cv2_circle = canvas.copy()
    center = (256, 230)
    cv2.circle(cv2_circle, center, 120, (220, 190, 165), -1)
    cv2.ellipse(cv2_circle, (256, 450), (180, 130), 0, 0, 360, (35, 45, 65), -1)
    cv2.circle(cv2_circle, (215, 210), 12, (50, 40, 30), -1)
    cv2.circle(cv2_circle, (297, 210), 12, (50, 40, 30), -1)
    cv2.ellipse(cv2_circle, (256, 270), (35, 18), 0, 0, 180, (60, 40, 40), 3)
    return Image.fromarray(cv2.cvtColor(cv2_circle, cv2.COLOR_BGR2RGB))


STYLES_PATH = CURRENT_DIR / "styles.css"
FRAMES_PER_ROW = 5
AGENT_OPTIONS = [AgentModel.EXPERT_RULES.value, AgentModel.GEMINI_FLASH.value, AgentModel.OPENAI_MINI.value]


def decision_state(decision: Dict[str, Any]) -> str:
    accepted = decision.get("accepted")
    if accepted is True:
        return "aceptada"
    if accepted is False:
        return "rechazada"
    return "pendiente"


def step_heading(number: int, title: str, hint: Optional[str] = None) -> None:
    hint_html = f'<p class="indicacion">{hint}</p>' if hint else ""
    st.markdown(
        f'<p class="paso"><span class="numero">{number}</span>{title}</p>{hint_html}',
        unsafe_allow_html=True,
    )


st.markdown(f"<style>{STYLES_PATH.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

st.markdown(
    """
    <header class="cabecera">
        <h1>Retratos profesionales</h1>
        <p class="bajada">Sube una foto, revisa las variaciones para LinkedIn, WhatsApp o GitHub y decide cuáles usarías. Al final, un agente explica tus elecciones a partir de lo que marcaste.</p>
        <p class="credito">Proyecto 2 de CS5363 Planificación y Toma de Decisiones en IA, UTEC 2026-2. Grupo 7: José Guillermo Gálvez Pacori, Matías Alonso Meneses Roncal y Alejandro Joel Ore García.</p>
    </header>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    st.markdown("#### Participante")
    participant_code = st.text_input(
        "Código",
        value="",
        placeholder="U1",
        help="Identificador anónimo. No escribas nombres ni datos personales.",
    )
    participant_profile = st.text_input(
        "Perfil",
        value="",
        placeholder="Estudiante de Ing. Industrial, 7.º ciclo",
    )
    if st.button("Guardar y cerrar sesión", width="stretch"):
        if not participant_code.strip():
            st.error("Escribe el código del participante antes de cerrar la sesión.")
        else:
            archived_path = archive_participant_session(participant_code, participant_profile)
            if archived_path is None:
                st.warning("Todavía no hay decisiones para guardar.")
            else:
                st.session_state.last_archived_session = archived_path.name
    if st.session_state.last_archived_session:
        st.caption(f"Sesión guardada en data/processed/sessions/{st.session_state.last_archived_session}")

    st.divider()

    st.markdown("#### Generación")
    mode_by_label = {mode.value: mode for mode in (EngineMode.INTERMEDIATE, EngineMode.BASIC, EngineMode.LOCAL)}
    engine_mode_choice = st.radio(
        "Motor generativo",
        options=list(mode_by_label.keys()),
        index=0,
        help=(
            "Nivel Intermedio: img2img guiado por los bordes Canny de la cara (ControlNet). "
            "Nivel Básico: img2img de Stable Diffusion sin ControlNet. "
            "Ambos corren en el servidor GPU. La contingencia local solo aplica filtros de imagen."
        ),
    )
    current_mode = mode_by_label[engine_mode_choice]

    if current_mode in GPU_MODES:
        st.session_state.gpu_backend_url = st.text_input(
            "URL del servidor GPU",
            value=st.session_state.gpu_backend_url,
            placeholder="https://....trycloudflare.com",
            help="La URL que muestra la última celda del notebook de Colab, o la de una máquina virtual (http://IP:8000).",
        ).strip()
        if st.button("Probar conexión", width="stretch"):
            try:
                resp = requests.get(f"{st.session_state.gpu_backend_url.rstrip('/')}/health", timeout=6)
                if resp.status_code == 200:
                    data = resp.json()
                    st.session_state.gpu_connected = True
                    st.session_state.gpu_device_name = data.get("device_name", "GPU")
                    st.session_state.gpu_lora_loaded = bool(data.get("lora_loaded"))
                else:
                    st.session_state.gpu_connected = False
                    st.session_state.gpu_device_name = ""
            except Exception:
                st.session_state.gpu_connected = False
                st.session_state.gpu_device_name = ""
            st.session_state.gpu_checked = True
        if st.session_state.get("gpu_checked"):
            if st.session_state.gpu_connected:
                lora_text = "LoRA activo" if st.session_state.get("gpu_lora_loaded") else "LoRA no cargado"
                st.markdown(
                    f'<p class="estado-conexion ok">Conectado a {st.session_state.gpu_device_name}, {lora_text}</p>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<p class="estado-conexion error">Sin conexión. Revisa que la URL sea la actual y que la celda del servidor siga en ejecución.</p>',
                    unsafe_allow_html=True,
                )
    else:
        st.caption("Sin GPU no se usa un modelo generativo: solo sirve para probar la interfaz.")

    st.session_state.engine.mode = current_mode

    st.divider()

    st.markdown("#### Estilos")
    selection_strategy = st.radio(
        "Cómo elegir los estilos",
        options=["Paquete", "Elegir uno por uno"],
        index=0,
        horizontal=True,
    )

    selected_preset_ids: List[str] = []
    if selection_strategy == "Paquete":
        package_options = {pkg.id: f"{pkg.name}" for pkg in get_all_packages()}
        selected_pkg_id = st.selectbox(
            "Paquete",
            options=list(package_options.keys()),
            format_func=lambda x: package_options[x],
        )
        chosen_pkg = get_package(selected_pkg_id)
        if chosen_pkg:
            st.caption(chosen_pkg.description)
            selected_preset_ids = chosen_pkg.preset_ids
    else:
        for p in get_all_presets():
            is_checked = st.checkbox(
                p.title,
                value=(p.id in ["linkedin_formal", "linkedin_business_casual", "whatsapp_smart_casual", "github_tech_casual", "content_creator"]),
                key=f"chk_{p.id}",
            )
            if is_checked:
                selected_preset_ids.append(p.id)
        st.caption(f"{len(selected_preset_ids)} estilos seleccionados.")

    st.divider()

    st.markdown("#### Vestimenta")
    custom_prompt_input = st.text_input(
        "Ajuste de vestimenta (opcional)",
        value="",
        placeholder="Terno gris de tres piezas, corbata verde",
        help="Se agrega a la descripción de cada estilo. Pasa primero por el filtro ético.",
    )

    if custom_prompt_input.strip():
        safety_check = check_prompt_safety(custom_prompt_input)
        if safety_check.is_safe:
            st.caption("El filtro ético aprobó el ajuste.")
        else:
            st.error(safety_check.warning_message)

    st.divider()

    st.markdown("#### Explicación")
    default_agent = 1 if os.getenv("GEMINI_API_KEY") else 0
    selected_agent_model = st.selectbox(
        "Modelo para la explicación",
        options=AGENT_OPTIONS,
        index=default_agent,
        help="El agente de reglas funciona sin internet. Gemini y OpenAI necesitan su clave de API.",
    )

    with st.expander("Claves de API"):
        gemini_key_input = st.text_input("Gemini", type="password", value=os.getenv("GEMINI_API_KEY", ""))
        openai_key_input = st.text_input("OpenAI", type="password", value=os.getenv("OPENAI_API_KEY", ""))
        if gemini_key_input:
            os.environ["GEMINI_API_KEY"] = gemini_key_input
        if openai_key_input:
            os.environ["OPENAI_API_KEY"] = openai_key_input


step_heading(1, "Tu foto", "De frente, a la altura de los ojos y de pecho hacia arriba. El sistema recorta la cara y extrae sus bordes para guiar al modelo.")

col_photo, col_preview = st.columns([1, 1.6], gap="large")

with col_photo:
    uploaded_file = st.file_uploader("Foto (PNG o JPG)", type=["png", "jpg", "jpeg", "webp"])
    use_sample = st.checkbox("Usar imagen de prueba", value=(uploaded_file is None))

    source_image: Optional[Image.Image] = None
    if uploaded_file is not None:
        source_image = ImageOps.exif_transpose(Image.open(uploaded_file)).convert("RGB")
    elif use_sample:
        source_image = create_sample_portrait()

    if source_image:
        st.image(source_image, caption="Foto original", width=240)

with col_preview:
    if source_image:
        preprocessed = st.session_state.engine.preprocess_face(source_image)
        edges = st.session_state.engine.extract_controlnet_edges(preprocessed)
        col_crop, col_edges = st.columns(2)
        with col_crop:
            st.image(preprocessed, caption="Recorte de 512 × 512 px", width="stretch")
        with col_edges:
            st.image(edges, caption="Bordes Canny que usa ControlNet", width="stretch")

    generate_clicked = st.button("Generar variaciones", type="primary", width="stretch")

    if generate_clicked:
        if current_mode in GPU_MODES and not st.session_state.gpu_backend_url:
            st.error("Escribe en la barra lateral la URL del servidor GPU (termina en trycloudflare.com) y presiona Probar conexión.")
        elif not source_image:
            st.error("Sube una foto o marca Usar imagen de prueba.")
        elif not selected_preset_ids:
            st.error("Elige al menos un estilo en la barra lateral.")
        else:
            with st.spinner(f"Generando {len(selected_preset_ids)} variaciones..."):
                start_time = time.time()
                if current_mode in GPU_MODES:
                    variations, safety_res = st.session_state.engine.generate_via_remote_gpu(
                        source_image,
                        selected_preset_ids,
                        backend_url=st.session_state.gpu_backend_url,
                        custom_prompt=custom_prompt_input,
                        mode=current_mode,
                    )
                else:
                    variations, safety_res = st.session_state.engine.generate_batch(
                        source_image,
                        selected_preset_ids,
                        custom_prompt=custom_prompt_input,
                    )
                elapsed = time.time() - start_time

                if not safety_res.is_safe:
                    st.error(safety_res.warning_message)
                else:
                    st.session_state.variations = variations
                    per_image_latency = round(elapsed / len(variations), 3) if variations else None
                    st.session_state.latency_by_variation = {v.variation_id: per_image_latency for v in variations}
                    if variations:
                        saved_dir = save_generation_batch(source_image, variations, current_mode, elapsed)
                        st.success(f"Se generaron {len(variations)} variaciones en {elapsed:.1f} s.")
                        st.caption(f"Guardadas en data/processed/generated/{saved_dir.name}")
                    else:
                        st.error("El motor no devolvió ninguna variación.")


st.divider()

step_heading(
    2,
    "Elige tus fotos",
    "Cada foto empieza pendiente. Acepta las que usarías y rechaza las demás. La calificación y el comentario ayudan al agente a explicar tu elección.",
)

if not st.session_state.variations:
    st.markdown(
        '<div class="vacio">Todavía no hay variaciones. Sube tu foto y presiona Generar variaciones.</div>',
        unsafe_allow_html=True,
    )
else:
    variations = st.session_state.variations
    for row_start in range(0, len(variations), FRAMES_PER_ROW):
        row = variations[row_start:row_start + FRAMES_PER_ROW]
        columns = st.columns(FRAMES_PER_ROW, gap="medium")
        for offset, var in enumerate(row):
            idx = row_start + offset
            curr_decision = st.session_state.decisions.get(var.variation_id, {})
            state = decision_state(curr_decision)
            with columns[offset]:
                with st.container(key=f"fotograma-{state}-{idx}"):
                    st.image(var.image, width="stretch")
                    st.markdown(
                        f'<p class="fotograma-numero">Variación {idx + 1}</p>'
                        f'<p class="fotograma-titulo">{var.title}</p>'
                        f'<p class="fotograma-red">{var.formality}, para {var.platform}</p>'
                        f'<p class="estado estado-{state}">{state.capitalize()}</p>',
                        unsafe_allow_html=True,
                    )

                    col_acc, col_rej = st.columns(2, gap="small")
                    with col_acc:
                        if st.button("Aceptar", key=f"acc_{var.variation_id}", width="stretch"):
                            st.session_state.decisions[var.variation_id] = build_decision_record(
                                var, True, curr_decision, 5, participant_code
                            )
                            save_decisions_json(list(st.session_state.decisions.values()), DECISIONS_FILEPATH)
                            st.rerun()
                    with col_rej:
                        if st.button("Rechazar", key=f"rej_{var.variation_id}", width="stretch"):
                            st.session_state.decisions[var.variation_id] = build_decision_record(
                                var, False, curr_decision, 2, participant_code
                            )
                            save_decisions_json(list(st.session_state.decisions.values()), DECISIONS_FILEPATH)
                            st.rerun()

                    rating = st.slider(
                        "Calificación",
                        min_value=1,
                        max_value=5,
                        value=int(curr_decision.get("rating", 4)),
                        key=f"rate_{var.variation_id}",
                    )
                    notes = st.text_input(
                        "Comentario",
                        value=str(curr_decision.get("user_notes", "")),
                        key=f"note_{var.variation_id}",
                        placeholder="Qué te gustó o qué cambiarías",
                    )
                    if rating != curr_decision.get("rating") or notes != curr_decision.get("user_notes"):
                        if var.variation_id in st.session_state.decisions:
                            st.session_state.decisions[var.variation_id]["rating"] = rating
                            st.session_state.decisions[var.variation_id]["user_notes"] = notes
                            save_decisions_json(list(st.session_state.decisions.values()), DECISIONS_FILEPATH)

                    with st.expander("Detalles"):
                        st.caption(f"Iluminación: {var.recommended_lighting}")
                        st.caption(f"Fondo: {var.recommended_background}")
                        st.caption(f"Vestimenta: {var.recommended_attire}")
                        st.caption(f"Prompt: {var.prompt_used}")
                        st.caption(f"Guidance {var.guidance_scale}, strength {var.denoising_strength}")


st.divider()

col_expl, col_metrics = st.columns([1.7, 1.0], gap="large")
all_decisions_list = list(st.session_state.decisions.values())

with col_expl:
    step_heading(3, "Por qué elegiste así", "El agente lee tus decisiones registradas, lista lo que aceptaste y rechazaste, y explica el patrón.")

    if st.button("Generar explicación", type="primary"):
        if not all_decisions_list:
            st.warning("Primero acepta o rechaza al menos una variación.")
        else:
            with st.spinner("Analizando tus decisiones..."):
                agent_enum = AgentModel.EXPERT_RULES
                if "Gemini" in selected_agent_model:
                    agent_enum = AgentModel.GEMINI_FLASH
                elif "OpenAI" in selected_agent_model:
                    agent_enum = AgentModel.OPENAI_MINI

                agent = ExplanationAgent(preferred_model=agent_enum)
                st.session_state.agent_explanation = agent.explain_decisions(all_decisions_list, model_choice=agent_enum)

    if st.session_state.agent_explanation:
        res = st.session_state.agent_explanation
        st.markdown(
            f'<p class="explicacion-meta">Modelo: {res.model_name}. '
            f'Fidelidad con el registro: {res.factual_consistency_score * 100:.0f} %.</p>',
            unsafe_allow_html=True,
        )
        with st.container(key="explicacion"):
            st.markdown(res.narrative)

with col_metrics:
    st.markdown('<p class="paso">Registro de la sesión</p>', unsafe_allow_html=True)
    current_metrics = compute_metrics(
        all_decisions_list,
        explanation_narrative=st.session_state.agent_explanation.narrative if st.session_state.agent_explanation else None,
    )
    st.markdown(
        f"""
        <dl class="registro">
            <div><dt>Variaciones evaluadas</dt><dd>{current_metrics.total_evaluated}</dd></div>
            <div><dt>Aceptadas</dt><dd>{current_metrics.accepted_count} ({current_metrics.acceptance_rate_percent:.0f} %)</dd></div>
            <div><dt>Rechazadas</dt><dd>{current_metrics.rejected_count}</dd></div>
            <div><dt>Calificación media</dt><dd>{current_metrics.average_rating:.1f} de 5</dd></div>
            <div><dt>Diversidad de estilos</dt><dd>{current_metrics.visual_diversity_score:.2f}</dd></div>
        </dl>
        """,
        unsafe_allow_html=True,
    )

    with open(DECISIONS_FILEPATH, "w", encoding="utf-8") as f:
        json.dump(all_decisions_list, f, indent=2, ensure_ascii=False)

    with open(DECISIONS_FILEPATH, "r", encoding="utf-8") as f:
        json_data = f.read()

    st.caption("Cada decisión se guarda al instante en data/processed/user_decisions.json.")
    st.download_button(
        label="Descargar registro (JSON)",
        data=json_data,
        file_name="user_decisions.json",
        mime="application/json",
        width="stretch",
    )
