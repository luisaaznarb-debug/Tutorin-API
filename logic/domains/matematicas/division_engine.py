# -*- coding: utf-8 -*-
"""
division_engine.py
Motor de división paso a paso para Tutorín
✅ VERSIÓN CORREGIDA: Las pistas se manejan en solve.py, no aquí
"""
import re
from typing import List, Dict, Tuple

# ═══════════════════════════════════════════════════════════════
# SISTEMA DE DETECCIÓN DE AYUDA (mantener para compatibilidad)
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

# ─────────────────────────────────────────────────────────────
# Parseo y helpers
# ─────────────────────────────────────────────────────────────
def _parse_div(q: str):
    """Acepta '3457 / 3', '3457:3' o '3457 ÷ 3'."""
    q2 = q.replace("÷", "/").replace(":", "/")
    m = re.search(r"(\d+)\s*/\s*(\d+)", q2)
    if not m:
        return None
    a, b = int(m.group(1)), int(m.group(2))
    if b == 0:
        return None
    return a, b

def _first_group_len(dividend: int, divisor: int) -> int:
    """Longitud mínima del prefijo del dividendo que es >= divisor (o todo el número)."""
    s = str(dividend)
    k = 1
    while k < len(s) and int(s[:k]) < divisor:
        k += 1
    return k

def _compute_steps(dividend: int, divisor: int) -> Tuple[List[Dict], int, int, int]:
    """
    Devuelve:
        - steps: [{ group, qdigit, product, remainder, [next_digit], [new_group], quotient_prefix }]
        - quotient_full, remainder_final
        - first_k: nº de dígitos del primer grupo
    """
    s = str(dividend)
    n = len(s)
    first_k = _first_group_len(dividend, divisor)
    group = int(s[:first_k])
    steps: List[Dict] = []
    quotient_str = ""
    pos = first_k
    while True:
        qdigit = group // divisor
        product = qdigit * divisor
        remainder = group - product
        quotient_str += str(qdigit)
        item = {
            "group": group,
            "qdigit": qdigit,
            "product": product,
            "remainder": remainder,
            "quotient_prefix": quotient_str
        }
        if pos < n:
            next_digit = int(s[pos])
            new_group = remainder * 10 + next_digit
            item["next_digit"] = next_digit
            item["new_group"] = new_group
            steps.append(item)
            group = new_group
            pos += 1
        else:
            steps.append(item)
            break
    quotient_full = int(quotient_str)
    remainder_final = steps[-1]["remainder"]
    return steps, quotient_full, remainder_final, first_k

# ─────────────────────────────────────────────────────────────
# Render: DIVIDENDO a la IZQUIERDA (4578 | 2) y COCIENTE DEBAJO del divisor
# ─────────────────────────────────────────────────────────────
def _render_pre_left_dividend(dividend: int,
                              divisor: int,
                              steps: List[Dict],
                              first_k: int,
                              block: int,
                              sub: int,
                              show_full_quotient: bool = False) -> str:
    """
    Dos columnas monoespaciadas:
      - Izquierda: operaciones bajo el DIVIDENDO.
      - Derecha: DIVISOR y, DEBAJO, el COCIENTE parcial/total (solo cifras confirmadas).
    Estructura:
      1) Cabecera: "<dividendo> | <divisor>"
      2) Cociente: " " * len(dividendo) + "   " + <cociente-confirmado>
      3) Operaciones bajo el dividendo: producto, guiones, resto (con ceros a la izda) y flecha de bajada.
         * IMPORTANTE: el producto NO se pinta en el subpaso de cifra del cociente (sub==0) para no revelar.
    """
    s_div = str(dividend)
    s_divisor = str(divisor)
    L = len(s_div)                # ancho de la columna izquierda (dividendo)
    Rmin = len(s_divisor)         # ancho mínimo derecha (divisor)
    SEP_BAR = " | "               # separador en cabecera
    SEP = "   "                   # separador en el resto de filas
    # Cifras de cociente confirmadas:
    # todas las de bloques previos + (la del bloque actual si ya estamos en la RESTA o posterior).
    confirmed = block + (1 if sub >= 1 else 0)
    q_parcial = steps[block]["quotient_prefix"][:confirmed] if block < len(steps) else steps[-1]["quotient_prefix"]
    q_shown = (steps[-1]["quotient_prefix"] if show_full_quotient else q_parcial) or ""
    R = max(Rmin, len(q_shown))
    rows: List[str] = []
    # 1) Cabecera: dividendo | divisor
    rows.append(f"{s_div}{SEP_BAR}{s_divisor.rjust(R)}")
    # 2) Fila de cociente (debajo del divisor, en la columna derecha)
    rows.append(" " * L + SEP + q_shown.rjust(R))
    # Helper: operaciones bajo el dividendo
    def add_left(text: str):
        rows.append(text.ljust(L) + SEP + " " * R)
    # 3) Bloques terminados (pintamos todo)
    for j in range(0, block):
        end_idx = first_k - 1 + j
        prod = str(steps[j]["product"])
        rem_raw = str(steps[j]["remainder"])
        rem = rem_raw.rjust(len(s_divisor), "0")  # p. ej., '09' para comparar con el divisor
        off_prod = end_idx - (len(prod) - 1)
        off_rem = end_idx - (len(rem) - 1)
        add_left(" " * off_prod + prod)
        add_left(" " * off_prod + "-" * len(prod))
        # Si hay next_digit, mostrar solo el new_group (no el resto)
        # Si no hay next_digit, mostrar el resto
        if "next_digit" in steps[j]:
            new_grp = str(steps[j]["new_group"])
            off_new = end_idx + 1 - (len(new_grp) - 1)
            add_left(" " * off_new + new_grp)
        else:
            add_left(" " * off_rem + rem)
    # 4) Bloque actual (NO mostrar producto si aún estamos eligiendo la cifra del cociente)
    if block < len(steps):
        end_idx = first_k - 1 + block
        prod = str(steps[block]["product"])
        rem_raw = str(steps[block]["remainder"])
        rem = rem_raw.rjust(len(s_divisor), "0")
        if sub >= 1:
            off_prod = end_idx - (len(prod) - 1)
            add_left(" " * off_prod + prod)
            add_left(" " * off_prod + "-" * len(prod))
        if sub >= 2:
            # Mostrar el resto solo después de responder la resta
            off_rem = end_idx - (len(rem) - 1)
            add_left(" " * off_rem + rem)
            # Mostrar la flecha solo en el paso de bajar
            if "next_digit" in steps[block]:
                arrow_col = end_idx + 1
                add_left(" " * arrow_col + "↓" + str(steps[block]["next_digit"]))
    return "<pre style='font-family:monospace;line-height:1.25;margin:6px 0 0 0'>" + "\n".join(rows) + "</pre>"

# ─────────────────────────────────────────────────────────────
# Motor por pasos
# ─────────────────────────────────────────────────────────────
def handle_div_step(question: str, step_now: int, last_answer: str, error_count: int):
    """
    Motor principal de división paso a paso.
    ✅ CORREGIDO: Ya NO agrega pistas automáticamente (las maneja solve.py)
    """
    parsed = _parse_div(question)
    if not parsed:
        return None
    
    dividend, divisor = parsed
    
    # ✅ MANTENER detección de ayuda (para compatibilidad)
    asking_for_help = _is_asking_for_help(last_answer)
    
    steps, q_full, r_final, first_k = _compute_steps(dividend, divisor)
    # subpasos por bloque: 3 (cifra, resta, bajar) excepto el último que es 2 (no hay bajar)
    subcounts = [3] * (len(steps) - 1) + [2]
    
    # Paso 0: elegir primer grupo
    if step_now == 0:
        pre = _render_pre_left_dividend(dividend, divisor, steps, first_k, block=0, sub=0, show_full_quotient=False)
        msg = (
            f"{pre}"
            "👉 Elige el <b>primer grupo del dividendo</b> (lee los números desde la izquierda) "
            "que sea <b>mayor o igual</b> que el <b>divisor</b> (número de la derecha). "
            f"En este caso: dividendo = <b>{dividend}</b>, divisor = <b>{divisor}</b>. "
            "¿Con qué <b>número empezamos</b>? Escribe solo ese número."
        )
        
        # 🔥 ELIMINADO: Ya no agregamos pistas aquí
        
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": str(int(str(dividend)[:first_k])),
            "topic": "division",
            "hint_type": "div_grupo",
            "next_step": step_now + 1
        }
    
    # Mapear step_now → (block, sub)
    s = step_now - 1
    block = 0
    while block < len(subcounts) and s >= subcounts[block]:
        s -= subcounts[block]
        block += 1
    
    # Fin (tras el último resto): tablero final con cociente completo DEBAJO del divisor
    if block >= len(steps):
        pre = _render_pre_left_dividend(dividend, divisor, steps, first_k, block=len(steps)-1, sub=2, show_full_quotient=True)
        msg = f"{pre}✅ ¡Buen trabajo! Has completado todos los pasos de la división."
        
        # 🔥 ELIMINADO: Ya no agregamos pistas aquí
        
        return {
            "status": "done",
            "message": msg,
            "expected_answer": "ok",
            "topic": "division",
            "hint_type": "div_resultado",
            "next_step": step_now + 1
        }
    
    sub = s  # 0: cifra del cociente, 1: resta, 2: bajar
    show_full = (block == len(steps) - 1 and sub >= 1)
    pre = _render_pre_left_dividend(dividend, divisor, steps, first_k, block, sub, show_full_quotient=show_full)
    
    if sub == 0:  # elegir cifra del cociente
        msg = (
            f"{pre}"
            f"👉 ¿Cuántas veces cabe <b>{divisor}</b> en <b>{steps[block]['group']}</b> sin pasarte? "
            "Escribe solo la <b>cifra del cociente</b>."
        )
        
        # 🔥 ELIMINADO: Ya no agregamos pistas aquí
        
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": str(steps[block]["qdigit"]),
            "topic": "division",
            "hint_type": "div_qdigit",
            "next_step": step_now + 1
        }
    
    if sub == 1:  # resta
        msg = (
            f"{pre}"
            f"Ahora resta: <b>{steps[block]['group']}</b> − <b>{divisor}×{steps[block]['qdigit']}</b>. "
            "👉 Escribe solo el <b>resto</b>."
        )
        
        # 🔥 ELIMINADO: Ya no agregamos pistas aquí
        
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": str(steps[block]["remainder"]),
            "topic": "division",
            "hint_type": "div_resta",
            "next_step": step_now + 1
        }
    
    if sub == 2 and "next_digit" in steps[block]:  # bajar cifra
        msg = (
            f"{pre}"
            f"Baja la siguiente cifra: <b>{steps[block]['next_digit']}</b>. "
            "👉 ¿Cuál es el <b>nuevo número</b> que queda?"
        )
        
        # 🔥 ELIMINADO: Ya no agregamos pistas aquí
        
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": str(steps[block]["new_group"]),
            "topic": "division",
            "hint_type": "div_bajar",
            "next_step": step_now + 1
        }
    
    # Fallback
    msg = f"{pre}Sigamos con la división."
    
    # 🔥 ELIMINADO: Ya no agregamos pistas aquí
    
    return {
        "status": "ask",
        "message": msg,
        "topic": "division",
        "hint_type": "div_resultado",
        "next_step": step_now + 1
    }

# ✅ ALIAS PARA COMPATIBILIDAD
def handle_step(question: str, step_now: int, last_answer: str, error_count: int, cycle: str = "c2"):
    """Alias para compatibilidad con otros motores"""
    return handle_div_step(question, step_now, last_answer, error_count)