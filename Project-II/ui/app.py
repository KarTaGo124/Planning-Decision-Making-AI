import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st
from PIL import Image

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

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
    page_title="Retratos Pro IA - UTEC Grupo 7",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
DECISIONS_FILEPATH = str(DATA_PROCESSED_DIR / "decisiones_usuario.json")


def initialize_session_state() -> None:
    if "variations" not in st.session_state:
        st.session_state.variations = []
    if "decisions" not in st.session_state:
        existing = load_decisions_json(DECISIONS_FILEPATH)
        st.session_state.decisions = {d["variation_id"]: d for d in existing} if existing else {}
    if "agent_explanation" not in st.session_state:
        st.session_state.agent_explanation = None
    if "engine" not in st.session_state:
        st.session_state.engine = GenerationEngine(mode=EngineMode.INTERMEDIATE)


initialize_session_state()


def create_sample_portrait() -> Image.Image:
    import numpy as np
    canvas = np.zeros((512, 512, 3), dtype=np.uint8)
    for i in range(512):
        for j in range(512):
            canvas[i, j] = [min(255, 40 + i // 4), min(255, 50 + j // 4), min(255, 80 + (i + j) // 6)]
    cv2_circle = canvas.copy()
    center = (256, 230)
    import cv2
    cv2.circle(cv2_circle, center, 120, (220, 190, 165), -1)
    cv2.ellipse(cv2_circle, (256, 450), (180, 130), 0, 0, 360, (35, 45, 65), -1)
    cv2.circle(cv2_circle, (215, 210), 12, (50, 40, 30), -1)
    cv2.circle(cv2_circle, (297, 210), 12, (50, 40, 30), -1)
    cv2.ellipse(cv2_circle, (256, 270), (35, 18), 0, 0, 180, (60, 40, 40), 3)
    return Image.fromarray(cv2.cvtColor(cv2_circle, cv2.COLOR_BGR2RGB))


st.markdown(
    """
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 22px 28px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 24px;">
        <div style="font-size: 13px; font-weight: 700; color: #38bdf8; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 6px;">
            UTEC · CS5363 Planificación y Toma de Decisiones en IA (2026-2) · Proyecto 2
        </div>
        <h1 style="color: #ffffff; margin: 0 0 10px 0; font-size: 26px; font-weight: 800;">
            📸 Sistema Generativo de Retratos Profesionales con Feedback Humano
        </h1>
        <p style="color: #cbd5e1; margin: 0; font-size: 14px; line-height: 1.5;">
            Generación controlada de fotos profesionales para redes (LinkedIn, WhatsApp, GitHub) mediante difusión y ControlNet, captura estructurada de decisiones humanas y síntesis explicativa mediante agentes LLM.
        </p>
        <div style="margin-top: 10px; font-size: 12px; color: #94a3b8;">
            <b>Grupo 7:</b> José Guillermo Gálvez Pacori · Matías Alonso Meneses Roncal · Alejandro Joel Ore García | <b>Docentes:</b> Dra. Aurea Soriano-Vargas & Mg. Robert Buleje
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    st.header("⚙️ Configuración del Sistema")

    engine_mode_choice = st.radio(
        "Nivel Técnico del Modelo Generativo:",
        options=[EngineMode.INTERMEDIATE.value, EngineMode.BASIC.value],
        index=0,
        help="El Nivel Intermedio aplica preprocesamiento facial y condicionamiento estructural tipo ControlNet/Canny. El Nivel Básico simula el uso directo de APIs preentrenadas.",
    )
    current_mode = EngineMode.INTERMEDIATE if "Intermedio" in engine_mode_choice else EngineMode.BASIC
    st.session_state.engine.mode = current_mode

    st.divider()

    st.subheader("🎯 Catálogo y Paquetes de Estilo")
    selection_strategy = st.radio(
        "Modo de selección de variaciones:",
        options=["Por Paquete Temático", "Selección Personalizada"],
        index=0,
    )

    selected_preset_ids: List[str] = []
    if selection_strategy == "Por Paquete Temático":
        package_options = {pkg.id: f"{pkg.name}" for pkg in get_all_packages()}
        selected_pkg_id = st.selectbox(
            "Seleccione un paquete sugerido:",
            options=list(package_options.keys()),
            format_func=lambda x: package_options[x],
        )
        chosen_pkg = get_package(selected_pkg_id)
        if chosen_pkg:
            st.caption(f"ℹ️ {chosen_pkg.description}")
            selected_preset_ids = chosen_pkg.preset_ids
    else:
        st.write("Seleccione los estilos deseados (recomendado: 5 a 7):")
        all_presets = get_all_presets()
        for p in all_presets:
            is_checked = st.checkbox(
                f"{p.platform.value} - {p.formality.value}",
                value=(p.id in ["linkedin_formal", "linkedin_business_casual", "whatsapp_smart_casual", "github_tech_casual", "content_creator"]),
                key=f"chk_{p.id}",
            )
            if is_checked:
                selected_preset_ids.append(p.id)

    st.divider()

    st.subheader("✍️ Personalización (Prompt Libre)")
    custom_prompt_input = st.text_input(
        "Ajustes de vestimenta o accesorios (opcional):",
        value="",
        placeholder="Ej: terno 3 piezas gris marengo, corbata verde oscuro",
        help="Si no se ingresa texto, se aplicará el prompt por defecto óptimo del preset.",
    )

    if custom_prompt_input.strip():
        safety_check = check_prompt_safety(custom_prompt_input)
        if safety_check.is_safe:
            st.success("✅ Filtro ético: Solicitud aprobada.")
        else:
            st.error(f"🚫 {safety_check.warning_message}")

    st.divider()

    st.subheader("🤖 Agente de Explicación")
    selected_agent_model = st.selectbox(
        "Modelo de Lenguaje para Explicaciones:",
        options=[
            AgentModel.EXPERT_RULES.value,
            AgentModel.GEMINI_FLASH.value,
            AgentModel.OPENAI_MINI.value,
        ],
        index=0,
    )


col_left, col_right = st.columns([1, 2], gap="large")

with col_left:
    st.subheader("1. Fotografía de Entrada")
    uploaded_file = st.file_uploader(
        "Subir retrato base (PNG, JPG):",
        type=["png", "jpg", "jpeg", "webp"],
    )

    use_sample = st.checkbox("Usar retrato sintético de demostración", value=(uploaded_file is None))

    source_image: Optional[Image.Image] = None
    if uploaded_file is not None:
        source_image = Image.open(uploaded_file).convert("RGB")
    elif use_sample:
        source_image = create_sample_portrait()

    if source_image:
        st.image(source_image, caption="Fotografía de entrada proporcionada", use_container_width=True)
        if current_mode == EngineMode.INTERMEDIATE:
            with st.expander("🔍 Vista de Preprocesamiento y ControlNet Canny"):
                preprocessed = st.session_state.engine.preprocess_face(source_image)
                edges = st.session_state.engine.extract_controlnet_edges(preprocessed)
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    st.image(preprocessed, caption="Rostro centrado / 512x512", use_container_width=True)
                with col_c2:
                    st.image(edges, caption="Estructura Canny (ControlNet)", use_container_width=True)

    st.markdown("---")

    generate_clicked = st.button("🚀 Generar Variaciones Visuales", type="primary", use_container_width=True)

    if generate_clicked:
        if not source_image:
            st.error("Por favor, suba una fotografía o active la imagen de demostración.")
        elif not selected_preset_ids:
            st.error("Debe seleccionar al menos un estilo o paquete.")
        else:
            with st.spinner("Procesando transformaciones con el motor generativo..."):
                start_time = time.time()
                variations, safety_res = st.session_state.engine.generate_batch(
                    source_image,
                    selected_preset_ids,
                    custom_prompt=custom_prompt_input,
                    mode=current_mode,
                )
                elapsed = time.time() - start_time

                if not safety_res.is_safe:
                    st.error(f"❌ {safety_res.warning_message}")
                else:
                    st.session_state.variations = variations
                    st.success(f"Se generaron {len(variations)} variaciones exitosamente en {elapsed:.2f} s.")


with col_right:
    st.subheader("2. Variaciones Generadas y Feedback Humano")

    if not st.session_state.variations:
        st.info("👈 Presione 'Generar Variaciones Visuales' para producir las fotos profesionales.")
    else:
        st.caption(f"Mostrando {len(st.session_state.variations)} variaciones bajo el {current_mode.value}. Indique su decisión en cada una:")

        for idx, var in enumerate(st.session_state.variations):
            with st.container(border=True):
                c_img, c_meta, c_actions = st.columns([1.2, 1.8, 1.3], gap="medium")

                with c_img:
                    st.image(var.image, caption=f"Var #{idx+1} · {var.title}", use_container_width=True)

                with c_meta:
                    st.markdown(f"**{var.title}**")
                    st.markdown(f"📱 **Plataforma:** `{var.platform}` | 👔 **Formalidad:** `{var.formality}`")
                    st.markdown(f"💡 **Iluminación:** {var.recommended_lighting}")
                    st.markdown(f"🏢 **Fondo:** {var.recommended_background}")
                    st.markdown(f"👔 **Vestimenta:** {var.recommended_attire}")

                    with st.expander("Detalles del Prompt Técnico"):
                        st.caption(f"**Prompt:** {var.prompt_used}")
                        st.caption(f"**CFG Scale:** {var.guidance_scale} | **Denoising:** {var.denoising_strength}")

                with c_actions:
                    curr_decision = st.session_state.decisions.get(var.variation_id, {})
                    is_accepted = curr_decision.get("accepted")

                    if is_accepted is True:
                        st.success("✅ Aceptada")
                    elif is_accepted is False:
                        st.error("❌ Rechazada")
                    else:
                        st.warning("⏳ Pendiente")

                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("Aceptar", key=f"acc_{var.variation_id}", use_container_width=True):
                            st.session_state.decisions[var.variation_id] = {
                                "variation_id": var.variation_id,
                                "preset_id": var.preset_id,
                                "title": var.title,
                                "platform": var.platform,
                                "formality": var.formality,
                                "accepted": True,
                                "rating": curr_decision.get("rating", 5),
                                "recommended_lighting": var.recommended_lighting,
                                "recommended_background": var.recommended_background,
                                "user_notes": curr_decision.get("user_notes", ""),
                                "timestamp": time.time(),
                                "latency_seconds": 2.1,
                            }
                            save_decisions_json(list(st.session_state.decisions.values()), DECISIONS_FILEPATH)
                            st.rerun()

                    with col_btn2:
                        if st.button("Rechazar", key=f"rej_{var.variation_id}", use_container_width=True):
                            st.session_state.decisions[var.variation_id] = {
                                "variation_id": var.variation_id,
                                "preset_id": var.preset_id,
                                "title": var.title,
                                "platform": var.platform,
                                "formality": var.formality,
                                "accepted": False,
                                "rating": curr_decision.get("rating", 2),
                                "recommended_lighting": var.recommended_lighting,
                                "recommended_background": var.recommended_background,
                                "user_notes": curr_decision.get("user_notes", ""),
                                "timestamp": time.time(),
                                "latency_seconds": 1.8,
                            }
                            save_decisions_json(list(st.session_state.decisions.values()), DECISIONS_FILEPATH)
                            st.rerun()

                    rating = st.slider(
                        "Calificación:",
                        min_value=1,
                        max_value=5,
                        value=int(curr_decision.get("rating", 4)),
                        key=f"rate_{var.variation_id}",
                    )
                    notes = st.text_input(
                        "Nota de feedback:",
                        value=str(curr_decision.get("user_notes", "")),
                        key=f"note_{var.variation_id}",
                        placeholder="Ej: Buena luz, pero fondo algo simple",
                    )
                    if rating != curr_decision.get("rating") or notes != curr_decision.get("user_notes"):
                        if var.variation_id in st.session_state.decisions:
                            st.session_state.decisions[var.variation_id]["rating"] = rating
                            st.session_state.decisions[var.variation_id]["user_notes"] = notes
                            save_decisions_json(list(st.session_state.decisions.values()), DECISIONS_FILEPATH)


st.divider()

col_expl, col_metrics = st.columns([1.3, 1.0], gap="large")

with col_expl:
    st.subheader("3. Agente Explicador de Decisiones (LLM)")
    st.caption("Analiza las razones detrás de las elecciones del usuario y sintetiza patrones de preferencia.")

    all_decisions_list = list(st.session_state.decisions.values())

    if st.button("🧠 Generar Explicación con Agente IA", type="secondary", use_container_width=True):
        if not all_decisions_list:
            st.warning("Primero debe calificar o aceptar/rechazar al menos una imagen generada.")
        else:
            with st.spinner("El agente de IA está analizando los registros de decisiones..."):
                agent_enum = AgentModel.EXPERT_RULES
                if "Gemini" in selected_agent_model:
                    agent_enum = AgentModel.GEMINI_FLASH
                elif "OpenAI" in selected_agent_model:
                    agent_enum = AgentModel.OPENAI_MINI

                agent = ExplanationAgent(preferred_model=agent_enum)
                explanation_res = agent.explain_decisions(all_decisions_list, model_choice=agent_enum)
                st.session_state.agent_explanation = explanation_res

    if st.session_state.agent_explanation:
        res = st.session_state.agent_explanation
        st.markdown(f"**Modelo Utilizado:** `{res.model_name}`")
        st.markdown(f"**Fidelidad Factual:** `{res.factual_consistency_score * 100:.1f}%`")
        st.info(res.summary)
        with st.expander("Ver informe explicativo completo", expanded=True):
            st.markdown(res.narrative)


with col_metrics:
    st.subheader("4. Métricas de Evaluación y Registro")
    current_metrics = compute_metrics(
        all_decisions_list,
        explanation_narrative=st.session_state.agent_explanation.narrative if st.session_state.agent_explanation else None,
    )

    m1, m2 = st.columns(2)
    m1.metric("Tasa de Aceptación", f"{current_metrics.acceptance_rate_percent:.1f}%")
    m2.metric("Total Evaluadas", f"{current_metrics.total_evaluated}")

    m3, m4 = st.columns(2)
    m3.metric("Calificación Promedio", f"{current_metrics.average_rating:.2f} / 5.0")
    m4.metric("Diversidad Visual", f"{current_metrics.visual_diversity_score:.2f}")

    st.caption(f"📁 Registro persistente en: `data/processed/decisiones_usuario.json` ({len(all_decisions_list)} entradas)")

    with open(DECISIONS_FILEPATH, "w", encoding="utf-8") as f:
        import json
        json.dump(all_decisions_list, f, indent=2, ensure_ascii=False)

    with open(DECISIONS_FILEPATH, "r", encoding="utf-8") as f:
        json_data = f.read()

    st.download_button(
        label="📥 Descargar decisiones_usuario.json",
        data=json_data,
        file_name="decisiones_usuario.json",
        mime="application/json",
        use_container_width=True,
    )
