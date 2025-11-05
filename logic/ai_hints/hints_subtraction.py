# -*- coding: utf-8 -*-
"""
hints_subtraction.py
Pistas de resta con bolitas de colores (emojis) - adaptado para todas las columnas
"""
import re

# Funciones de extracción
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
    
    # Formato: "¿Cuánto es 7 - 1 (que prestamos) - 2?"
    m = re.search(r"[¿¡]?[Cc]u[aá]nto\s+es\s+(\d+)\s*-\s*(\d+)\s*\(que\s+prestamos\)\s*-\s*(\d+)", ctx)
    if m:
        return (int(m.group(1)), int(m.group(3)), int(m.group(2)))  # d1, d2, borrow
    
    # Formato: "¿Cuánto es 8 - 2?"
    m = re.search(r"[¿¡]?[Cc]u[aá]nto\s+es\s+(\d+)\s*-\s*(\d+)", ctx)
    if m:
        return (int(m.group(1)), int(m.group(2)), 0)
    
    # Formato antiguo: "7-2"
    m = re.search(r"(\d+)\s*-\s*(\d+)", ctx)
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
            "concepto": "Pedir prestado significa tomar 10 de la siguiente columna"
        },
        "decenas": {
            "nombre": "decenas", 
            "siguiente": "centenas",
            "concepto": "Pedir prestado significa tomar 10 decenas (100 unidades) de las centenas"
        },
        "centenas": {
            "nombre": "centenas",
            "siguiente": "millares",
            "concepto": "Pedir prestado significa tomar 10 centenas de los millares"
        },
        "millares": {
            "nombre": "millares",
            "siguiente": "decenas de millar",
            "concepto": "Pedir prestado significa tomar 10 millares"
        }
    }
    return columns.get(column_name, columns["unidades"])

# Pista 1: Explicación conceptual del préstamo
def _hint_1_borrow_explanation(d1: int, d2: int, borrow: int, column_info: dict) -> str:
    """Primera pista: explica el préstamo previo y el nuevo préstamo si es necesario"""
    col_name = column_info["nombre"]
    siguiente = column_info["siguiente"]
    
    actual_d1 = d1 - borrow
    
    if actual_d1 >= d2:
        # No necesita préstamo nuevo
        if borrow > 0:
            original_circles = "&#128309;" * d1
            remaining_after_borrow = "&#128309;" * actual_d1
            
            return (
                f"<div style='font-family:sans-serif;line-height:1.8;padding:10px;background:#fff3cd;border-radius:8px;font-size:1.1em'>"
                f"<b>&#127912;</b> <b>Te lo explico paso a paso:</b><br>"
                f"<br>"
                f"<b>1. Teníamos:</b> {original_circles} ({d1} en la columna de <b>{col_name}</b>)<br>"
                f"<br>"
                f"<b>2. Pero prestamos 1 a la columna anterior</b><br>"
                f"<br>"
                f"<b>3. Ahora nos queda:</b> {remaining_after_borrow} ({actual_d1})<br>"
                f"<br>"
                f"<b>&#128161;</b> ¿Cuánto es {actual_d1} - {d2}?<br>"
                f"Escribe el numero en la columna de <b>{col_name}</b>."
                f"</div>"
            )
        else:
            all_circles = "&#128309;" * actual_d1
            
            return (
                f"<div style='font-family:sans-serif;line-height:1.8;padding:10px;background:#fff3cd;border-radius:8px;font-size:1.1em'>"
                f"<b>&#127912;</b> <b>Te lo dibujo con bolitas:</b><br>"
                f"<b>Tenemos:</b> {all_circles} ({actual_d1} bolitas)<br>"
                f"<br>"
                f"<b>&#128161;</b> ¿Cuánto es {actual_d1} - {d2}?<br>"
                f"Escribe el numero en la columna de <b>{col_name}</b>."
                f"</div>"
            )
    else:
        # Necesita préstamo nuevo
        borrowed_d1 = actual_d1 + 10
        
        if borrow > 0:
            original_circles = "&#128309;" * d1
            remaining_after_borrow = "&#128309;" * actual_d1 if actual_d1 > 0 else "ninguna"
            borrowed_group = "[" + "&#128308;" * 10 + "]"
            
            return (
                f"<div style='font-family:sans-serif;line-height:1.8;padding:10px;background:#fff3cd;border-radius:8px;font-size:1.1em'>"
                f"<b>&#127912;</b> <b>Te lo explico paso a paso:</b><br>"
                f"<br>"
                f"<b>1. Teníamos:</b> {original_circles} ({d1} en la columna de <b>{col_name}</b>)<br>"
                f"<br>"
                f"<b>2. Pero prestamos 1 a la columna anterior</b><br>"
                f"<br>"
                f"<b>3. Ahora nos queda:</b> {remaining_after_borrow} ({actual_d1})<br>"
                f"<br>"
                f"<b>4. ¿Por qué pedimos prestado de nuevo?</b><br>"
                f"Porque solo tenemos <b>{actual_d1}</b> y necesitamos quitar <b>{d2}</b>.<br>"
                f"<b>{actual_d1} &lt; {d2}</b> → ¡No tenemos suficientes!<br>"
                f"<br>"
                f"<b>5. Pedimos prestado:</b> {borrowed_group} (10 más de la columna de <b>{siguiente}</b>)<br>"
                f"<br>"
                f"<b>6. Ahora tenemos {actual_d1} + 10 = {borrowed_d1}</b><br>"
                f"<br>"
                f"<b>&#128161;</b> ¿Cuánto es {borrowed_d1} - {d2}?<br>"
                f"Escribe el numero de las <b>{col_name}</b> y recuerda que has pedido prestado 1 a las <b>{siguiente}</b>."
                f"</div>"
            )
        else:
            original_circles = "&#128309;" * actual_d1 if actual_d1 > 0 else "ninguna"
            borrowed_group = "[" + "&#128308;" * 10 + "]"
            
            return (
                f"<div style='font-family:sans-serif;line-height:1.8;padding:10px;background:#fff3cd;border-radius:8px;font-size:1.1em'>"
                f"<b>&#127912;</b> <b>Te lo explico paso a paso:</b><br>"
                f"<br>"
                f"<b>1. Teníamos:</b> {original_circles} ({actual_d1} {'bolita' if actual_d1 == 1 else 'bolitas'})<br>"
                f"<br>"
                f"<b>2. ¿Por qué pedimos prestado?</b><br>"
                f"Porque solo tenemos <b>{actual_d1}</b> y necesitamos quitar <b>{d2}</b>.<br>"
                f"<b>{actual_d1} &lt; {d2}</b> → ¡No tenemos suficientes!<br>"
                f"<br>"
                f"<b>3. Pedimos prestado:</b> {borrowed_group} (10 más de la columna de <b>{siguiente}</b>)<br>"
                f"<br>"
                f"<b>4. Ahora tenemos {actual_d1} + 10 = {borrowed_d1} bolitas</b><br>"
                f"<br>"
                f"<b>&#128161;</b> ¿Cuánto es {borrowed_d1} - {d2}?<br>"
                f"Escribe el numero de las <b>{col_name}</b> y recuerda que has pedido prestado 1 a las <b>{siguiente}</b>."
                f"</div>"
            )

# Pista 2: Visualización con bolitas tachadas
def _hint_2_visual_circles(d1: int, d2: int, borrow: int, column_info: dict) -> str:
    """Segunda pista: muestra bolitas tachadas y sin tachar"""
    col_name = column_info["nombre"]
    siguiente = column_info["siguiente"]
    
    actual_d1 = d1 - borrow
    
    if actual_d1 >= d2:
        result = actual_d1 - d2
        
        crossed = "&#10683;" * d2
        remaining = "&#128309;" * result
        
        all_circles = crossed + " " + remaining if result > 0 else crossed
        
        return (
            f"<div style='font-family:sans-serif;line-height:1.8;padding:10px;background:#fff3cd;border-radius:8px;font-size:1.1em'>"
            f"<b>&#127912;</b> <b>Tenemos {actual_d1} bolitas y queremos quitar {d2}:</b><br>"
            f"{all_circles}<br>"
            f"<br>"
            f"<b>&#10683;</b> = Tachadas ({d2} que quitamos)<br>"
            f"<b>&#128309;</b> = Sin tachar ({result} que quedan)<br>"
            f"<br>"
            f"<b>&#128161;</b> Cuenta cuantas NO están tachadas y escribe ese numero."
            f"</div>"
        )
    else:
        borrowed_d1 = actual_d1 + 10
        result = borrowed_d1 - d2
        
        crossed = "&#10683;" * d2
        remaining = "&#128309;" * result
        
        all_circles = crossed + " " + remaining
        
        return (
            f"<div style='font-family:sans-serif;line-height:1.8;padding:10px;background:#fff3cd;border-radius:8px;font-size:1.1em'>"
            f"<b>&#127912;</b> <b>Tenemos {borrowed_d1} bolitas y queremos quitar {d2}:</b><br>"
            f"{all_circles}<br>"
            f"<br>"
            f"<b>&#10683;</b> = Tachadas ({d2} que quitamos)<br>"
            f"<b>&#128309;</b> = Sin tachar ({result} que quedan)<br>"
            f"<br>"
            f"<b>&#128161;</b> Cuenta cuantas NO están tachadas y escribe ese numero.<br>"
            f"No olvides restar 1 en la columna de <b>{siguiente}</b>."
            f"</div>"
        )

# Pista 3: Solución directa
def _hint_3_solution(d1: int, d2: int, borrow: int, column_info: dict) -> str:
    """Tercera pista: solución directa con cálculo"""
    col_name = column_info["nombre"]
    siguiente = column_info["siguiente"]
    
    actual_d1 = d1 - borrow
    
    if actual_d1 >= d2:
        result = actual_d1 - d2
        if borrow > 0:
            calc = f"{d1} - {borrow} (prestado) - {d2} = {result}"
        else:
            calc = f"{d1} - {d2} = {result}"
        
        return (
            f"<div style='font-family:sans-serif;line-height:1.8;padding:10px;background:#dcfce7;border-radius:8px;font-size:1.1em'>"
            f"<b>&#9989;</b> {calc}<br>"
            f"<b>&#8594;</b> Escribe el <b>{result}</b> en la columna de <b>{col_name}</b>"
            f"</div>"
        )
    else:
        borrowed_d1 = actual_d1 + 10
        result = borrowed_d1 - d2
        
        return (
            f"<div style='font-family:sans-serif;line-height:1.8;padding:10px;background:#dcfce7;border-radius:8px;font-size:1.1em'>"
            f"<b>&#9989;</b> La respuesta es <b>{result}</b><br>"
            f"<br>"
            f"<b>Cálculo:</b><br>"
            f"• Teníamos: {d1}<br>"
            f"• Prestamos a columna anterior: -{borrow if borrow > 0 else 0}<br>"
            f"• Nos quedó: {actual_d1}<br>"
            f"• Pedimos prestado: +10<br>"
            f"• Total: {borrowed_d1}<br>"
            f"• Restamos: {borrowed_d1} - {d2} = <b>{result}</b><br>"
            f"<br>"
            f"<b>&#8594;</b> Escribe el <b>{result}</b> en la columna de <b>{col_name}</b><br>"
            f"<b>&#8594;</b> No olvides restar 1 en la columna de <b>{siguiente}</b>"
            f"</div>"
        )

# Genera pistas progresivas
def _sub_col_hint_visual(context: str, err: int) -> str:
    """Pistas con bolitas de colores adaptadas por columna."""
    digits = _extract_digits_from_context(context)
    column_name = _extract_column_name(context)
    column_info = _get_column_info(column_name)
    
    if not digits:
        return "&#128073; Resta los numeros de la columna."
    
    d1, d2, borrow = digits
    
    if err == 1:
        return _hint_1_borrow_explanation(d1, d2, borrow, column_info)
    
    if err == 2:
        return _hint_2_visual_circles(d1, d2, borrow, column_info)
    
    if err >= 3:
        return _hint_3_solution(d1, d2, borrow, column_info)
    
    return "Resta los numeros de la columna."

# Función pública
def get_hint(step: str, error_count: int, context: str = "", answer: str = "") -> str:
    return _sub_col_hint_visual(context, error_count)
