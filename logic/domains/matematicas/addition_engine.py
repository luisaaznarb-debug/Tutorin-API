# -*- coding: utf-8 -*-
import re
from typing import List, Tuple

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

def _generate_hint(hint_type: str, error_count: int, context: str) -> str:
    """Genera una pista usando el sistema de hints"""
    try:
        from logic.ai_hints.hints_addition import get_hint
        e = max(1, min(int(error_count), 9))
        return get_hint(hint_type, e, context, "")
    except Exception as e:
        print(f"[SUMA_ENGINE] ⚠️ Error generando pista: {e}")
        return "💡 Pista: suma columna por columna, empezando por la derecha."

# ═══════════════════════════════════════════════════════════════
# FUNCIONES AUXILIARES
# ═══════════════════════════════════════════════════════════════

_PLACES = [
    "unidades", "decenas", "centenas", "millares", "decenas de millar",
    "centenas de millar", "millones", "decenas de millón", "centenas de millón"
]

# Mapeo de nombres de columnas siguientes
_NEXT_PLACES = {
    "unidades": "decenas",
    "decenas": "centenas",
    "centenas": "millares",
    "millares": "decenas de millar",
    "decenas de millar": "centenas de millar",
    "centenas de millar": "millones",
    "millones": "decenas de millón",
    "decenas de millón": "centenas de millón"
}

def _place_name(k: int) -> str:
    return _PLACES[k] if k < len(_PLACES) else f"posición {k}"

def _next_place_name(k: int) -> str:
    current = _place_name(k)
    return _NEXT_PLACES.get(current, "siguiente columna")

def _norm_cycle(cycle: str | None) -> str:
    c = (cycle or "c2").strip().lower()
    if c in {"1", "c1"}: return "c1"
    if c in {"2", "c2"}: return "c2"
    if c in {"3", "c3"}: return "c3"
    return "c2"

def _parse_add(question: str) -> Tuple[int, int] | None:
    q = question.replace("＋", "+").replace("﹢", "+").replace("—", "-")
    m = re.search(r"(\d+)\s*\+\s*(\d+)", q)
    if not m:
        return None
    a, b = int(m.group(1)), int(m.group(2))
    return a, b

def _digits_rev(n: int) -> List[int]:
    return [int(ch) for ch in str(n)][::-1]

def _compute_columns(a: int, b: int):
    A = _digits_rev(a)
    B = _digits_rev(b)
    n = max(len(A), len(B))
    cols = []
    carry = 0
    for k in range(n):
        d1 = A[k] if k < len(A) else 0
        d2 = B[k] if k < len(B) else 0
        total = d1 + d2 + carry
        digit = total % 10
        new_carry = total // 10
        cols.append((d1, d2, carry, total, digit, new_carry, _place_name(k)))
        carry = new_carry
    return cols, carry

def _width(a: int, b: int) -> int:
    total = a + b
    return max(len(str(a)), len(str(b)) + 2, len(str(total))) + 2

def _board(a: int, b: int, solved_right_digits: List[int], show_sum_line: bool) -> str:
    w = _width(a, b)
    rj = lambda s: s.rjust(w)
    lines = [rj(str(a)), rj("+ " + str(b)), rj("-" * max(len(str(a)), len(str(b)) + 2))]
    partial = "".join(str(d) for d in solved_right_digits[::-1])
    lines.append(rj(partial))
    if show_sum_line:
        lines.append(rj("-" * max(len(partial), 1)))
    return (
        "<pre style='font-family:monospace;line-height:1.25;margin:6px 0 0 0'>"
        + "\n".join(lines)
        + "</pre>"
    )

def _draw_simple_circles(d1: int, d2: int) -> str:
    """Dibuja bolitas para sumas simples (un dígito + un dígito)"""
    circles = []
    
    if d1 > 0:
        circles.append("&#128309;" * d1 + f" ({d1})")
    if d2 > 0:
        circles.append("&#128994;" * d2 + f" ({d2})")
    
    circles_display = "<br>".join(circles)
    
    total = d1 + d2
    all_circles = "&#9899;" * total
    
    return (
        f"<div style='font-family:sans-serif;line-height:1.8;padding:10px;background:#f9fafb;border-radius:8px;margin-top:8px;font-size:1.1em'>"
        f"<b>&#127912;</b> <b>Te lo dibujo con bolitas de colores:</b><br>"
        f"{circles_display}<br>"
        f"<b>Total:</b> {all_circles}<br>"
        f"<b>&#128161;</b> Cuenta las bolitas y escribe el numero."
        f"</div>"
    )

def _is_simple_sum(a: int, b: int) -> bool:
    """Detecta si es una suma simple: ambos números de un solo dígito"""
    return a < 10 and b < 10

def _msg_col(a: int, b: int, col, cycle: str, k: int) -> str:
    """Genera el mensaje para una columna específica siguiendo el formato de las pistas."""
    d1, d2, carry_in, total, digit, carry_out, place = col
    next_place = _next_place_name(k)
    
    # === CASO ESPECIAL: SUMA SIMPLE (un dígito + un dígito) ===
    # SIEMPRE mostramos bolitas para sumas de un dígito + un dígito
    if _is_simple_sum(a, b) and k == 0 and carry_in == 0:
        return _draw_simple_circles(d1, d2)
    
    # === CASOS NORMALES (sumas complejas) ===
    # Mensaje inicial según si es la primera columna o no
    if k == 0:
        intro = f"&#129513; <b>Empezamos por la columna de {place}.</b><br>"
    else:
        intro = f"&#129513; <b>Ahora vamos con la columna de {place}.</b><br>"
    
    # Construir la pregunta
    if carry_in > 0:
        question = f"¿Cuánto es {d1} + {d2} + lo que llevas? (¿Te acuerdas?)"
    else:
        question = f"¿Cuánto es {d1} + {d2}?"
    
    # Recordatorio pedagógico
    if carry_out > 0 or total >= 10:
        reminder = (
            f"<b>&#128161; Recuerda:</b> Si la suma es mayor de 10, solo escribes las <b>{place}</b>, "
            f"el resto lo llevas a la columna de <b>{next_place}</b>."
        )
    else:
        reminder = f"<b>&#128161; Recuerda:</b> Escribe el resultado en la columna de <b>{place}</b>."
    
    return (
        f"<div style='padding:8px;background:#f0f9ff;border-radius:6px;margin-top:8px'>"
        f"{intro}"
        f"{question}<br>"
        f"{reminder}"
        f"</div>"
    )

def _msg_carry(final_carry: int) -> str:
    """Mensaje pedagógico para la llevada final."""
    return (
        f"<div style='padding:8px;background:#f0f9ff;border-radius:6px;margin-top:8px'>"
        f"&#129513; <b>¡Casi terminamos!</b><br>"
        f"Hay una <b>llevada final</b> de la última columna.<br>"
        f"<b>&#128161;</b> ¿Qué número escribes a la izquierda del resultado?"
        f"</div>"
    )

# ════════════════════════════════════════════════════════════
# Motor principal (CON PISTAS INTEGRADAS)
# ════════════════════════════════════════════════════════════
def handle_step(question: str, step_now: int, last_answer: str, error_count: int, cycle: str = "c2"):
    parsed = _parse_add(question)
    if not parsed:
        return None
    a, b = parsed
    cycle = _norm_cycle(cycle)
    
    # ✅ DETECTAR si pidió ayuda
    asking_for_help = _is_asking_for_help(last_answer)
    
    cols, final_carry = _compute_columns(a, b)
    n = len(cols)
    num_solved = min(step_now, n)
    solved_digits = [cols[j][4] for j in range(num_solved)]

    # === CASO ESPECIAL: SUMA SIMPLE (un dígito + un dígito) ===
    # Para sumas simples, el ejercicio termina en un solo paso
    if _is_simple_sum(a, b) and step_now == 0:
        board = _board(a, b, solved_right_digits=[], show_sum_line=False)
        msg = _draw_simple_circles(a, b)
        expected = str(a + b)
        
        # ✅ AÑADIR PISTA
        if error_count > 0 or asking_for_help:
            hint = _generate_hint("add_simple", error_count, f"{a} + {b}")
            msg += (
                f"<div style='padding:10px;background:#fff9c4;border-radius:6px;"
                f"margin-top:10px;border-left:3px solid #fbc02d'>"
                f"💡 {hint}"
                f"</div>"
            )
        
        return {
            "status": "ask",
            "message": f"{board}{msg}",
            "expected_answer": expected,
            "topic": "suma",
            "hint_type": "add_simple",
            "next_step": step_now + 1
        }
    
    # Si es suma simple y ya respondió correctamente, terminar
    if _is_simple_sum(a, b) and step_now > 0:
        result_digits = [int(d) for d in str(a + b)][::-1]
        board = _board(a, b, solved_right_digits=result_digits, show_sum_line=True)
        final_message = (
            f"<div style='padding:8px;background:#dcfce7;border-radius:6px;margin-top:8px'>"
            f"&#127881; <b>¡Buen trabajo!</b><br>"
            f"Has completado la suma correctamente."
            f"</div>"
        )
        return {
            "status": "done",
            "message": f"{board}{final_message}",
            "expected_answer": str(a + b),
            "topic": "suma",
            "hint_type": "add_resultado",
            "next_step": step_now + 1
        }

    # === CASOS NORMALES: SUMAS COMPLEJAS ===
    # Paso de columnas (0 hasta n-1)
    if 0 <= step_now < n:
        board = _board(a, b, solved_right_digits=solved_digits, show_sum_line=False)
        col = cols[step_now]
        msg = _msg_col(a, b, col, cycle, step_now)
        expected = str(col[4])
        
        # ✅ AÑADIR PISTA
        if error_count > 0 or asking_for_help:
            hint = _generate_hint("add_col", error_count, f"{a} + {b}")
            msg += (
                f"<div style='padding:10px;background:#fff9c4;border-radius:6px;"
                f"margin-top:10px;border-left:3px solid #fbc02d'>"
                f"💡 {hint}"
                f"</div>"
            )
        
        return {
            "status": "ask",
            "message": f"{board}{msg}",
            "expected_answer": expected,
            "topic": "suma",
            "hint_type": "add_col",
            "next_step": step_now + 1
        }

    # Paso de llevada final (step_now == n)
    if step_now == n and final_carry > 0:
        board = _board(a, b, solved_right_digits=solved_digits, show_sum_line=False)
        msg = _msg_carry(final_carry)
        
        # ✅ AÑADIR PISTA
        if error_count > 0 or asking_for_help:
            hint = _generate_hint("add_carry", error_count, f"{a} + {b}")
            msg += (
                f"<div style='padding:10px;background:#fff9c4;border-radius:6px;"
                f"margin-top:10px;border-left:3px solid #fbc02d'>"
                f"💡 {hint}"
                f"</div>"
            )
        
        return {
            "status": "ask",
            "message": f"{board}{msg}",
            "expected_answer": str(final_carry),
            "topic": "suma",
            "hint_type": "add_carry",
            "next_step": step_now + 1
        }

    # Cierre final
    result_digits = [col[4] for col in cols]
    if final_carry > 0:
        result_digits.append(final_carry)
    board = _board(a, b, solved_right_digits=result_digits, show_sum_line=True)
    
    final_message = (
        f"<div style='padding:8px;background:#dcfce7;border-radius:6px;margin-top:8px'>"
        f"&#127881; <b>¡Buen trabajo!</b><br>"
        f"Has completado la suma correctamente."
        f"</div>"
    )
    
    return {
        "status": "done",
        "message": f"{board}{final_message}",
        "expected_answer": str(a + b),
        "topic": "suma",
        "hint_type": "add_resultado",
        "next_step": step_now + 1
    }
