# -*- coding: utf-8 -*-
"""
hints_geometry.py
Pistas progresivas para geometría.
✅ VERSIÓN CORREGIDA:
- Firma compatible con ai_router.py
- Pistas más específicas por tipo de figura
- Integración con OpenAI
"""
from typing import Optional
import os

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
    "geo_formula": """Eres Tutorín, profesor de Primaria (España, LOMLOE).

El alumno debe recordar la fórmula para calcular área o perímetro de una figura geométrica.

CONTEXTO: {context}
RESPUESTA DEL ALUMNO: "{answer}"
ERRORES: {err}

Da UNA pista breve (máximo 2 frases) sobre cómo recordar la fórmula.
NO des la fórmula completa.""",

    "geo_substitute": """Eres Tutorín, profesor de Primaria (España, LOMLOE).

El alumno debe sustituir valores numéricos en una fórmula geométrica.

CONTEXTO: {context}
RESPUESTA DEL ALUMNO: "{answer}"
ERRORES: {err}

Da UNA pista breve (máximo 2 frases) sobre cómo sustituir los valores.
NO des la respuesta completa.""",

    "geo_calc": """Eres Tutorín, profesor de Primaria (España, LOMLOE).

El alumno debe realizar el cálculo numérico final de un problema de geometría.

CONTEXTO: {context}
RESPUESTA DEL ALUMNO: "{answer}"
ERRORES: {err}

Da UNA pista breve (máximo 2 frases) sobre cómo hacer el cálculo.
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
    
    if hint_type == "geo_formula":
        return (
            "💡 <b>Recuerda las fórmulas básicas:</b><br/><br/>"
            "🔹 <b>Cuadrado:</b><br/>"
            "• Área: lado × lado<br/>"
            "• Perímetro: 4 × lado<br/><br/>"
            "🔹 <b>Rectángulo:</b><br/>"
            "• Área: base × altura<br/>"
            "• Perímetro: 2 × (base + altura)<br/><br/>"
            "🔹 <b>Triángulo:</b><br/>"
            "• Área: (base × altura) ÷ 2<br/><br/>"
            "🔹 <b>Círculo:</b><br/>"
            "• Área: π × radio²<br/>"
            "• Perímetro: 2 × π × radio"
        )
    
    elif hint_type == "geo_substitute":
        return (
            "💡 <b>Para sustituir valores:</b><br/>"
            "1️⃣ Identifica qué representa cada número (lado, base, altura, radio)<br/>"
            "2️⃣ Reemplaza cada palabra de la fórmula por su número<br/><br/>"
            "🔹 <b>Ejemplo:</b><br/>"
            "Si la fórmula es <b>base × altura</b><br/>"
            "Y tienes base = 8, altura = 5<br/>"
            "Entonces escribes: <b>8 × 5</b>"
        )
    
    elif hint_type == "geo_calc":
        return (
            "💡 <b>Para calcular:</b><br/>"
            "1️⃣ Resuelve las operaciones dentro de paréntesis primero<br/>"
            "2️⃣ Luego multiplicaciones y divisiones (de izquierda a derecha)<br/>"
            "3️⃣ Finalmente sumas y restas<br/><br/>"
            "🔹 <b>Ejemplo:</b> 2 × (8 + 5)<br/>"
            "→ Primero: 8 + 5 = 13<br/>"
            "→ Luego: 2 × 13 = <b>26</b>"
        )
    
    elif hint_type == "geo_result":
        return (
            "🎉 ¡Muy bien! Has calculado correctamente.<br/><br/>"
            "📚 <b>Recuerda:</b><br/>"
            "• El <b>área</b> se mide en unidades cuadradas (cm², m², etc.)<br/>"
            "• El <b>perímetro</b> se mide en unidades lineales (cm, m, etc.)"
        )
    
    # ──────────────────────────────────────────────────────────
    # FALLBACK GENÉRICO
    # ──────────────────────────────────────────────────────────
    return (
        "🤔 <b>Recuerda los pasos:</b><br/>"
        "1️⃣ Identifica la fórmula correcta<br/>"
        "2️⃣ Sustituye los valores<br/>"
        "3️⃣ Calcula el resultado paso a paso"
    )