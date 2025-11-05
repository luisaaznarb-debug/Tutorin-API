# -*- coding: utf-8 -*-
"""
multiplication_engine.py
Motor de multiplicación DÍGITO POR DÍGITO - Versión con sistema de pistas
El último dígito de cada línea pide el resultado completo (no crea paso extra para llevada).
"""
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

def _generate_hint(hint_type: str, error_count: int, context: str, topic: str) -> str:
    """Genera una pista usando el sistema de hints"""
    try:
        # Importar la función get_hint del módulo correspondiente
        if topic == "multiplicacion":
            from logic.ai_hints.hints_multiplication import get_hint
        else:
            return "💡 Pista: piensa paso a paso y revisa los números."
        
        e = max(1, min(int(error_count), 9))
        return get_hint(hint_type, e, context, "")
        
    except Exception as e:
        print(f"[{topic.upper()}_ENGINE] ⚠️ Error generando pista: {e}")
        return "💡 Pista: piensa paso a paso y revisa los números cuidadosamente."

# ═══════════════════════════════════════════════════════════════
# FUNCIONES AUXILIARES DE MULTIPLICACIÓN
# ═══════════════════════════════════════════════════════════════

def _parse_mult(q: str):
    """Extrae dos enteros de una expresión como '123 * 45'."""
    q2 = q.replace("×", "*").replace("·", "*").replace("x", "*").replace("X", "*")
    m = re.search(r"^\s*(\d+)\s*\*\s*(\d+)\s*$", q2)
    if not m:
        return None
    a, b = int(m.group(1)), int(m.group(2))
    return a, b

def _compute_partial_full(a: int, digit: int, shift: int) -> int:
    """Calcula una línea parcial completa (con desplazamiento)."""
    return a * digit * (10 ** shift)

def _multiply_digit_by_digit(a: int, digit: int) -> List[Tuple[int, int]]:
    """
    Multiplica 'a' por 'digit' dígito por dígito, devolviendo:
    [(resultado_dígito, llevada_siguiente), ...]
    De derecha a izquierda (unidades primero).
    """
    a_str = str(a)[::-1]
    carry = 0
    results = []
    
    for ch in a_str:
        d = int(ch)
        product = d * digit + carry
        digit_result = product % 10
        carry = product // 10
        results.append((digit_result, carry))
    
    if carry > 0:
        results.append((carry, 0))
    
    return results

def _width(a: int, b: int) -> int:
    """Calcula el ancho necesario para la tabla."""
    total = a * b
    return max(len(str(a)), len(str(b)) + 2, len(str(total)))

def _build_progress_banner(a: int, b: int, current_line: int, total_lines: int, is_sum_step: bool = False, is_done: bool = False) -> str:
    """Banner de progreso adaptado según el número de líneas."""
    banner_style = "background-color: #fff3e0; border: 2px solid #ff9800; border-radius: 8px; padding: 12px; margin-bottom: 15px; text-align: center; font-size: 16px; font-weight: bold;"
    
    if is_done:
        return f"<div style='{banner_style}'>✅ ¡Multiplicación completada! 🎉</div>"
    
    if is_sum_step:
        progress_text = f"📊 <b>Paso final:</b> Sumando las líneas parciales"
    elif total_lines == 1:
        progress_text = f"📝 Multiplicando <b>{a} × {b}</b> dígito por dígito"
    else:
        progress_text = f"📝 <b>Línea {current_line + 1} de {total_lines}:</b> Multiplicando dígito por dígito"
    
    return f"<div style='{banner_style}'>{progress_text}</div>"

def _board_with_highlight(a: int, b: int, partial_lines_data: List[dict], current_line_idx: int, 
                         current_digit_pos: int, show_highlight: bool, show_sum: bool) -> str:
    """Genera tablero visual con protecciones de índice."""
    w = _width(a, b)
    rj = lambda s: s.rjust(w)
    
    lines = []
    
    # Números principales con resaltado
    a_str = str(a)
    b_str = str(b)
    
    if show_highlight and current_line_idx < len(str(b)):
        a_reversed_idx = len(a_str) - 1 - current_digit_pos
        if 0 <= a_reversed_idx < len(a_str) and current_digit_pos < len(a_str):
            a_highlighted = (
                a_str[:a_reversed_idx] + 
                f"<span style='background-color:#fff59d;padding:2px 4px;border-radius:3px;font-weight:bold;'>{a_str[a_reversed_idx]}</span>" + 
                a_str[a_reversed_idx+1:]
            )
        else:
            a_highlighted = a_str
        
        b_reversed_idx = len(b_str) - 1 - current_line_idx
        if 0 <= b_reversed_idx < len(b_str):
            b_highlighted = (
                b_str[:b_reversed_idx] + 
                f"<span style='background-color:#ffcc80;padding:2px 4px;border-radius:3px;font-weight:bold;'>{b_str[b_reversed_idx]}</span>" + 
                b_str[b_reversed_idx+1:]
            )
        else:
            b_highlighted = b_str
        
        lines.append(f"<span style='color:#1976d2;'>{rj(a_highlighted)}</span>")
        lines.append(f"<span style='color:#1976d2;'>{rj('× ' + b_highlighted)}</span>")
    else:
        lines.append(f"<span style='color:#1976d2;font-weight:bold;'>{rj(a_str)}</span>")
        lines.append(f"<span style='color:#1976d2;font-weight:bold;'>{rj('× ' + b_str)}</span>")
    
    lines.append(rj("-" * max(len(a_str), len(b_str) + 2)))
    
    # Líneas parciales
    for i, line_data in enumerate(partial_lines_data):
        text = line_data.get('text', '')
        is_complete = line_data.get('complete', False)
        
        if text:
            if i == current_line_idx and not show_sum and not is_complete:
                lines.append(f"<span style='color:#388e3c;background-color:#e8f5e9;padding:2px;'>{rj(text)} ←</span>")
            else:
                lines.append(f"<span style='color:#388e3c;'>{rj(text)}</span>")
    
    # Línea de suma
    if show_sum:
        valid_texts = [ld['text'] for ld in partial_lines_data if ld.get('text')]
        if valid_texts:
            lines.append(rj("-" * max(len(t) for t in valid_texts)))
            total = a * b
            lines.append(f"<span style='color:#d32f2f;font-weight:bold;'>{rj(str(total))}</span>")
    
    return (
        "<pre style='font-family:\"Courier New\",monospace;line-height:1.6;margin:8px 0;"
        "padding:12px;background-color:#f5f5f5;border-radius:6px;border:1px solid #ddd;"
        "font-size:16px;'>"
        + "\n".join(lines) + 
        "</pre>"
    )

# ═══════════════════════════════════════════════════════════════
# MOTOR PRINCIPAL
# ═══════════════════════════════════════════════════════════════

def handle_step(question: str, step_now: int, last_answer: str, error_count: int, cycle: str = "c2"):
    parsed = _parse_mult(question)
    if not parsed:
        return {
            "status": "error",
            "message": "⚠️ No pude entender la multiplicación. Por favor escribe algo como: <b>23 × 45</b> o <b>12 * 8</b>.",
            "topic": "matematicas",
            "hint_type": "mult_parcial",
            "next_step": step_now
        }
    
    # ✅ DETECTAR si pidió ayuda
    asking_for_help = _is_asking_for_help(last_answer)
    
    a, b = parsed
    b_str = str(b)[::-1]
    n_lines = len(b_str)
    a_str = str(a)
    
    # CORRECCIÓN: Los pasos son solo los dígitos de 'a', NO la llevada final
    # La llevada final se incluye en el último dígito
    total_steps_per_line = [len(a_str)] * n_lines
    
    # Calcular en qué línea y qué dígito estamos
    current_line = 0
    digit_in_line = 0
    steps_accumulated = 0
    
    for line_idx in range(n_lines):
        steps_in_this_line = total_steps_per_line[line_idx]
        if step_now < steps_accumulated + steps_in_this_line:
            current_line = line_idx
            digit_in_line = step_now - steps_accumulated
            break
        steps_accumulated += steps_in_this_line
    else:
        current_line = n_lines
        digit_in_line = 0
    
    total_partial_steps = sum(total_steps_per_line)
    
    # Array para almacenar datos de líneas parciales
    partial_lines_data = []
    
    # Calcular líneas parciales para visualización
    for i in range(n_lines):
        digit = int(b_str[i])
        shift = i
        
        if i < current_line:
            partial = _compute_partial_full(a, digit, shift)
            partial_lines_data.append({
                'text': str(partial),
                'complete': True
            })
        elif i == current_line and step_now < total_partial_steps:
            results = _multiply_digit_by_digit(a, digit)
            built = ""
            for j in range(digit_in_line):
                built = str(results[j][0]) + built
            display_text = built + ("0" * shift)
            partial_lines_data.append({
                'text': display_text,
                'complete': False
            })
        else:
            partial_lines_data.append({
                'text': '',
                'complete': False
            })
    
    # PASO: Multiplicación dígito por dígito
    if step_now < total_partial_steps:
        digit_mult = int(b_str[current_line])
        shift = current_line
        results = _multiply_digit_by_digit(a, digit_mult)
        
        # Acceso seguro
        if digit_in_line >= len(results):
            digit_in_line = len(results) - 1
        
        digit_result, next_carry = results[digit_in_line]
        carry = results[digit_in_line - 1][1] if digit_in_line > 0 else 0
        
        # Determinar si es el último dígito de a
        is_last_digit_of_a = (digit_in_line == len(a_str) - 1)
        
        # Calcular el dígito de 'a' que estamos multiplicando
        a_digit = int(a_str[-(digit_in_line + 1)])
        
        # Calcular producto y respuesta esperada
        product = a_digit * digit_mult + carry
        
        if is_last_digit_of_a:
            # Último dígito: esperamos el resultado completo
            expected_digit = product
        else:
            # Dígitos intermedios: solo la unidad
            expected_digit = product % 10
        
        # Nombres de lugares
        place_names_singular = ["unidades", "decenas", "centenas", "millares", "decenas de millar"]
        place_names_plural = ["unidades", "decenas", "centenas", "millares", "decenas de millar"]
        place_a = place_names_singular[digit_in_line] if digit_in_line < len(place_names_singular) else f"posición {digit_in_line}"
        
        # Banner de progreso
        progress_banner = _build_progress_banner(a, b, current_line, n_lines, False, False)
        
        # Tablero visual
        board = _board_with_highlight(a, b, partial_lines_data, current_line, digit_in_line, True, False)
        
        # Explicación del shift (solo al inicio de líneas 2+)
        shift_explanation = ""
        if digit_in_line == 0 and shift > 0:
            place_name = place_names_plural[shift] if shift < len(place_names_plural) else f"posición {shift}"
            zero_text = "un cero" if shift == 1 else f"{shift} ceros"
            shift_explanation = (
                f"<div style='background-color:#fff9c4;padding:10px;border-left:4px solid #fbc02d;margin-bottom:10px;'>"
                f"📍 <b>¡Atención!</b> Como multiplicamos por el dígito de las <b>{place_name}</b>, "
                f"he añadido automáticamente <b>{zero_text}</b> al final de esta línea.<br/>"
                f"Ahora empezamos a multiplicar dígito por dígito."
                f"</div>"
            )
        
        # Determinar el número del paso
        step_number = sum(total_steps_per_line[:current_line]) + digit_in_line + 1
        
        # MENSAJES SEGÚN POSICIÓN
        if is_last_digit_of_a:
            # Último dígito de la línea
            intro = f"<b>Paso {step_number}:</b> Último dígito de esta línea."
            
            if product >= 10:
                # Resultado de dos cifras
                if carry > 0:
                    question_text = (
                        f"{intro}<br/>"
                        f"Multiplica <b>{a_digit} × {digit_mult}</b> y suma la llevada ({carry}).<br/>"
                        f"✏️ Como es el final, escribe <b>el resultado completo</b> (ambas cifras)."
                    )
                else:
                    question_text = (
                        f"{intro}<br/>"
                        f"Multiplica <b>{a_digit} × {digit_mult}</b>.<br/>"
                        f"✏️ Como es el final, escribe <b>el resultado completo</b> (ambas cifras)."
                    )
            else:
                # Resultado de una cifra
                if carry > 0:
                    question_text = (
                        f"{intro}<br/>"
                        f"Multiplica <b>{a_digit} × {digit_mult}</b> y suma la llevada ({carry}).<br/>"
                        f"✏️ Escribe el resultado."
                    )
                else:
                    question_text = (
                        f"{intro}<br/>"
                        f"Multiplica <b>{a_digit} × {digit_mult}</b>.<br/>"
                        f"✏️ Escribe el resultado."
                    )
        elif digit_in_line == 0 and shift == 0:
            # Primer paso absoluto
            intro = f"<b>Paso 1:</b> Empezamos por las <b>{place_a}</b>."
            question_text = (
                f"{intro}<br/>"
                f"Multiplica <b>{a_digit} × {digit_mult}</b>. ¿Cuánto es?<br/>"
                f"✏️ Anota <b>solo la cifra de las {place_a}</b> y recuerda lo que te llevas."
            )
        elif digit_in_line == 0:
            # Primer dígito de una línea (no la primera)
            intro = f"<b>Paso {step_number}:</b> Ahora multiplicamos por las <b>{place_a}</b>."
            question_text = (
                f"{intro}<br/>"
                f"Multiplica <b>{a_digit} × {digit_mult}</b>. ¿Cuánto es?<br/>"
                f"✏️ Anota <b>solo la cifra de las {place_a}</b> y recuerda lo que te llevas."
            )
        else:
            # Dígitos intermedios
            intro = f"<b>Paso {step_number}:</b> Continuamos con las <b>{place_a}</b>."
            if carry == 0:
                question_text = (
                    f"{intro}<br/>"
                    f"Multiplica <b>{a_digit} × {digit_mult}</b>. ¿Cuánto es?<br/>"
                    f"✏️ Anota <b>solo la cifra de las {place_a}</b> y recuerda lo que te llevas."
                )
            else:
                question_text = (
                    f"{intro}<br/>"
                    f"Multiplica <b>{a_digit} × {digit_mult}</b> (no olvides la llevada anterior).<br/>"
                    f"✏️ Anota <b>solo la cifra de las {place_a}</b> y recuerda lo que te llevas."
                )
        
        msg = (
            f"{progress_banner}"
            f"{board}"
            f"{shift_explanation}"
            f"<div style='margin-top:10px;'>"
            f"{question_text}"
            f"</div>"
        )
        
        # ✅ AÑADIR PISTA si hay errores o pide ayuda
        if error_count > 0 or asking_for_help:
            hint = _generate_hint("mult_parcial", error_count, f"{a_digit} × {digit_mult}", "multiplicacion")
            msg += (
                f"<div style='padding:10px;background:#fff9c4;border-radius:6px;"
                f"margin-top:10px;border-left:3px solid #fbc02d'>"
                f"💡 {hint}"
                f"</div>"
            )
        
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": str(expected_digit),
            "topic": "matematicas",
            "hint_type": "mult_parcial",
            "next_step": step_now + 1
        }
    
    # PASO: Suma final (solo si hay más de una línea)
    elif step_now == total_partial_steps:
        if n_lines == 1:
            # CASO ESPECIAL: Multiplicación por una cifra - No hay suma
            progress_banner = _build_progress_banner(a, b, n_lines, n_lines, False, True)
            
            partial_lines_complete = []
            digit = int(b_str[0])
            partial = _compute_partial_full(a, digit, 0)
            partial_lines_complete.append({
                'text': str(partial),
                'complete': True
            })
            
            board = _board_with_highlight(a, b, partial_lines_complete, -1, -1, False, False)
            
            msg = (
                f"{progress_banner}"
                f"{board}"
                f"<div style='margin-top:10px;'>"
                f"✅ ¡Excelente! Como solo multiplicaste por <b>{b}</b>, "
                f"el resultado final es <b>{partial}</b>. 🎉"
                f"</div>"
            )
            
            # ✅ AÑADIR PISTA si hay errores o pide ayuda
            if error_count > 0 or asking_for_help:
                hint = _generate_hint("mult_resultado", error_count, f"{a} × {b}", "multiplicacion")
                msg += (
                    f"<div style='padding:10px;background:#fff9c4;border-radius:6px;"
                    f"margin-top:10px;border-left:3px solid #fbc02d'>"
                    f"💡 {hint}"
                    f"</div>"
                )
            
            return {
                "status": "done",
                "message": msg,
                "expected_answer": "ok",
                "topic": "matematicas",
                "hint_type": "mult_resultado",
                "next_step": step_now + 1
            }
        else:
            # Varias líneas: pedir suma
            progress_banner = _build_progress_banner(a, b, n_lines, n_lines, True, False)
            
            partial_lines_complete = []
            for i in range(n_lines):
                digit = int(b_str[i])
                shift = i
                partial = _compute_partial_full(a, digit, shift)
                partial_lines_complete.append({
                    'text': str(partial),
                    'complete': True
                })
            
            board = _board_with_highlight(a, b, partial_lines_complete, -1, -1, False, False)
            total = a * b
            
            msg = (
                f"{progress_banner}"
                f"{board}"
                f"<div style='margin-top:10px;'>"
                f"👉 ¡Perfecto! Ahora <b>suma todas las líneas parciales</b> en vertical.<br/>"
                f"✏️ Escribe el <b>resultado final</b>."
                f"</div>"
            )
            
            # ✅ AÑADIR PISTA si hay errores o pide ayuda
            if error_count > 0 or asking_for_help:
                hint = _generate_hint("mult_suma", error_count, f"{a} × {b}", "multiplicacion")
                msg += (
                    f"<div style='padding:10px;background:#fff9c4;border-radius:6px;"
                    f"margin-top:10px;border-left:3px solid #fbc02d'>"
                    f"💡 {hint}"
                    f"</div>"
                )
            
            return {
                "status": "ask",
                "message": msg,
                "expected_answer": str(total),
                "topic": "matematicas",
                "hint_type": "mult_suma",
                "next_step": step_now + 1
            }
    
    # PASO: Completado
    else:
        progress_banner = _build_progress_banner(a, b, n_lines, n_lines, False, True)
        
        partial_lines_complete = []
        for i in range(n_lines):
            digit = int(b_str[i])
            shift = i
            partial = _compute_partial_full(a, digit, shift)
            partial_lines_complete.append({
                'text': str(partial),
                'complete': True
            })
        
        board = _board_with_highlight(a, b, partial_lines_complete, -1, -1, False, True)
        
        msg = (
            f"{progress_banner}"
            f"{board}"
            f"<div style='margin-top:10px;'>"
            f"✅ ¡Excelente trabajo! 🎉🎊<br/>"
            f"Has completado la multiplicación paso a paso correctamente."
            f"</div>"
        )
        
        # ✅ AÑADIR PISTA si hay errores o pide ayuda
        if error_count > 0 or asking_for_help:
            hint = _generate_hint("mult_resultado", error_count, f"{a} × {b}", "multiplicacion")
            msg += (
                f"<div style='padding:10px;background:#fff9c4;border-radius:6px;"
                f"margin-top:10px;border-left:3px solid #fbc02d'>"
                f"💡 {hint}"
                f"</div>"
            )
        
        return {
            "status": "done",
            "message": msg,
            "expected_answer": "ok",
            "topic": "matematicas",
            "hint_type": "mult_resultado",
            "next_step": step_now + 1
        }