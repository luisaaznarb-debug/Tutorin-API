# -*- coding: utf-8 -*-
"""
hints_percentages.py
Pistas progresivas para porcentajes.
✅ VERSIÓN CORREGIDA V3:
- Añadidos nuevos hint_types: perc_multiply, perc_divide
- Prompts específicos para cada paso
- Integración con OpenAI
"""
from typing import Optional
import os
import re

# ══════════════════════════════════════════════════════════════
# INTEGRACIÓN CON OPENAI
# ══════════════════════════════════════════════════════════════

try:
    from openai import OpenAI
    _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    _USE_AI = bool(os.getenv("OPENAI_API_KEY"))
except Exception:
    _client = None
    _USE_AI = False

# ══════════════════════════════════════════════════════════════
# PROMPTS ESPECÍFICOS POR TIPO DE HINT
# ══════════════════════════════════════════════════════════════

PROMPT_TEMPLATES = {
    "perc_frac": """Eres Tutorín, profesor de Primaria (España, LOMLOE).

El alumno debe convertir un porcentaje a fracción.

CONTEXTO: {context}
RESPUESTA DEL ALUMNO: "{answer}"
ERRORES: {err}

Da UNA pista breve (máximo 2 frases) sobre cómo convertir % a fracción.
Ejemplo: "El símbolo % significa 'de cada 100', así que 25% = 25/100"
NO des la respuesta completa.""",

    "perc_multiply": """Eres Tutorín, profesor de Primaria (España, LOMLOE).

El alumno debe multiplicar dos números para calcular un porcentaje.

CONTEXTO: {context}
RESPUESTA DEL ALUMNO: "{answer}"
ERRORES: {err}

Da UNA pista breve (máximo 2 frases) sobre cómo hacer la multiplicación.
Puedes sugerirle que use la calculadora o que lo haga paso a paso.
NO des el resultado final.""",

    "perc_divide": """Eres Tutorín, profesor de Primaria (España, LOMLOE).

El alumno debe dividir entre 100 para obtener el resultado final del porcentaje.

CONTEXTO: {context}
RESPUESTA DEL ALUMNO: "{answer}"
ERRORES: {err}

Da UNA pista breve (máximo 2 frases) sobre cómo dividir entre 100.
Puedes mencionar el truco de mover la coma dos posiciones a la izquierda.
NO des el resultado final.""",
}

# ══════════════════════════════════════════════════════════════
# GENERACIÓN DE HINTS CON IA
# ══════════════════════════════════════════════════════════════

def _ai_hint(hint_type: str, context: str, answer: str, err: int) -> Optional[str]:
    """Genera pista con OpenAI si está disponible y err >= 2."""
    if not _USE_AI or not _client or err < 2:
        return None
    
    prompt_template = PROMPT_TEMPLATES.get(hint_type)
    if not prompt_template:
        return None
    
    prompt = prompt_template.format(context=context, answer=answer, err=err)
    
    try:
        res = _client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "Eres Tutorín, profesor de Primaria empático y claro. Hablas con naturalidad a niños de 8-12 años."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=120,
            temperature=0.7
        )
        
        ai_response = res.choices[0].message.content.strip()
        return ai_response.replace('"', '').replace("'", "")
        
    except Exception as e:
        print(f"[AI Hint Error] {e}")
        return None

# ══════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL
# ══════════════════════════════════════════════════════════════

def get_hint(hint_type: str, errors: int, context: str = "", answer: str = "") -> str:
    """
    Genera pista según tipo, errores, contexto y respuesta del alumno.
    ✅ Firma compatible con ai_router.py
    
    Niveles:
    - Error 1: Pista general
    - Error 2+: Pista con IA (si está disponible)
    - Fallback: Pista genérica
    """
    
    # Intentar con IA primero (si err >= 2)
    if errors >= 2:
        ai_hint = _ai_hint(hint_type, context, answer, errors)
        if ai_hint:
            return f"💡 <b>Pista:</b> {ai_hint}"
    
    # ──────────────────────────────────────────────────────────
    # FALLBACK: Pistas locales por tipo
    # ──────────────────────────────────────────────────────────
    
    if hint_type == "perc_frac":
        return (
            "💡 <b>Recuerda:</b> El símbolo <b>%</b> significa <i>'de cada 100'</i>.<br/><br/>"
            "🔹 Ejemplo: <b>25%</b> = <b>25/100</b><br/>"
            "🔹 Ejemplo: <b>50%</b> = <b>50/100</b> = <b>1/2</b><br/>"
            "🔹 Ejemplo: <b>10%</b> = <b>10/100</b> = <b>1/10</b>"
        )
    
    elif hint_type == "perc_multiply":
        return (
            "💡 <b>Pista para multiplicar:</b><br/><br/>"
            "🔹 Puedes usar la calculadora si lo necesitas<br/>"
            "🔹 O hacerlo paso a paso:<br/>"
            "   → Ejemplo: <b>25 × 75</b><br/>"
            "   → 25 × 70 = 1750<br/>"
            "   → 25 × 5 = 125<br/>"
            "   → 1750 + 125 = <b>1875</b><br/><br/>"
            "💡 ¡Revisa bien los cálculos!"
        )
    
    elif hint_type == "perc_divide":
        return (
            "💡 <b>Pista para dividir entre 100:</b><br/><br/>"
            "🔹 <b>Truco rápido:</b> Mover la coma dos posiciones a la izquierda<br/><br/>"
            "📝 Ejemplos:<br/>"
            "• <b>1875</b> ÷ 100 → mueve la coma: <b>18.75</b><br/>"
            "• <b>2000</b> ÷ 100 → mueve la coma: <b>20.00</b> = <b>20</b><br/>"
            "• <b>350</b> ÷ 100 → mueve la coma: <b>3.50</b> = <b>3.5</b><br/><br/>"
            "💡 ¿Ves el patrón? ¡Inténtalo con tu número!"
        )
    
    elif hint_type == "perc_result":
        return (
            "🎉 ¡Muy bien! Has calculado correctamente el porcentaje.<br/><br/>"
            "📚 <b>Recuerda:</b><br/>"
            "• 50% es la mitad<br/>"
            "• 25% es la cuarta parte<br/>"
            "• 10% es la décima parte"
        )
    
    # ──────────────────────────────────────────────────────────
    # FALLBACK GENÉRICO
    # ──────────────────────────────────────────────────────────
    return (
        "🤔 <b>Recuerda los pasos:</b><br/>"
        "1️⃣ Convertir % a fracción (ejemplo: 25% = 25/100)<br/>"
        "2️⃣ Multiplicar la cantidad por el porcentaje<br/>"
        "3️⃣ Dividir entre 100"
    )