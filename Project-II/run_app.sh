#!/usr/bin/env bash
printf '\033]0;%s\007' "Retratos Pro IA - UTEC CS5363 Grupo 7"
echo "==================================================================="
echo "  Iniciando Retratos Pro IA (Human-in-the-Loop + Agente LLM)"
echo "  Grupo 7 - CS5363 Planificacion y Toma de Decisiones en IA (UTEC)"
echo "==================================================================="
echo ""
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
uv run streamlit run ui/app.py
read -r -p "Presione Enter para continuar..."
