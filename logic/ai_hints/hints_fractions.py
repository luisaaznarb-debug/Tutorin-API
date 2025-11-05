# -*- coding: utf-8 -*-
"""
hints_fractions.py
Pistas progresivas para fracciones según nivel de error.
CORREGIDO: Las pistas NO revelan la respuesta
Compatible con fractions_engine.py
"""

from .hints_utils import _extract_pre_block, _lcm, _question
import re
import math
from typing import Optional, Tuple

# ────────── Utilidades ──────────
def _parse_two_fractions(ctx: str):
    """Lee dos fracciones A/B (op) C/D desde el contexto."""
    text = ctx or ""

    # Marcador oculto
    m = re.search(r"\[FRAC:\s*(\d+)\s*/\s*(\d+)\s*([+\-])\s*(\d+)\s*/\s*(\d+)\s*\]", text)
    if m:
        a, b, op, c, d = int(m.group(1)), int(m.group(2)), m.group(3), int(m.group(4)), int(m.group(5))
        return ((a, b), (c, d), op)

    # Desde el <pre>
    pre = _extract_pre_block(text) or ""
    m = re.search(r"(\d+)\s*/\s*(\d+)\s*([+\-])\s*(\d+)\s*/\s*(\d+)", pre)
    if m:
        a, b, op, c, d = int(m.group(1)), int(m.group(2)), m.group(3), int(m.group(4)), int(m.group(5))
        return ((a, b), (c, d), op)

    # Fallback
    m = re.search(r"(\d+)\s*/\s*(\d+)\s*([+\-])\s*(\d+)\s*/\s*(\d+)", text)
    if m:
        a, b, op, c, d = int(m.group(1)), int(m.group(2)), m.group(3), int(m.group(4)), int(m.group(5))
        return ((a, b), (c, d), op)

    return None

# ────────── Pistas por subpaso ──────────

def _frac_inicio_hint(context: str, err: int, cycle: str) -> str:
    """Pistas para comparar denominadores (sí/no)."""
    pf = _parse_two_fractions(context)
    if pf:
        (a, b), (c, d), _ = pf
        correcta = "sí" if b == d else "no"
    else:
        b, d, correcta = 3, 5, "no"

    if err == 1:
        return (
            "👉 Fíjate bien: el <b>denominador</b> es el número de <b>abajo</b> en cada fracción. "
            + _question("¿Son iguales?")
        )
    
    if err == 2:
        return (
            f"🧮 Mira solo los números de abajo: <b>{b}</b> y <b>{d}</b>. "
            + _question("¿Coinciden exactamente?")
        )
    
    if err == 3:
        return (
            f"💡 Denominadores: {b} y {d}. "
            "Si son iguales, responde 'sí'; si no, responde 'no'. "
            "No te confundas con los numeradores (los de arriba)."
        )
    
    if err >= 4:
        return f"✅ Respuesta correcta: <b>{correcta}</b>."
    
    return "Compara solo los denominadores."

def _frac_mcm_hint(context: str, err: int, cycle: str) -> str:
    """Pistas para calcular el m.c.m."""
    pf = _parse_two_fractions(context)
    if pf:
        (a, b), (c, d), _ = pf
    else:
        b, d = 3, 5
    
    m = _lcm(b, d)
    
    if err == 1:
        return (
            f"👉 El m.c.m. es el <b>primer múltiplo común</b> de {b} y {d}. "
            "Haz dos listas de múltiplos hasta encontrar el primero que se repite. "
            + _question("¿Cuál te sale?")
        )
    
    if err == 2:
        return (
            f"🧮 Escribe los múltiplos de <b>{b}</b>: {b}, {b*2}, {b*3}, {b*4}, {b*5}...\n"
            f"Escribe los múltiplos de <b>{d}</b>: {d}, {d*2}, {d*3}, {d*4}, {d*5}...\n"
            + _question("¿Cuál es el primer número que coincide?")
        )
    
    if err == 3:
        multiples_b = ', '.join(str(b*i) for i in range(1, 7))
        multiples_d = ', '.join(str(d*i) for i in range(1, 7))
        return (
            f"💡 Múltiplos de {b}: {multiples_b}\n"
            f"Múltiplos de {d}: {multiples_d}\n"
            + _question("¿Cuál es el primer número que aparece en ambas listas?")
        )
    
    if err >= 4:
        return f"✅ El m.c.m.({b},{d}) = <b>{m}</b>. Úsalo como denominador común."
    
    return "Busca el primer múltiplo común de ambos denominadores."

def _frac_equiv_hint(context: str, err: int, cycle: str) -> str:
    """Pistas para calcular fracciones equivalentes."""
    pf = _parse_two_fractions(context)
    if not pf:
        return "👉 Convierte ambas fracciones al mismo denominador usando el m.c.m."
    
    (a, b), (c, d), _ = pf
    m = _lcm(b, d)
    kb, kd = (m // b), (m // d)
    A, C = a * kb, c * kd

    if err == 1:
        return (
            f"👉 Multiplica el <b>numerador</b> por el mismo número que multiplicaste "
            f"el denominador para llegar a {m}. "
            + _question("¿Qué numeradores obtienes?")
        )
    
    if err == 2:
        return (
            f"🧮 En la primera fracción, multiplicaste el denominador por <b>{kb}</b> "
            f"(porque {b} × {kb} = {m}). "
            f"Ahora multiplica el numerador {a} por ese mismo <b>{kb}</b>.\n"
            f"En la segunda fracción, multiplica {c} por <b>{kd}</b>. "
            + _question("¿Qué numeradores te salen?")
        )
    
    if err == 3:
        return (
            f"💡 Recuerda la regla:\n"
            f"Para {a}/{b}: divide {m} entre {b}, eso te da <b>{kb}</b>. "
            f"Multiplica el numerador {a} por <b>{kb}</b>.\n"
            f"Para {c}/{d}: divide {m} entre {d}, eso te da <b>{kd}</b>. "
            f"Multiplica el numerador {c} por <b>{kd}</b>.\n"
            + _question("¿Qué numeradores obtienes?")
        )
    
    if err >= 4:
        return (
            f"✅ Perfecto. Los nuevos numeradores son:\n"
            f"<b>{A} y {C}</b>\n"
            f"(Fracciones equivalentes: <b>{A}/{m}</b> y <b>{C}/{m}</b>)"
        )
    
    return "Multiplica cada numerador por el factor correspondiente."

def _frac_operacion_hint(context: str, err: int, cycle: str) -> str:
    """Pistas para operar los numeradores."""
    pf = _parse_two_fractions(context)
    if not pf:
        return "👉 Opera los numeradores y conserva el denominador común."
    
    (a, b), (c, d), op = pf
    m = _lcm(b, d)
    kb, kd = m // b, m // d
    a2, c2 = a * kb, c * kd
    num = a2 + c2 if op == "+" else a2 - c2

    if err == 1:
        return (
            f"👉 Ya tienen denominador común ({m}). "
            f"Opera <b>solo los numeradores</b>. "
            + _question(f"¿Cuánto es {a2} {op} {c2}?")
        )
    
    if err == 2:
        return (
            f"🧮 El denominador queda igual (<b>{m}</b>). "
            f"Solo tienes que {'sumar' if op == '+' else 'restar'} los numeradores. "
            + _question(f"Calcula: {a2} {op} {c2}")
        )
    
    if err == 3:
        return (
            f"💡 Hazlo paso a paso:\n"
            f"Numerador 1: {a2}\n"
            f"Numerador 2: {c2}\n"
            f"Operación: {a2} {op} {c2}\n"
            + _question("¿Qué resultado obtienes?")
        )
    
    if err >= 4:
        return (
            f"✅ Resultado de la operación:\n"
            f"{a2} {op} {c2} = <b>{num}</b>\n"
            f"Fracción resultante: <b>{num}/{m}</b> (sin simplificar)."
        )
    
    return "Opera solo los numeradores, el denominador no cambia."

def _frac_simplificar_hint(context: str, err: int, cycle: str) -> str:
    """Pistas para simplificar fracciones."""
    m = re.search(r"\[FRAC:\s*(\d+)\s*/\s*(\d+)\s*([+\-])\s*(\d+)\s*/\s*(\d+)\s*\]", context or "")
    if m:
        a, b, op, c, d = int(m.group(1)), int(m.group(2)), m.group(3), int(m.group(4)), int(m.group(5))
        mcm = _lcm(b, d)
        kb, kd = mcm // b, mcm // d
        A, C = a * kb, c * kd
        n = A + C if op == "+" else A - C
        den = mcm
        g = math.gcd(n, den)
    else:
        txt = _extract_pre_block(context) or ""
        all_fracs = re.findall(r"(\d+)\s*/\s*(\d+)", txt)
        if not all_fracs:
            n, den, g = 32, 24, math.gcd(32, 24)
        else:
            n, den = map(int, all_fracs[-1])
            g = math.gcd(n, den)

    # Marcador para persistir el GCD
    marker = f"<span style='display:none'>[GCD:{g}]</span>"

    if g == 1:
        return (
            f"✅ No se puede simplificar más, ya que {n} y {den} "
            "no tienen divisores comunes mayores que 1."
        )

    if err == 1:
        return (
            f"👉 Busca un número mayor que 1 que divida tanto a <b>{n}</b> como a <b>{den}</b>. "
            + _question("¿Qué número puedes usar como divisor común?")
            + marker
        )
    
    if err == 2:
        return (
            f"🧮 Piensa: ¿qué número divide exactamente a {n} y también a {den}? "
            "Prueba con 2, 3, 5, 7... "
            + _question("¿Cuál encuentras?")
            + marker
        )
    
    if err == 3:
        return (
            f"💡 Busca el máximo común divisor (M.C.D.) de {n} y {den}. "
            f"Una pista: prueba dividir ambos por <b>{g}</b>. "
            + _question("¿Qué fracción obtienes después de dividir?")
            + marker
        )
    
    if err >= 4:
        return (
            f"✅ La fracción simplificada es:\n"
            f"{n} ÷ {g} = {n // g}\n"
            f"{den} ÷ {g} = {den // g}\n"
            f"Respuesta: <b>{n // g}/{den // g}</b>"
        )
    
    return "Divide numerador y denominador por el MCD."

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
    "para operaciones con fracciones. No reveles la solución completa. "
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
    Genera pista para fracciones según hint_type y nivel de error.
    
    Args:
        hint_type: 'frac_inicio', 'frac_mcm', 'frac_equiv', 'frac_operacion', 'frac_simplificar'
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
    if hint_type == "frac_inicio":
        return _frac_inicio_hint(context, ec, "c2")
    elif hint_type == "frac_mcm":
        return _frac_mcm_hint(context, ec, "c2")
    elif hint_type == "frac_equiv":
        return _frac_equiv_hint(context, ec, "c2")
    elif hint_type == "frac_operacion":
        return _frac_operacion_hint(context, ec, "c2")
    elif hint_type == "frac_simplificar":
        return _frac_simplificar_hint(context, ec, "c2")
    else:
        return "Dime qué parte no entiendes (m.c.m., numeradores, operación o simplificar)."