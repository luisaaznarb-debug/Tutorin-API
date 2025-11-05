# -*- coding: utf-8 -*-
"""
hints_measures.py
Pistas progresivas para conversión de unidades.
✅ VERSIÓN CORREGIDA:
- Firma compatible con ai_router.py
- Pistas más específicas por tipo de medida
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
    "meas_factor": """Eres Tutorín, profesor de Primaria (España, LOMLOE).

El alumno debe identificar el factor de conversión entre dos unidades de medida.

CONTEXTO: {context}
RESPUESTA DEL ALUMNO: "{answer}"
ERRORES: {err}

Da UNA pista breve (máximo 2 frases) sobre cómo recordar el factor de conversión.
NO des el factor directamente.""",

    "meas_calc": """Eres Tutorín, profesor de Primaria (España, LOMLOE).

El alumno debe calcular el resultado de una conversión de unidades.

CONTEXTO: {context}
RESPUESTA DEL ALUMNO: "{answer}"
ERRORES: {err}

Da UNA pista breve (máximo 2 frases) sobre cómo hacer la multiplicación.
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
    
    if hint_type == "meas_factor":
        return (
            "💡 <b>Recuerda las equivalencias básicas:</b><br/><br/>"
            "📏 <b>Longitud:</b><br/>"
            "• 1 km = 1000 m<br/>"
            "• 1 m = 100 cm<br/>"
            "• 1 cm = 10 mm<br/><br/>"
            "⚖️ <b>Masa:</b><br/>"
            "• 1 kg = 1000 g<br/>"
            "• 1 g = 1000 mg<br/><br/>"
            "🥤 <b>Capacidad:</b><br/>"
            "• 1 l = 1000 ml<br/>"
            "• 1 l = 100 cl<br/>"
            "• 1 l = 10 dl"
        )
    
    elif hint_type == "meas_calc":
        return (
            "💡 <b>Para calcular la conversión:</b><br/>"
            "1️⃣ Multiplica el valor por el factor de conversión<br/>"
            "2️⃣ Usa calculadora si lo necesitas<br/><br/>"
            "🔹 <b>Ejemplo:</b> 3 km a m<br/>"
            "→ 3 × 1000 = <b>3000 m</b><br/><br/>"
            "🔹 <b>Ejemplo:</b> 2500 ml a l<br/>"
            "→ 2500 × 0.001 = <b>2.5 l</b>"
        )
    
    elif hint_type == "meas_result":
        return (
            "🎉 ¡Muy bien! Has convertido correctamente las unidades.<br/><br/>"
            "📚 <b>Recuerda:</b><br/>"
            "• A unidad más pequeña → número más grande (multiplicas)<br/>"
            "• A unidad más grande → número más pequeño (divides o multiplicas por decimal)"
        )
    
    elif hint_type == "meas_unknown":
        return (
            "❌ No conozco esa conversión todavía.<br/><br/>"
            "💡 <b>Unidades válidas:</b><br/>"
            "• Longitud: km, m, cm, mm<br/>"
            "• Masa: kg, g, mg<br/>"
            "• Capacidad: l, ml, cl, dl"
        )
    
    # ──────────────────────────────────────────────────────────
    # FALLBACK GENÉRICO
    # ──────────────────────────────────────────────────────────
    return (
        "🤔 <b>Recuerda los pasos:</b><br/>"
        "1️⃣ Identifica el factor de conversión<br/>"
        "2️⃣ Multiplica el valor por el factor"
    )