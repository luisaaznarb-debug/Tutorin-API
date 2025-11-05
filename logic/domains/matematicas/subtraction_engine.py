# -*- coding: utf-8 -*-
from typing import List, Tuple, Optional
import re

# ═══════════════════════════════════════════════════════════════
# SISTEMA DE PISTAS
# ═══════════════════════════════════════════════════════════════

HELP_KEYWORDS = [
    "no se", "no sé", "nose", "nosé", "no lo se", "no lo sé",
    "no entiendo", "no comprendo", "ayuda", "ayudame", "ayúdame",
    "pista", "dame una pista", "necesito ayuda"
]

def _is_asking_for_help(user_answer: str) -> bool:
    """Detecta si el usuario está pidiendo ayuda"""
    if not user_answer:
        return False
    answer_clean = user_answer.lower().strip()
    for keyword in HELP_KEYWORDS:
        if keyword in answer_clean:
            return True
    return answer_clean in ["?", "??", "???", "...", "..", "."]

def _generate_hint(hint_type: str, error_count: int, context: str, topic: str) -> str:
    """Genera una pista usando el sistema de hints"""
    try:
        # Importar la función get_hint del módulo correspondiente
        if topic == "resta":
            from logic.ai_hints.hints_subtraction import get_hint
        else:
            return "💡 Pista: piensa paso a paso y revisa los números."
        
        e = max(1, min(int(error_count), 9))
        return get_hint(hint_type, e, context, "")
        
    except Exception as e:
        print(f"[{topic.upper()}_ENGINE] ⚠️ Error generando pista: {e}")
        return "💡 Pista: piensa paso a paso y revisa los números cuidadosamente."
    
# ═══════════════════════════════════════════════════════════════
# FUNCIONES AUXILIARES
# ═══════════════════════════════════════════════════════════════

_PLACES = [
    "unidades", "decenas", "centenas", "millares", "decenas de millar",
    "centenas de millar", "millones"
]

# Mapeo de nombres de columnas siguientes
_NEXT_PLACES = {
    "unidades": "decenas",
    "decenas": "centenas",
    "centenas": "millares",
    "millares": "decenas de millar",
    "decenas de millar": "centenas de millar",
    "centenas de millar": "millones"
}

def _place_name(k: int) -> str:
    return _PLACES[k] if k < len(_PLACES) else f"posición {k}"

def _next_place_name(k: int) -> str:
    current = _place_name(k)
    return _NEXT_PLACES.get(current, "siguiente columna")

def _normalize(text: str) -> str:
    return (
        text.replace("∑", "-")
        .replace("–", "-")
        .replace("—", "-")
        .replace("÷", "/")
        .replace("×", "*")
        .replace("·", "*")
    )

def _detect(question: str) -> Optional[Tuple[int, int]]:
    q = _normalize(question)
    m = re.search(r"(\d+)\s*-\s*(\d+)", q)
    return (int(m.group(1)), int(m.group(2))) if m else None

def _digits_rev(n: int) -> List[int]:
    return [int(ch) for ch in str(n)][::-1]

def _compute_columns(a: int, b: int):
    A = _digits_rev(a)
    B = _digits_rev(b)
    n = max(len(A), len(B))
    cols = []
    borrow = 0
    for k in range(n):
        d1 = A[k] if k < len(A) else 0
        d2 = B[k] if k < len(B) else 0
        
        # Restar el préstamo de la columna anterior
        actual_d1 = d1 - borrow
        
        if actual_d1 < d2:
            # Necesitamos pedir prestado
            digit = actual_d1 + 10 - d2
            borrow = 1
        else:
            digit = actual_d1 - d2
            borrow = 0
        
        needs_borrow = (actual_d1 < d2)
        cols.append((d1, d2, borrow, digit, _place_name(k), needs_borrow))
    
    return cols

def _width(a: int, b: int) -> int:
    result = a - b
    return max(len(str(a)), len(str(b)) + 2, len(str(result))) + 2

def _board(a: int, b: int, solved_digits: List[int], show_line: bool = False) -> str:
    w = _width(a, b)
    rj = lambda s: s.rjust(w)
    lines = [rj(str(a)), rj("- " + str(b)), rj("-" * max(len(str(a)), len(str(b)) + 2))]
    partial = "".join(str(d) for d in solved_digits[::-1])
    lines.append(rj(partial))
    if show_line:
        lines.append(rj("-" * max(len(partial), 1)))
    return (
        "<pre style='font-family:monospace;line-height:1.25;margin:6px 0 0 0'>"
        + "\n".join(lines)
        + "</pre>"
    )

def _draw_simple_circles(d1: int, d2: int) -> str:
    """Dibuja bolitas para restas simples (un dígito - un dígito)"""
    total_circles = "&#128309;" * d1
    crossed_circles = "&#10060;" * d2
    remaining = d1 - d2
    remaining_circles = "&#9989;" * remaining if remaining > 0 else ""
    
    return (
        f"<div style='font-family:sans-serif;line-height:1.8;padding:10px;background:#fff3cd;border-radius:8px;margin-top:8px;font-size:1.1em'>"
        f"<b>&#127912;</b> <b>Te lo dibujo con bolitas:</b><br>"
        f"<b>Tenemos:</b> {total_circles} ({d1} bolitas)<br>"
        f"<b>Quitamos:</b> {crossed_circles} ({d2} bolitas)<br>"
        f"<b>Quedan:</b> {remaining_circles} <b>({remaining} bolitas)</b><br>"
        f"<b>&#128161;</b> Escribe cuantas bolitas quedan."
        f"</div>"
    )

def _is_simple_subtraction(a: int, b: int) -> bool:
    """Detecta si es una resta simple: ambos números de un solo dígito"""
    return a < 10 and b < 10 and a >= b

def _msg_col(a: int, b: int, col, k: int, prev_borrow: int) -> str:
    """Genera el mensaje para una columna específica."""
    d1, d2, borrow, digit, place, needs_borrow = col
    next_place = _next_place_name(k)
    
    # === CASO ESPECIAL: RESTA SIMPLE ===
    if _is_simple_subtraction(a, b) and k == 0:
        return _draw_simple_circles(d1, d2)
    
    # === CASOS NORMALES (restas complejas) ===
    if k == 0:
        intro = f"&#129513; <b>Empezamos por la columna de {place}.</b><br>"
    else:
        intro = f"&#129513; <b>Ahora vamos con la columna de {place}.</b><br>"
    
    # Construir la pregunta considerando el préstamo previo
    actual_d1 = d1 - prev_borrow
    
    if prev_borrow > 0:
        question = f"¿Cuánto es {d1} - {prev_borrow} (que prestamos) - {d2}?"
    else:
        question = f"¿Cuánto es {d1} - {d2}?"
    
    # Recordatorio pedagógico
    if needs_borrow:
        reminder = (
            f"<b>&#128161; Recuerda:</b> Si {actual_d1} es menor que {d2}, "
            f"pide prestado 10 de la columna de <b>{next_place}</b>."
        )
    else:
        reminder = f"<b>&#128161; Recuerda:</b> Escribe el resultado en la columna de <b>{place}</b>."
    
    return (
        f"<div style='padding:8px;background:#fff3cd;border-radius:6px;margin-top:8px'>"
        f"{intro}"
        f"{question}<br>"
        f"{reminder}"
        f"</div>"
    )

# ══════════════════════════════════════════════════════════════
# Motor principal
# ══════════════════════════════════════════════════════════════
def handle_step(question: str, step_now: int, last_answer: str, error_count: int, cycle: str = "c2"):
    parsed = _detect(question)
    if not parsed:
        return None
    a, b = parsed
    
    # ✅ DETECTAR si pidió ayuda
    asking_for_help = _is_asking_for_help(last_answer)

    # Asegurarnos de que a >= b
    if a < b:
        a, b = b, a
    
    cols = _compute_columns(a, b)
    n = len(cols)
    num_solved = min(step_now, n)
    solved_digits = [cols[j][3] for j in range(num_solved)]

    # === CASO ESPECIAL: RESTA SIMPLE (un dígito - un dígito) ===
    if _is_simple_subtraction(a, b) and step_now == 0:
        board = _board(a, b, solved_digits=[], show_line=False)
        msg = _draw_simple_circles(a, b)
        expected = str(a - b)
        
        # ✅ AÑADIR PISTA si hay errores o pide ayuda
        full_msg = f"{board}{msg}"
        if error_count > 0 or asking_for_help:
            hint = _generate_hint("sub_simple", error_count, f"{a} - {b}", "resta")
            full_msg += (
                f"<div style='padding:10px;background:#fff9c4;border-radius:6px;"
                f"margin-top:10px;border-left:3px solid #fbc02d'>"
                f"💡 {hint}"
                f"</div>"
            )
        
        return {
            "status": "ask",
            "message": full_msg,
            "expected_answer": expected,
            "topic": "resta",
            "hint_type": "sub_simple",
            "next_step": step_now + 1
        }
    
    # Si es resta simple y ya respondió correctamente, terminar
    if _is_simple_subtraction(a, b) and step_now > 0:
        result_digits = [int(d) for d in str(a - b)][::-1]
        board = _board(a, b, solved_digits=result_digits, show_line=True)
        final_message = (
            f"<div style='padding:8px;background:#dcfce7;border-radius:6px;margin-top:8px'>"
            f"&#127881; <b>¡Buen trabajo!</b><br>"
            f"Has completado la resta correctamente."
            f"</div>"
        )
        
        msg = f"{board}{final_message}"
        
        # ✅ AÑADIR PISTA si hay errores o pide ayuda
        if error_count > 0 or asking_for_help:
            hint = _generate_hint("sub_resultado", error_count, f"{a} - {b}", "resta")
            msg += (
                f"<div style='padding:10px;background:#fff9c4;border-radius:6px;"
                f"margin-top:10px;border-left:3px solid #fbc02d'>"
                f"💡 {hint}"
                f"</div>"
            )
        
        return {
            "status": "done",
            "message": msg,
            "expected_answer": str(a - b),
            "topic": "resta",
            "hint_type": "sub_resultado",
            "next_step": step_now + 1
        }

    # === CASOS NORMALES: RESTAS COMPLEJAS ===
    if 0 <= step_now < n:
        board = _board(a, b, solved_digits=solved_digits, show_line=False)
        col = cols[step_now]
        prev_borrow = cols[step_now - 1][2] if step_now > 0 else 0
        msg_col_text = _msg_col(a, b, col, step_now, prev_borrow)
        expected = str(col[3])
        
        # Determinar hint_type
        hint_type = "sub_borrow" if col[5] else "sub_col"
        
        full_msg = f"{board}{msg_col_text}"
        
        # ✅ AÑADIR PISTA si hay errores o pide ayuda
        if error_count > 0 or asking_for_help:
            d1, d2 = col[0], col[1]
            hint = _generate_hint(hint_type, error_count, f"{d1} - {d2}", "resta")
            full_msg += (
                f"<div style='padding:10px;background:#fff9c4;border-radius:6px;"
                f"margin-top:10px;border-left:3px solid #fbc02d'>"
                f"💡 {hint}"
                f"</div>"
            )
        
        return {
            "status": "ask",
            "message": full_msg,
            "expected_answer": expected,
            "topic": "resta",
            "hint_type": hint_type,
            "next_step": step_now + 1
        }

    # Cierre final
    if step_now >= n:
        full_digits = [c[3] for c in cols]
        board = _board(a, b, solved_digits=full_digits, show_line=True)
        final_message = (
            f"<div style='padding:8px;background:#dcfce7;border-radius:6px;margin-top:8px'>"
            f"&#127881; <b>¡Buen trabajo!</b><br>"
            f"Has completado la resta correctamente: {a} - {b} = {a - b}."
            f"</div>"
        )
        
        msg = f"{board}{final_message}"
        
        # ✅ AÑADIR PISTA si hay errores o pide ayuda
        if error_count > 0 or asking_for_help:
            hint = _generate_hint("sub_resultado", error_count, f"{a} - {b}", "resta")
            msg += (
                f"<div style='padding:10px;background:#fff9c4;border-radius:6px;"
                f"margin-top:10px;border-left:3px solid #fbc02d'>"
                f"💡 {hint}"
                f"</div>"
            )
        
        return {
            "status": "done",
            "message": msg,
            "expected_answer": str(a - b),
            "topic": "resta",
            "hint_type": "sub_resultado",
            "next_step": step_now + 1
        }