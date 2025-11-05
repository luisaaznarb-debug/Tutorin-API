# -*- coding: utf-8 -*-
"""
fractions_engine.py
Motor de fracciones con progreso horizontal y fracciones visuales
✅ VERSIÓN DEFINITIVA: Con sistema de pistas integrado y contexto correcto
"""

from fractions import Fraction
import re
from math import lcm

# ═══════════════════════════════════════════════════════════════
# SISTEMA DE PISTAS (CORREGIDO)
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

def _generate_hint(hint_type: str, error_count: int, context_with_marker: str) -> str:
    """
    Genera una pista usando el sistema ai_router.
    
    IMPORTANTE: context_with_marker debe incluir el marcador [FRAC:2/3+4/5]
    que necesita hints_fractions.py para extraer los números.
    """
    try:
        from logic.ai_hints.ai_router import generate_hint_with_ai
        hint = generate_hint_with_ai(
            topic="fracciones",
            step=hint_type,
            question_or_context=context_with_marker,  # ← Debe incluir [FRAC:...]
            answer="",
            error_count=error_count,
            cycle="c2"
        )
        return hint
    except Exception as e:
        print(f"[FRACTIONS_ENGINE] ⚠️ Error generando pista: {e}")
        import traceback
        traceback.print_exc()
        return "💡 Pista: piensa paso a paso y revisa los números cuidadosamente."


# ──────────────────────────────────────────────
# Utilidades (sin cambios)
# ──────────────────────────────────────────────

def _parse_frac_with_op(expr: str):
    expr = expr.replace(":", "/").replace("÷", "/").replace(",", ".").strip()
    m = re.search(r"(\d+)\s*/\s*(\d+)\s*([+\-])\s*(\d+)\s*/\s*(\d+)", expr)
    if not m:
        return None
    a, b, op, c, d = int(m.group(1)), int(m.group(2)), m.group(3), int(m.group(4)), int(m.group(5))
    return Fraction(a, b), Fraction(c, d), op

def _pretty_frac(numerator: int, denominator: int, color: str = "#1e3a8a") -> str:
    return f"<span class='fraction' style='color: {color};'><span class='fraction-numerator'>{numerator}</span><span class='fraction-denominator'>{denominator}</span></span>"

def _build_progress_banner(f1: Fraction, f2: Fraction, op: str, step_now: int) -> str:
    op_symbol = " + " if op == "+" else " - "
    common_den = lcm(f1.denominator, f2.denominator)
    factor1, factor2 = common_den // f1.denominator, common_den // f2.denominator
    new_num1, new_num2 = f1.numerator * factor1, f2.numerator * factor2
    text_color = "#1e3a8a"
    banner_style = "background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%); border: 3px solid #5B9BD5; border-radius: 12px; padding: 14px; margin-bottom: 15px; display: flex; align-items: center; justify-content: flex-start; gap: 10px; flex-wrap: wrap;"
    banner_class = "fraction-progress-banner"
    arrow = f"<span style='color: {text_color}; font-weight: bold; font-size: 20px; margin: 0 8px;'>→</span>"
    current_style = f"background-color: #FFE082; padding: 6px 12px; border-radius: 8px; font-weight: bold; display: inline-flex; align-items: center; border: 2px solid #FFB84D; color: {text_color};"
    done_style = f"color: {text_color}; display: inline-flex; align-items: center; font-size: 18px; font-weight: 500;"
    
    frac1 = _pretty_frac(f1.numerator, f1.denominator, text_color)
    frac2 = _pretty_frac(f2.numerator, f2.denominator, text_color)
    frac_equiv1 = _pretty_frac(new_num1, common_den, text_color)
    frac_equiv2 = _pretty_frac(new_num2, common_den, text_color)
    
    if step_now <= 1:
        return f"<div class='{banner_class}' style='{banner_style}'><div style='display: inline-flex; align-items: center; gap: 8px; color: {text_color};'><span style='font-size: 18px;'>📝</span>{frac1}<span style='margin: 0 5px; font-size: 20px; color: {text_color};'>{op_symbol}</span>{frac2}</div></div>"
    elif step_now == 2:
        return f"<div class='{banner_class}' style='{banner_style}'><div style='{done_style}'><span style='font-size: 16px; margin-right: 5px;'>📝</span>{frac1}<span style='margin: 0 5px;'>{op_symbol}</span>{frac2}</div>{arrow}<div style='{done_style}'><span>m.c.m. = <strong style='color: {text_color}; font-size: 20px;'>{common_den}</strong></span></div>{arrow}<div style='{current_style}'><span>⏳ Convirtiendo...</span></div></div>"
    elif step_now == 3:
        return f"<div class='{banner_class}' style='{banner_style}'><div style='{done_style}'><span style='font-size: 15px; margin-right: 5px;'>📝</span>{frac1}<span style='margin: 0 4px;'>{op_symbol}</span>{frac2}</div>{arrow}<div style='display: inline-flex; align-items: center; gap: 5px; color: {text_color};'>{frac_equiv1}<span style='margin: 0 5px; font-size: 20px;'>{op_symbol}</span>{frac_equiv2}</div>{arrow}<div style='{current_style}'><span>⏳ Operando...</span></div></div>"
    elif step_now == 4:
        result_num = new_num1 + new_num2 if op == "+" else new_num1 - new_num2
        frac_result = _pretty_frac(result_num, common_den, text_color)
        return f"<div class='{banner_class}' style='{banner_style}'><div style='{done_style}'><span style='font-size: 14px; margin-right: 4px;'>📝</span>{frac1}<span style='margin: 0 3px;'>{op_symbol}</span>{frac2}</div>{arrow}<div style='{done_style}'>{frac_equiv1}<span style='margin: 0 3px;'>{op_symbol}</span>{frac_equiv2}</div>{arrow}<div style='display: inline-flex; align-items: center; color: {text_color};'>{frac_result}</div>{arrow}<div style='{current_style}'><span>⏳ Simplificando...</span></div></div>"
    else:
        result_num = new_num1 + new_num2 if op == "+" else new_num1 - new_num2
        result_final = f1 + f2 if op == "+" else f1 - f2
        frac_result = _pretty_frac(result_num, common_den, text_color)
        frac_final = _pretty_frac(result_final.numerator, result_final.denominator, text_color)
        return f"<div class='{banner_class}' style='{banner_style}'><div style='{done_style}'><span style='font-size: 13px; margin-right: 3px;'>📝</span>{frac1}<span style='margin: 0 2px;'>{op_symbol}</span>{frac2}</div>{arrow}<div style='{done_style}'>{frac_equiv1}<span style='margin: 0 2px;'>{op_symbol}</span>{frac_equiv2}</div>{arrow}<div style='{done_style}'>{frac_result}</div>{arrow}<div style='display: inline-flex; align-items: center; color: #2e7d32; font-weight: bold; gap: 5px;'><span style='font-size: 20px;'>✅</span>{frac_final}</div></div>"


# ──────────────────────────────────────────────
# Motor principal (CON PISTAS INTEGRADAS Y CONTEXTO CORRECTO)
# ──────────────────────────────────────────────

def handle_step(question: str, step_now: int, last_answer: str, error_count: int, cycle: str = "c2"):
    parsed = _parse_frac_with_op(question)
    if not parsed:
        return {
            "status": "error",
            "message": "⚠️ No pude entender la operación. Por favor escribe algo como: <b>2/3 + 1/4</b>.",
            "topic": "matematicas",
            "hint_type": "frac_inicio",
            "next_step": step_now
        }
    
    f1, f2, op = parsed
    op_symbol = " + " if op == "+" else " - "
    
    # ✅ CONTEXTO CORRECTO: hints_fractions.py necesita el marcador [FRAC:...]
    context_marker = f"[FRAC:{f1.numerator}/{f1.denominator}{op}{f2.numerator}/{f2.denominator}]"
    
    # Marcador oculto para el HTML (visualización)
    hidden_marker = f"<span style='display:none'>{context_marker}</span>"
    
    progress_banner = _build_progress_banner(f1, f2, op, step_now)
    text_color = "#1e3a8a"
    frac1_visual = _pretty_frac(f1.numerator, f1.denominator, text_color)
    frac2_visual = _pretty_frac(f2.numerator, f2.denominator, text_color)

    # ✅ DETECTAR si pidió ayuda
    asking_for_help = _is_asking_for_help(last_answer)

    # Paso 0: ¿Tienen el mismo denominador?
    if step_now == 0:
        same_den = f1.denominator == f2.denominator
        expected = "sí" if same_den else "no"
        msg = f"{progress_banner}<div style='margin-top: 10px;'>👉 Observa las fracciones: {frac1_visual} y {frac2_visual}<br/>¿Tienen el mismo denominador?</div>{hidden_marker}"
        
        # ✅ AÑADIR PISTA con contexto correcto
        if error_count > 0 or asking_for_help:
            hint = _generate_hint("frac_inicio", error_count, context_marker)
            msg += f"<div style='padding:10px;background:#fff9c4;border-radius:6px;margin-top:10px;border-left:3px solid #fbc02d'>💡 {hint}</div>"
        
        return {"status": "ask", "message": msg, "expected_answer": expected, "topic": "matematicas", "hint_type": "frac_inicio", "next_step": 1}

    # Paso 1: m.c.m.
    if step_now == 1:
        common_den = lcm(f1.denominator, f2.denominator)
        msg = f"{progress_banner}<div style='margin-top: 10px;'>👉 Calcula el <b>mínimo común múltiplo (m.c.m.)</b> de <strong style='color: #5B9BD5;'>{f1.denominator}</strong> y <strong style='color: #5B9BD5;'>{f2.denominator}</strong>.<br/>¿Cuál es el m.c.m.?</div>{hidden_marker}"
        
        if error_count > 0 or asking_for_help:
            hint = _generate_hint("frac_mcm", error_count, context_marker)
            msg += f"<div style='padding:10px;background:#fff9c4;border-radius:6px;margin-top:10px;border-left:3px solid #fbc02d'>💡 {hint}</div>"
        
        return {"status": "ask", "message": msg, "expected_answer": str(common_den), "topic": "matematicas", "hint_type": "frac_mcm", "next_step": 2}

    # Paso 2: Equivalentes
    if step_now == 2:
        common_den = lcm(f1.denominator, f2.denominator)
        factor1, factor2 = common_den // f1.denominator, common_den // f2.denominator
        new_num1, new_num2 = f1.numerator * factor1, f2.numerator * factor2
        msg = f"{progress_banner}<div style='margin-top: 10px;'>👉 Convierte ambas fracciones al denominador común <strong style='color: #5B9BD5;'>{common_den}</strong>.<br/>Para {frac1_visual}: multiplica {f1.numerator} × {factor1}<br/>Para {frac2_visual}: multiplica {f2.numerator} × {factor2}<br/>Escribe los dos nuevos numeradores separados por 'y' (ejemplo: 6 y 8).</div>{hidden_marker}"
        
        if error_count > 0 or asking_for_help:
            hint = _generate_hint("frac_equiv", error_count, context_marker)
            msg += f"<div style='padding:10px;background:#fff9c4;border-radius:6px;margin-top:10px;border-left:3px solid #fbc02d'>💡 {hint}</div>"
        
        return {"status": "ask", "message": msg, "expected_answer": f"{new_num1} y {new_num2}", "topic": "matematicas", "hint_type": "frac_equiv", "next_step": 3}

    # Paso 3: Operación
    if step_now == 3:
        common_den = lcm(f1.denominator, f2.denominator)
        factor1, factor2 = common_den // f1.denominator, common_den // f2.denominator
        new_num1, new_num2 = f1.numerator * factor1, f2.numerator * factor2
        result_num = new_num1 + new_num2 if op == "+" else new_num1 - new_num2
        frac_equiv1_visual = _pretty_frac(new_num1, common_den, text_color)
        frac_equiv2_visual = _pretty_frac(new_num2, common_den, text_color)
        msg = f"{progress_banner}<div style='margin-top: 10px;'>👉 Ahora que ambas fracciones tienen denominador <strong style='color: #5B9BD5;'>{common_den}</strong>, {('suma' if op == '+' else 'resta')} los numeradores:<br/>{frac_equiv1_visual} {op_symbol} {frac_equiv2_visual}<br/>Escribe el resultado como fracción (ejemplo: 15/20).</div>{hidden_marker}"
        
        if error_count > 0 or asking_for_help:
            hint = _generate_hint("frac_operacion", error_count, context_marker)
            msg += f"<div style='padding:10px;background:#fff9c4;border-radius:6px;margin-top:10px;border-left:3px solid #fbc02d'>💡 {hint}</div>"
        
        return {"status": "ask", "message": msg, "expected_answer": f"{result_num}/{common_den}", "topic": "matematicas", "hint_type": "frac_operacion", "next_step": 4}

    # Paso 4: Simplificar
    if step_now == 4:
        common_den = lcm(f1.denominator, f2.denominator)
        factor1, factor2 = common_den // f1.denominator, common_den // f2.denominator
        new_num1, new_num2 = f1.numerator * factor1, f2.numerator * factor2
        result_num = new_num1 + new_num2 if op == "+" else new_num1 - new_num2
        unsimplified = Fraction(result_num, common_den)
        frac_unsimplified_visual = _pretty_frac(result_num, common_den, text_color)
        msg = f"{progress_banner}<div style='margin-top: 10px;'>👉 ¡Muy bien! Obtuviste {frac_unsimplified_visual}<br/>Ahora <b>simplifícala</b> al máximo.<br/>¿Cuál es la fracción simplificada?</div>{hidden_marker}"
        
        if error_count > 0 or asking_for_help:
            hint = _generate_hint("frac_simplificar", error_count, context_marker)
            msg += f"<div style='padding:10px;background:#fff9c4;border-radius:6px;margin-top:10px;border-left:3px solid #fbc02d'>💡 {hint}</div>"
        
        return {"status": "ask", "message": msg, "expected_answer": str(unsimplified), "topic": "matematicas", "hint_type": "frac_simplificar", "next_step": 5}

    # Paso 5: Éxito
    if step_now == 5:
        result = f1 + f2 if op == "+" else f1 - f2
        result_visual = _pretty_frac(result.numerator, result.denominator, text_color)
        msg = f"{progress_banner}<div style='margin-top: 10px;'>✅ ¡Excelente trabajo! 🎉<br/>La respuesta final es: {result_visual}<br/>Has completado el ejercicio correctamente.</div>{hidden_marker}"
        return {"status": "done", "message": msg, "expected_answer": str(result), "topic": "matematicas", "hint_type": "frac_simplificar", "next_step": 6}

    return {"status": "done", "message": "✅ ¡Has terminado la actividad!", "expected_answer": "ok", "topic": "matematicas", "hint_type": "frac_simplificar", "next_step": step_now + 1}
