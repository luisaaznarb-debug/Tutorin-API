# -*- coding: utf-8 -*-
"""
hints_statistics.py
Pistas progresivas para estadística y probabilidad.
✅ VERSIÓN CORREGIDA:
- Firma compatible con ai_router.py
- Pistas más específicas y útiles
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
    "stat_intro": """Eres Tutorín, profesor de Primaria (España, LOMLOE).

El alumno debe identificar la fracción de probabilidad (casos favorables / total).

CONTEXTO: {context}
RESPUESTA DEL ALUMNO: "{answer}"
ERRORES: {err}

Da UNA pista breve (máximo 2 frases) sobre cómo identificar casos favorables y totales.
NO des la fracción directamente.""",

    "stat_decimal": """Eres Tutorín, profesor de Primaria (España, LOMLOE).

El alumno debe calcular el valor decimal de una probabilidad dividiendo.

CONTEXTO: {context}
RESPUESTA DEL ALUMNO: "{answer}"
ERRORES: {err}

Da UNA pista breve (máximo 2 frases) sobre cómo hacer la división.
NO des el resultado final.""",

    "stat_percent": """Eres Tutorín, profesor de Primaria (España, LOMLOE).

El alumno debe convertir un decimal a porcentaje multiplicando por 100.

CONTEXTO: {context}
RESPUESTA DEL ALUMNO: "{answer}"
ERRORES: {err}

Da UNA pista breve (máximo 2 frases) sobre cómo multiplicar por 100.
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
    
    if hint_type == "stat_intro":
        return (
            "💡 <b>Para calcular probabilidad o frecuencia:</b><br/><br/>"
            "1️⃣ Identifica los <b>casos favorables</b> (los que cumplen la condición)<br/>"
            "2️⃣ Identifica el <b>total de casos</b> posibles<br/>"
            "3️⃣ Escribe la fracción: <b>casos favorables / total</b><br/><br/>"
            "🔹 <b>Ejemplo:</b><br/>"
            "Si de 20 alumnos, 5 prefieren azul:<br/>"
            "→ Casos favorables: <b>5</b><br/>"
            "→ Total: <b>20</b><br/>"
            "→ Fracción: <b>5/20</b>"
        )
    
    elif hint_type == "stat_decimal":
        return (
            "💡 <b>Para convertir a decimal:</b><br/>"
            "Divide el número de arriba (numerador) entre el de abajo (denominador)<br/><br/>"
            "🔹 <b>Ejemplos:</b><br/>"
            "• 5/20 → 5 ÷ 20 = <b>0.25</b><br/>"
            "• 3/10 → 3 ÷ 10 = <b>0.3</b><br/>"
            "• 1/4 → 1 ÷ 4 = <b>0.25</b><br/><br/>"
            "💡 <b>Interpretación:</b><br/>"
            "• 0 = imposible<br/>"
            "• 0.5 = igual de probable (50-50)<br/>"
            "• 1 = seguro"
        )
    
    elif hint_type == "stat_percent":
        return (
            "💡 <b>Para convertir a porcentaje:</b><br/>"
            "Multiplica el decimal por 100<br/><br/>"
            "🔹 <b>Ejemplos:</b><br/>"
            "• 0.25 × 100 = <b>25%</b><br/>"
            "• 0.5 × 100 = <b>50%</b><br/>"
            "• 0.75 × 100 = <b>75%</b><br/><br/>"
            "💡 <b>Significado:</b><br/>"
            "El porcentaje indica cuántas veces de cada 100 ocurrirá el evento"
        )
    
    elif hint_type == "stat_result":
        return (
            "🎉 ¡Muy bien! Has calculado correctamente la probabilidad.<br/><br/>"
            "📚 <b>Recuerda:</b><br/>"
            "• <b>Fracción:</b> muestra la proporción (ej: 1/4)<br/>"
            "• <b>Decimal:</b> valor numérico (ej: 0.25)<br/>"
            "• <b>Porcentaje:</b> más fácil de entender (ej: 25%)"
        )
    
    # ──────────────────────────────────────────────────────────
    # FALLBACK GENÉRICO
    # ──────────────────────────────────────────────────────────
    return (
        "🤔 <b>Recuerda los pasos:</b><br/>"
        "1️⃣ Identifica casos favorables y total<br/>"
        "2️⃣ Divide para obtener el decimal<br/>"
        "3️⃣ Multiplica por 100 para obtener el porcentaje"
    )