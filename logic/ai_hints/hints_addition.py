# -*- coding: utf-8 -*-
"""
hints_addition.py
Pistas de suma con bolitas de colores (emojis) adaptadas para todas las columnas
"""
import re

# Funciones de extraccion
def _extract_column_name(ctx: str) -> str:
    patterns = [
        r"(unidades|decenas|centenas|millares|decenas de millar|centenas de millar|millones)",
        r"columna de <b>(unidades|decenas|centenas|millares)</b>",
    ]
    for pattern in patterns:
        m = re.search(pattern, ctx, re.IGNORECASE)
        if m:
            return m.group(1).lower()
    return "unidades"

def _extract_digits_from_context(ctx: str):
    """Extrae los dígitos del contexto en diferentes formatos."""
    
    # Primero intentamos encontrar la llevada explícita en el contexto
    carry_match = re.search(r"lleva[sr]?\s+(\d+)|llevamos\s+(\d+)", ctx, re.IGNORECASE)
    found_carry = None
    if carry_match:
        found_carry = int(carry_match.group(1) or carry_match.group(2))
    
    # Formato: "¿Cuánto es 7 + 2 + lo que llevas?"
    m = re.search(r"[¿¡]?[Cc]u[aá]nto\s+es\s+(\d+)\s*\+\s*(\d+)\s*\+\s*lo\s+que\s+llevas", ctx)
    if m:
        d1, d2 = int(m.group(1)), int(m.group(2))
        if found_carry is not None:
            return (d1, d2, found_carry)
        return (d1, d2, 1)
    
    # Formato: "¿Cuánto es 7 + 2 + 1 (que llevas)?"
    m = re.search(r"[¿¡]?[Cc]u[aá]nto\s+es\s+(\d+)\s*\+\s*(\d+)\s*\+\s*(\d+)\s*\(", ctx)
    if m:
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    
    # Formato sin llevada: "¿Cuánto es 8 + 8?"
    m = re.search(r"[¿¡]?[Cc]u[aá]nto\s+es\s+(\d+)\s*\+\s*(\d+)[^+]", ctx)
    if m:
        return (int(m.group(1)), int(m.group(2)), 0)
    
    # Formato antiguo con llevada: "7+2 (+1 que llevas)"
    m = re.search(r"(\d+)\s*\+\s*(\d+)\s*(?:<b>)?\(\+(\d+)\s+que\s+llevas\)(?:</b>)?", ctx)
    if m:
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    
    # Formato antiguo: "7+2+1"
    m = re.search(r"(\d+)\s*\+\s*(\d+)\s*\+\s*(\d+)", ctx)
    if m:
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    
    # Formato antiguo sin llevada: "7+2"
    m = re.search(r"(\d+)\s*\+\s*(\d+)", ctx)
    if m:
        return (int(m.group(1)), int(m.group(2)), 0)
    
    return None

# Mapeo de columnas
def _get_column_info(column_name: str) -> dict:
    """Devuelve info de la columna actual y siguiente"""
    columns = {
        "unidades": {
            "nombre": "unidades",
            "siguiente": "decenas",
            "concepto": "10 unidades = 1 decena"
        },
        "decenas": {
            "nombre": "decenas", 
            "siguiente": "centenas",
            "concepto": "10 decenas = 1 centena"
        },
        "centenas": {
            "nombre": "centenas",
            "siguiente": "millares",
            "concepto": "10 centenas = 1 millar"
        },
        "millares": {
            "nombre": "millares",
            "siguiente": "decenas de millar",
            "concepto": "10 millares = 1 decena de millar"
        },
        "decenas de millar": {
            "nombre": "decenas de millar",
            "siguiente": "centenas de millar",
            "concepto": "10 decenas de millar = 1 centena de millar"
        },
        "centenas de millar": {
            "nombre": "centenas de millar",
            "siguiente": "millones",
            "concepto": "10 centenas de millar = 1 millon"
        }
    }
    return columns.get(column_name, columns["unidades"])

# Pista: Bolitas simples (PRIMERA PISTA PARA TODAS LAS SUMAS)
def _hint_simple_circles(d1: int, d2: int, carry: int, column_info: dict) -> str:
    """Primera pista: muestra bolitas sin agrupar"""
    col_name = column_info["nombre"]
    siguiente = column_info["siguiente"]
    
    circles = []
    
    if d1 > 0:
        circles.append("&#128309;" * d1 + f" ({d1})")
    if d2 > 0:
        circles.append("&#128994;" * d2 + f" ({d2})")
    if carry > 0:
        circles.append("&#128992;" * carry + f" ({carry} que llevas)")
    
    circles_display = "<br>".join(circles)
    
    total = d1 + d2 + carry
    all_circles = "&#9899;" * total
    
    # Texto adaptado según si pasa de 10 o no
    if total >= 10:
        hint_text = (
            f"<b>&#128161;</b> Cuenta cuantas bolitas hay en total. "
            f"Escribe solo el numero de las <b>{col_name}</b>, "
            f"el resto lo llevamos para la columna de <b>{siguiente}</b>."
        )
    else:
        hint_text = f"<b>&#128161;</b> Cuenta las bolitas y escribe ese numero en la columna de <b>{col_name}</b>."
    
    return (
        f"<div style='font-family:sans-serif;line-height:1.8;padding:10px;background:#f9fafb;border-radius:8px;font-size:1.1em'>"
        f"<b>&#127912;</b> <b>Te lo dibujo con bolitas de colores:</b><br>"
        f"{circles_display}<br>"
        f"<b>Total:</b> {all_circles}<br>"
        f"{hint_text}"
        f"</div>"
    )

# Pista: Bolitas agrupadas (SEGUNDA PISTA PARA SUMAS COMPLEJAS)
def _hint_3_grouped_circles(d1: int, d2: int, carry: int, column_info: dict) -> str:
    col_name = column_info["nombre"]
    siguiente = column_info["siguiente"]
    concepto = column_info["concepto"]
    
    total = d1 + d2 + carry
    groups_of_10 = total // 10
    remainder = total % 10
    
    circles = []
    
    if d1 > 0:
        circles.append("&#128309;" * d1 + f" ({d1})")
    if d2 > 0:
        circles.append("&#128994;" * d2 + f" ({d2})")
    if carry > 0:
        circles.append("&#128992;" * carry + f" ({carry} que llevas)")
    
    circles_display = "<br>".join(circles)
    
    result = "<b>Total agrupado:</b> "
    if groups_of_10 > 0:
        result += "[" + "&#128308;" * 10 + "]" * groups_of_10
        if remainder > 0:
            result += " + " + "&#9899;" * remainder
    else:
        result += "&#9899;" * remainder
    
    if groups_of_10 > 0:
        explanation = (
            f"<br><b>&#8594;</b> Hay <b style='color:#ef4444'>{groups_of_10} grupo(s) de 10</b> "
            f"y <b style='color:#6b7280'>{remainder} sueltas</b>.<br>"
            f"<b>&#128161; Recuerda:</b> {concepto}.<br>"
            f"Como no puedes escribir {total} en la columna de <b>{col_name}</b> porque solo cabe una cifra por columna, "
            f"escribimos solo las bolitas sueltas (<b>{remainder}</b>) y llevamos <b>{groups_of_10}</b> a la columna de <b>{siguiente}</b>."
        )
    else:
        explanation = (
            f"<br><b>&#8594;</b> Hay <b>{remainder} bolitas sueltas</b>.<br>"
            f"Como no hay grupos de 10, simplemente escribe <b>{remainder}</b> en la columna de <b>{col_name}</b>."
        )
    
    return (
        f"<div style='font-family:sans-serif;line-height:1.8;padding:10px;background:#fef3c7;border-radius:8px;font-size:1.1em'>"
        f"<b>&#127912;</b> <b>Te ayudo agrupando las bolitas de 10 en 10:</b><br>"
        f"{circles_display}<br>"
        f"{result}"
        f"{explanation}"
        f"</div>"
    )

# Pista: Solucion directa
def _hint_4_solution(d1: int, d2: int, carry: int, column_info: dict) -> str:
    col_name = column_info["nombre"]
    siguiente = column_info["siguiente"]
    
    total = d1 + d2 + carry
    digit = total % 10
    new_carry = total // 10
    
    if carry > 0:
        calc = f"{d1} + {d2} + {carry} = {total}"
    else:
        calc = f"{d1} + {d2} = {total}"
    
    if new_carry > 0:
        return (
            f"<div style='font-family:sans-serif;line-height:1.8;padding:10px;background:#dcfce7;border-radius:8px;font-size:1.1em'>"
            f"<b>&#9989;</b> {calc}<br>"
            f"<b>&#8594;</b> Escribe el <b>{digit}</b> en la columna de <b>{col_name}</b><br>"
            f"<b>&#8594;</b> Llevas <b>{new_carry}</b> a la columna de <b>{siguiente}</b>"
            f"</div>"
        )
    else:
        return (
            f"<div style='font-family:sans-serif;line-height:1.8;padding:10px;background:#dcfce7;border-radius:8px;font-size:1.1em'>"
            f"<b>&#9989;</b> {calc}<br>"
            f"<b>&#8594;</b> Escribe el <b>{digit}</b> en la columna de <b>{col_name}</b>"
            f"</div>"
        )

# Genera pistas progresivas
def _sum_col_hint_emoji(context: str, err: int) -> str:
    """Pistas con bolitas de colores (emojis) adaptadas por columna."""
    digits = _extract_digits_from_context(context)
    column_name = _extract_column_name(context)
    column_info = _get_column_info(column_name)
    
    if not digits:
        return "&#128073; Suma los numeros de la columna."
    
    d1, d2, carry = digits
    total = d1 + d2 + carry
    
    # Determinar si es suma simple o compleja
    is_simple = (total < 10 and carry == 0)
    
    # === PISTA 1: SIEMPRE BOLITAS (para todas las sumas) ===
    if err == 1:
        return _hint_simple_circles(d1, d2, carry, column_info)
    
    # === SUMA SIMPLE (resultado < 10 y sin llevada) ===
    if is_simple:
        # Pista 2+: Solución directa
        return _hint_4_solution(d1, d2, carry, column_info)
    
    # === SUMA COMPLEJA (resultado >= 10 o con llevada) ===
    else:
        if err == 2:
            # Pista 2: Bolitas agrupadas
            return _hint_3_grouped_circles(d1, d2, carry, column_info)
        else:
            # Pista 3+: Solución directa
            return _hint_4_solution(d1, d2, carry, column_info)

# Funcion publica - compatible con ai_router.py
def get_hint(step: str, error_count: int, context: str = "", answer: str = "") -> str:
    """
    Funcion publica para obtener pistas de suma con emojis.
    
    Args:
        step: El paso actual
        error_count: Cuantas veces se ha equivocado el nino
        context: El contexto del problema
        answer: La respuesta que dio el nino
    
    Returns:
        str: La pista en formato HTML con emojis de colores
    """
    return _sum_col_hint_emoji(context, error_count)

# Leyenda de colores
LEYENDA_EMOJI = """
<div style='padding:8px;background:#fff;border-radius:8px;margin:10px 0;font-size:0.9em'>
<b>&#127912; Codigo de colores:</b><br>
&#128309; Azul = Primer numero<br>
&#128994; Verde = Segundo numero<br>
&#128992; Naranja = Llevada<br>
&#128308; Rojo = Grupos de 10
</div>
"""