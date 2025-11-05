# -*- coding: utf-8 -*-
"""
hints_multiplication.py
Pistas progresivas pedagógicas para multiplicación DÍGITO POR DÍGITO.
Incluye detección especial para llevada final.
"""
import re
from typing import Optional

# ────────── Utilidades ──────────
def _extract_multiplication_from_context(context: str) -> Optional[tuple]:
    """
    Extrae la multiplicación que el motor está pidiendo.
    Busca patrones como: "Multiplica 5 × 3"
    Retorna: (digit_a, digit_b) o None
    """
    # Buscar patrón: "Multiplica X × Y"
    match = re.search(r'Multiplica\s+<b>(\d+)\s*×\s*(\d+)</b>', context)
    if match:
        digit_a = int(match.group(1))
        digit_b = int(match.group(2))
        return (digit_a, digit_b)
    
    return None

def _has_carry_mention(context: str) -> bool:
    """Detecta si se menciona que hay llevada."""
    return "llevada anterior" in context or "no olvides la llevada" in context

def _extract_position_from_context(context: str) -> str:
    """Extrae la posición actual."""
    positions = ["unidades de millar", "decenas de millar", "centenas", "decenas", "unidades"]
    for pos in positions:
        if f"las <b>{pos}</b>" in context:
            return pos
    return "esta columna"

def _asks_where_to_start(txt: str) -> bool:
    """Detecta si el alumno pregunta por dónde empezar."""
    if not txt: 
        return False
    t = txt.lower()
    return any(p in t for p in [
        "por qué número empie", "por que numero empie",
        "qué número empie", "que numero empie",
        "por dónde empie", "por donde empie",
        "dónde empie", "donde empie",
        "empiezo por", "cómo empiezo", "como empiezo"
    ])

# ────────── Pistas progresivas pedagógicas ──────────
def _mult_parcial_hint(context: str, err: int, cycle: str) -> str:
    """
    Pistas pedagógicas con andamiaje progresivo.
    Detecta si es llevada final y da pistas específicas.
    """
    # Detectar si pregunta por dónde empezar
    if _asks_where_to_start(context):
        return (
            "👉 Siempre empezamos por la <b>cifra de las unidades</b> del número de abajo "
            "(la que está más a la derecha). Después seguimos con decenas, centenas..."
        )
    
    # Detectar si es el caso de llevada final
    is_final_carry = "Solo queda anotar la llevada" in context or "Escribe la llevada que te quedó" in context
    
    if is_final_carry:
        # Pistas específicas para llevada final
        if err == 1:
            return "💡 Solo escribe la <b>llevada</b> que te quedó del paso anterior (un solo dígito)."
        if err == 2:
            return "🔢 Mira el último cálculo que hiciste. Si el resultado tenía dos cifras (por ejemplo, 15), la llevada es la cifra de las <b>decenas</b> (el 1)."
        if err == 3:
            return "✏️ Cuando el último paso dio un resultado de dos cifras, la cifra de las decenas es la que debes escribir ahora. Por ejemplo, si fue 15, escribe <b>1</b>."
        if err >= 4:
            return "📝 Escribe solo el <b>1</b> (la llevada del paso anterior)."
    
    # Extraer la multiplicación del contexto (caso normal)
    mult = _extract_multiplication_from_context(context)
    if not mult:
        return "💡 Piensa en las tablas de multiplicar. Escribe solo la cifra de las unidades."
    
    digit_a, digit_b = mult
    has_carry = _has_carry_mention(context)
    position = _extract_position_from_context(context)
    
    # Calcular resultado
    product = digit_a * digit_b
    write_digit = product % 10
    carry_next = product // 10
    
    # Nivel 1: Referencia a las tablas (sin dar resultado)
    if err == 1:
        if not has_carry:
            return (
                f"💡 Piensa en la <b>tabla del {digit_b}</b>. "
                f"Escribe la cifra de las <b>unidades</b> y recuerda lo que te llevas."
            )
        else:
            return (
                f"💡 Primero usa la <b>tabla del {digit_b}</b>, luego suma lo que te llevabas del paso anterior. "
                f"Escribe solo la cifra de las unidades."
            )
    
    # Nivel 2: Muestra la tabla (deja que busque)
    if err == 2:
        # Construir tabla hasta el número necesario
        table_items = [f"{digit_b}×{i}={digit_b*i}" for i in range(1, min(11, digit_a + 2))]
        table_str = ", ".join(table_items)
        
        if not has_carry:
            return (
                f"📊 Tabla del {digit_b}: {table_str}...<br/>"
                f"Busca <b>{digit_a}×{digit_b}</b> y anota la cifra de las <b>unidades</b>. "
                f"Si el resultado tiene dos cifras, te llevas la de las decenas."
            )
        else:
            return (
                f"📊 Tabla del {digit_b}: {table_str}...<br/>"
                f"Encuentra <b>{digit_a}×{digit_b}</b>, suma la llevada anterior, "
                f"y escribe solo la cifra de las unidades."
            )
    
    # Nivel 3: Da el cálculo pero hace pensar en unidades/llevadas
    if err == 3:
        if not has_carry:
            msg = f"🧮 <b>{digit_a} × {digit_b} = {product}</b>. "
            if product >= 10:
                msg += f"Como tiene dos cifras, escribes <b>{write_digit}</b> (unidades) y te llevas <b>{carry_next}</b> (decenas)."
            else:
                msg += f"Escribes <b>{write_digit}</b>."
            return msg
        else:
            # Con llevada anterior - intentar inferir
            for possible_carry in [1, 2, 3, 4]:
                total = product + possible_carry
                # Buscamos una llevada que tenga sentido pedagógicamente
                if 10 <= total <= 30:  # Rango razonable
                    msg = f"🧮 Primero: <b>{digit_a} × {digit_b} = {product}</b>. "
                    msg += f"Luego sumas la llevada anterior (que seguramente es <b>{possible_carry}</b>): {product} + {possible_carry} = {total}. "
                    msg += f"Escribes <b>{total % 10}</b> (unidades)"
                    if total // 10 > 0:
                        msg += f" y te llevas <b>{total // 10}</b> (decenas)."
                    else:
                        msg += "."
                    return msg
            
            # Fallback genérico si no encontramos llevada razonable
            msg = f"🧮 Primero: <b>{digit_a} × {digit_b} = {product}</b>. "
            msg += f"Luego suma la llevada del paso anterior. Escribe solo la cifra de las unidades del total."
            return msg
    
    # Nivel 4: Solución completa
    if err >= 4:
        if not has_carry:
            msg = f"✏️ <b>{digit_a} × {digit_b} = {product}</b>. "
            if carry_next > 0:
                msg += f"Escribes <b>{write_digit}</b> en {position} y te llevas <b>{carry_next}</b>."
            else:
                msg += f"Escribes <b>{write_digit}</b> en {position}."
            return msg
        else:
            # Con llevada - intentar inferir la correcta
            for possible_carry in [1, 2, 3, 4]:
                total = product + possible_carry
                if 10 <= total <= 30:
                    msg = f"✏️ <b>{digit_a} × {digit_b} = {product}</b>, "
                    msg += f"más la llevada ({possible_carry}): {product} + {possible_carry} = {total}. "
                    msg += f"Escribes <b>{total % 10}</b>"
                    if total // 10 > 0:
                        msg += f" y te llevas <b>{total // 10}</b>."
                    else:
                        msg += "."
                    return msg
            
            # Fallback
            return (
                f"✏️ <b>{digit_a} × {digit_b} = {product}</b>. "
                f"Suma la llevada anterior, escribe el dígito de las unidades del total."
            )
    
    return "💡 Usa las tablas de multiplicar. Escribe solo la cifra de las unidades."


def _mult_suma_hint(context: str, err: int, cycle: str) -> str:
    """Pistas para sumar las líneas parciales."""
    if err == 1:
        return (
            "👉 Suma todas las líneas parciales columna por columna, <b>de derecha a izquierda</b>. "
            "Empieza por las unidades. ¿Qué total obtienes?"
        )
    if err == 2:
        return (
            "🧮 Suma en vertical. Ten cuidado con las <b>llevadas</b> "
            "(cuando la suma de una columna pasa de 9). ¿Cuál es el resultado?"
        )
    if err == 3:
        return (
            "💡 Haz una <b>estimación rápida</b>: redondea los números y multiplica mentalmente. "
            "Si tu resultado está muy lejos, revisa la suma columna por columna."
        )
    return (
        "✅ Repasa la suma de cada columna de derecha a izquierda. "
        "Comprueba bien las llevadas. Si no cuadra, revisa las líneas parciales."
    )


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
    "Eres Tutorín (profesor de Primaria, LOMLOE). Da pistas pedagógicas y progresivas (1–2 frases cortas), "
    "amables y motivadoras. No des la respuesta directa a menos que sea el error 4+. "
    "Paso: {step} | Contexto: {context} | Respuesta: {answer} | Errores: {err}"
)

def _ai_hint(step: str, context: str, answer: str, err: int) -> Optional[str]:
    """Genera pista usando OpenAI si está disponible y err >= 3."""
    if not _USE_AI or not _client or err < 3:
        return None
    try:
        res = _client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "Eres un profesor de Primaria empático, claro y paciente."},
                {"role": "user", "content": PROMPT.format(step=step, context=context, answer=answer, err=err)},
            ],
            temperature=0.4,
            max_tokens=120,
        )
        txt = (res.choices[0].message.content or "").strip()
        return txt
    except Exception:
        return None


# ────────── Función principal ──────────
def get_hint(hint_type: str, errors: int = 0, context: str = "", answer: str = "") -> str:
    """
    Genera pista pedagógica según hint_type y nivel de error.
    Args:
        hint_type: 'mult_parcial', 'mult_suma', 'mult_resultado'
        errors: nivel de error (0-4+)
        context: contexto del motor
        answer: respuesta del alumno
    """
    ec = max(1, min(int(errors or 1), 4))
    
    # Intentar con IA si err >= 3
    ai = _ai_hint(hint_type, context, answer, ec)
    if ai:
        return ai
    
    # Fallback a pistas locales
    if hint_type == "mult_parcial":
        return _mult_parcial_hint(context, ec, "c2")
    elif hint_type in ("mult_suma", "mult_total", "mult_resultado"):
        return _mult_suma_hint(context, ec, "c2")
    else:
        return "💡 Piensa paso a paso usando las tablas de multiplicar."