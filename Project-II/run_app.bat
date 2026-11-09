@echo off
title Retratos Pro IA - UTEC CS5363 Grupo 7
echo ===================================================================
echo   Iniciando Retratos Pro IA (Human-in-the-Loop + Agente LLM)
echo   Grupo 7 - CS5363 Planificacion y Toma de Decisiones en IA (UTEC)
echo ===================================================================
echo.
cd /d "%~dp0"
streamlit run ui/app.py
pause
