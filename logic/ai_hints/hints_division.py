# -*- coding: utf-8 -*-
"""
hints_division.py
Pistas progresivas para división según nivel de error.
Compatible con division_engine.py
"""
from .hints_utils import _extract_pre_block, _question
import re
from typing import Optional

# ────────── Pistas por subpaso ──────────
def _div_grupo_hint(context: str, err: int, cycle: str) -> str:
    """Pistas para elegir el primer grupo del dividendo."""
    # CORREGIDO: Buscar el patrón que realmente genera el motor
    m = re.search(r"divisor = <b>(\d+)</b>", context) or re.search(r"divisor.*?<b>(\d+)</b>", context)
    d = int(m.group(1)) if m else None
    if err == 1:
        return (
            "👉 Elige el <b>primer grupo del dividendo</b> (empezando por la izquierda) "
            "que sea mayor o igual al divisor. " + _question("¿Qué número es?")
        )
    if err == 2 and d:
        return (
            f"🧮 Avanza desde la izquierda hasta formar un número ≥ {d}. "
            f"Ese será el primer grupo con el que empezamos a dividir. "
            + _question("¿Cuál es ese número?")
        )
    if err >= 3 and d:
        return (
            f"💡 Empieza con el mínimo número de cifras que sea ≥ {d}. "
            "Por ejemplo, si el dividendo es 847 y el divisor es 23, empiezas con 84 (no con 8)."
        )
    return "Toma el prefijo mínimo del dividendo que sea ≥ al divisor."

def _div_qdigit_hint(context: str, err: int, cycle: str) -> str:
    """Pistas para elegir la cifra del cociente."""
    m = re.search(r"cabe <b>(\d+)</b> en <b>(\d+)</b>", context)
    div = int(m.group(1)) if m else None
    grp = int(m.group(2)) if m else None
    
    if err == 1:
        return (
            "👉 Piensa: ¿cuántas veces cabe el divisor en este grupo sin pasarte? "
            "Esa es la cifra del cociente. " + _question("¿Qué cifra pones?")
        )
    if err == 2 and div and grp:
        # MEJORADO: Mostrar 3 opciones (una menor, la correcta, una mayor)
        if grp < div:
            return (
                f"🧮 Como {grp} es menor que {div}, la cifra del cociente es 0. "
                "Esto significa que este grupo no alcanza para dividir. "
                + _question("¿Qué cifra escribes?")
            )
        else:
            q_correcto = grp // div
            q_menor = max(0, q_correcto - 1)
            q_mayor = q_correcto + 1
            return (
                f"🧮 Prueba con la tabla del {div}:<br>"
                f"• {div}×{q_menor}={div*q_menor} (se queda corto)<br>"
                f"• {div}×{q_correcto}={div*q_correcto} (¡justo o casi!)<br>"
                f"• {div}×{q_mayor}={div*q_mayor} (se pasa de {grp})<br>"
                + _question("¿Cuál es la cifra correcta?")
            )
    if err >= 3 and div and grp:
        q = grp // div
        return (
            f"💡 La cifra correcta es <b>{q}</b>, porque {div}×{q}={div*q} es menor o igual que {grp} "
            f"y {div}×{q+1}={div*(q+1)} es mayor que {grp}."
        )
    return "Usa la tabla del divisor y elige la cifra más alta que no se pase."

def _div_resta_hint(context: str, err: int, cycle: str) -> str:
    """Pistas para la resta."""
    if err == 1:
        return (
            "👉 Resta el producto al grupo: grupo − (divisor × cifra del cociente). "
            + _question("¿Qué resto obtienes?")
        )
    if err == 2:
        return (
            "🧮 Escribe la resta en vertical para no confundirte. "
            "Recuerda que el resto debe ser <b>menor</b> que el divisor. "
            + _question("¿Cuál es el resto?")
        )
    if err >= 3:
        # MEJORADO: Más específico sobre cómo verificar
        m = re.search(r"resta:\s*<b>(\d+)</b>\s*−\s*<b>(\d+)×(\d+)</b>", context)
        if m:
            g, d, q = int(m.group(1)), int(m.group(2)), int(m.group(3))
            prod = d * q
            resto = g - prod
            return (
                f"💡 La resta es: {g} − {prod} = <b>{resto}</b>. "
                "Verifica tu cálculo cuidadosamente."
            )
        return (
            "💡 Comprueba que el resto sea menor que el divisor. "
            "Si no lo es, significa que la cifra del cociente era demasiado pequeña."
        )
    return "Resta el producto y verifica que el resto < divisor."

def _div_bajar_hint(context: str, err: int, cycle: str) -> str:
    """Pistas para bajar la siguiente cifra."""
    if err == 1:
        return (
            "👉 Baja la siguiente cifra del dividendo y júntala con el resto. "
            + _question("¿Qué nuevo número obtienes?")
        )
    if err == 2:
        return (
            "🧮 Piensa el nuevo número como: resto×10 + cifra bajada. "
            "Es como 'pegar' la cifra al final del resto. "
            + _question("¿Cuál es el nuevo grupo?")
        )
    if err >= 3:
        # MEJORADO: Extraer números específicos del contexto
        m_cifra = re.search(r"siguiente cifra:\s*<b>(\d+)</b>", context)
        m_resto = re.search(r"resto.*?<b>(\d+)</b>", context)
        if m_cifra and m_resto:
            cifra = m_cifra.group(1)
            resto = m_resto.group(1)
            nuevo = resto + cifra
            return (
                f"💡 El nuevo número es: {resto} + {cifra} bajada = <b>{nuevo}</b>. "
                "Ahora trabaja con este número."
            )
        return (
            "💡 Forma bien el nuevo número antes de elegir la siguiente cifra del cociente. "
            "Recuerda que es como si pegaras la cifra bajada al final del resto."
        )
    return "Baja la cifra y forma el nuevo número correctamente."

# ────────── Integración con OpenAI ──────────
try:
    from openai import OpenAI
    import os
    _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    _USE_AI = bool(os.getenv("OPENAI_API_KEY"))
except Exception:
    _client = None
    _USE_AI = False

PROMPT = (
    "Eres Tutorín (profesor de Primaria, LOMLOE). Da pistas concisas (1–2 frases) "
    "para divisiones paso a paso. No reveles la solución completa. "
    "Paso: {step} | Contexto: {context} | Respuesta: {answer} | Errores: {err}"
)

def _ai_hint(step: str, context: str, answer: str, err: int) -> Optional[str]:
    """Genera pista con OpenAI si err >= 2."""
    if not _USE_AI or not _client or err < 2:
        return None
    try:
        res = _client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "Eres un profesor de Primaria empático y paciente."},
                {"role": "user", "content": PROMPT.format(step=step, context=context, answer=answer, err=err)},
            ],
            temperature=0.4,
            max_tokens=120,
        )
        return (res.choices[0].message.content or "").strip()
    except Exception:
        return None

# ────────── Función principal (API pública) ──────────
def get_hint(hint_type: str, errors: int = 0, context: str = "", answer: str = "") -> str:
    """
    Genera pista para división según hint_type y nivel de error.
    Args:
        hint_type: 'div_grupo', 'div_qdigit', 'div_resta', 'div_bajar', 'div_resultado'
        errors: nivel de error (0-4+)
        context: contexto del motor
        answer: respuesta del alumno
    """
    ec = max(1, min(int(errors or 1), 4))
    # Intentar con IA
    ai = _ai_hint(hint_type, context, answer, ec)
    if ai:
        return ai
    # Fallback local
    if hint_type == "div_grupo":
        return _div_grupo_hint(context, ec, "c2")
    elif hint_type == "div_qdigit":
        return _div_qdigit_hint(context, ec, "c2")
    elif hint_type == "div_resta":
        return _div_resta_hint(context, ec, "c2")
    elif hint_type == "div_bajar":
        return _div_bajar_hint(context, ec, "c2")
    else:
        return "💡 Vamos paso a paso: elige el grupo, calcula la cifra, resta, baja la siguiente cifra y repite."
    