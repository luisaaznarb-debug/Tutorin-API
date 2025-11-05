# -*- coding: utf-8 -*-
"""
hints_decimals.py
Pistas progresivas para decimales.
✅ VERSIÓN ACTUALIZADA: Coherente con el motor corregido
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
    "decimal_suma": """Eres Tutorín, profesor de Primaria (España, LOMLOE).

El alumno está sumando decimales DIRECTAMENTE (sin quitar la coma).

CONTEXTO: {context}
RESPUESTA DEL ALUMNO: "{answer}"
ERRORES: {err}

Da UNA pista breve (máximo 2 frases) sobre cómo alinear las comas y sumar.
NO des el resultado final.""",

    "decimal_resta": """Eres Tutorín, profesor de Primaria (España, LOMLOE).

El alumno está restando decimales DIRECTAMENTE (sin quitar la coma).

CONTEXTO: {context}
RESPUESTA DEL ALUMNO: "{answer}"
ERRORES: {err}

Da UNA pista breve (máximo 2 frases) sobre cómo alinear las comas y restar.
NO des el resultado final.""",

    "decimal_convert": """Eres Tutorín, profesor de Primaria (España, LOMLOE).

El alumno está aprendiendo a convertir decimales a enteros para MULTIPLICAR.

CONTEXTO: {context}
RESPUESTA DEL ALUMNO: "{answer}"
ERRORES: {err}

Da UNA pista breve (máximo 2 frases) sobre cómo mover la coma para convertir a enteros.
NO des la respuesta completa.""",

    "decimal_multiplicacion": """Eres Tutorín, profesor de Primaria (España, LOMLOE).

El alumno debe multiplicar dos números enteros (que originalmente eran decimales).

CONTEXTO: {context}
RESPUESTA DEL ALUMNO: "{answer}"
ERRORES: {err}

Da UNA pista breve (máximo 2 frases) sobre cómo hacer la multiplicación.
NO des el resultado final.""",

    "decimal_final": """Eres Tutorín, profesor de Primaria (España, LOMLOE).

El alumno debe colocar la coma en el resultado de una MULTIPLICACIÓN contando decimales desde la derecha.

CONTEXTO: {context}
RESPUESTA DEL ALUMNO: "{answer}"
ERRORES: {err}

Da UNA pista breve (máximo 2 frases) sobre cómo colocar la coma correctamente.
NO des el resultado final.""",

    "decimal_div_count": """Eres Tutorín, profesor de Primaria (España, LOMLOE).

El alumno debe contar cuántas cifras decimales tiene el divisor.

CONTEXTO: {context}
RESPUESTA DEL ALUMNO: "{answer}"
ERRORES: {err}

Da UNA pista breve (máximo 2 frases) sobre cómo contar las cifras después de la coma.
NO des la respuesta.""",

    "decimal_div_calculate": """Eres Tutorín, profesor de Primaria (España, LOMLOE).

El alumno debe dividir dos números después de haber ajustado los decimales.

CONTEXTO: {context}
RESPUESTA DEL ALUMNO: "{answer}"
ERRORES: {err}

Da UNA pista breve (máximo 2 frases) sobre cómo hacer la división.
NO des el resultado final."""
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
    
    # ✅ SUMA Y RESTA: Ahora es operación directa
    if hint_type == "decimal_suma":
        return (
            "💡 <b>Recuerda:</b> Para sumar decimales, <u>NO quites la coma</u>.<br/>"
            "Solo alinea las comas y suma como si fueran números enteros.<br/><br/>"
            "🔹 Ejemplo:<br/>"
            "<pre style='background: #e3f2fd; padding: 5px; font-family: monospace;'>"
            "  2.5\n"
            "+ 1.3\n"
            "-----\n"
            "  3.8"
            "</pre>"
        )
    
    elif hint_type == "decimal_resta":
        return (
            "💡 <b>Recuerda:</b> Para restar decimales, <u>NO quites la coma</u>.<br/>"
            "Solo alinea las comas y resta como si fueran números enteros.<br/><br/>"
            "🔹 Ejemplo:<br/>"
            "<pre style='background: #e3f2fd; padding: 5px; font-family: monospace;'>"
            "  5.6\n"
            "- 2.3\n"
            "-----\n"
            "  3.3"
            "</pre>"
        )
    
    # ✅ MULTIPLICACIÓN: Mantiene método de conversión
    elif hint_type == "decimal_convert":
        return (
            "💡 <b>Recuerda:</b> Para multiplicar decimales, primero los convertimos a enteros.<br/>"
            "Mueve la coma hacia la derecha hasta que desaparezca.<br/><br/>"
            "🔹 Ejemplo: <b>2.5</b> → <b>25</b> (movimos 1 posición)<br/>"
            "🔹 Ejemplo: <b>0.34</b> → <b>34</b> (movimos 2 posiciones)"
        )
    
    elif hint_type == "decimal_multiplicacion":
        return (
            "💡 <b>Recuerda:</b> Multiplica los números enteros que obtuviste.<br/>"
            "Puedes usar papel y lápiz si lo necesitas."
        )
    
    elif hint_type == "decimal_final":
        return (
            "💡 <b>Recuerda:</b> Cuenta cuántas cifras decimales tienen los dos números originales.<br/>"
            "Súmalas y coloca la coma contando esa cantidad de posiciones desde la derecha."
        )
    
    # ✅ DIVISIÓN: Mantiene método pero corregido
    elif hint_type == "decimal_div_count":
        return (
            "💡 <b>Recuerda:</b> Las cifras decimales son las que están <b>después de la coma</b>.<br/>"
            "🔹 Ejemplo: <b>2.5</b> tiene <b>1</b> cifra decimal<br/>"
            "🔹 Ejemplo: <b>0.34</b> tiene <b>2</b> cifras decimales"
        )
    
    elif hint_type == "decimal_div_calculate":
        return (
            "💡 <b>Recuerda:</b> Divide los números que obtuviste después de mover las comas.<br/>"
            "Puedes hacer la división larga en papel si lo necesitas."
        )
    
    # ──────────────────────────────────────────────────────────
    # FALLBACK GENÉRICO
    # ──────────────────────────────────────────────────────────
    return (
        "🤔 <b>Piensa en los pasos:</b><br/>"
        "• <b>Suma/Resta:</b> Alinea las comas y opera directamente<br/>"
        "• <b>Multiplicación:</b> Convierte a enteros, multiplica, coloca coma<br/>"
        "• <b>División:</b> Ajusta decimales del divisor y divide"
    )