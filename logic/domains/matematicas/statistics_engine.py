# -*- coding: utf-8 -*-
"""
statistics_engine.py
Motor para probabilidad y estadística básica.
✅ VERSIÓN CORREGIDA:
- Ahora VALIDA las respuestas del usuario
- NO revela el resultado, pide al alumno que calcule
- Flujo simplificado (3 pasos útiles)
- Compatible con solve.py
"""

import re
from typing import Dict, Any, Optional, Tuple, List

# ══════════════════════════════════════════════════════════════
# FUNCIONES AUXILIARES
# ══════════════════════════════════════════════════════════════

def _canon(s: str) -> str:
    """Normaliza texto para comparación."""
    return str(s or "").strip().lower().replace(" ", "").replace(",", ".").replace("%", "")

def _parse_statistics(question: str) -> Optional[Tuple[str, List[float]]]:
    """
    Detecta tipo de ejercicio y extrae números.
    Retorna: (tipo, [números]) o None
    """
    q = question.lower().replace(",", ".")
    
    # Buscar números
    nums = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", q)]
    if not nums:
        return None
    
    # Detección del tipo de ejercicio
    tipo = "probabilidad"  # por defecto
    if "probabilidad" in q or "azar" in q or "moneda" in q or "dado" in q:
        tipo = "probabilidad"
    elif "porcentaje" in q or "%" in q or "gráfico" in q or "grafico" in q:
        tipo = "porcentaje"
    elif "frecuencia" in q or "encuesta" in q:
        tipo = "frecuencia"
    
    return tipo, nums

def _format_number(num: float) -> str:
    """Formatea un número eliminando ceros innecesarios."""
    if num == int(num):
        return str(int(num))
    return f"{num:.3f}".rstrip('0').rstrip('.')

# ══════════════════════════════════════════════════════════════
# MOTOR PRINCIPAL
# ══════════════════════════════════════════════════════════════

def handle_step(
    prompt: str, 
    step: int, 
    answer: str, 
    errors: int, 
    cycle: str = "c2"
) -> Dict[str, Any]:
    """
    Maneja cálculo de probabilidad y estadística paso a paso.
    
    Pasos:
    - 0: Identificar fracción (casos favorables/total)
    - 1: Calcular probabilidad decimal
    - 2: Convertir a porcentaje
    - 3: Done
    """
    
    # ──────────────────────────────────────────────────────────
    # VALIDAR Y EXTRAER DATOS
    # ──────────────────────────────────────────────────────────
    parsed = _parse_statistics(prompt)
    if not parsed:
        return {
            "status": "ask",
            "message": (
                "📝 Necesito un problema de probabilidad o estadística.<br/><br/>"
                "💡 <b>Ejemplos válidos:</b><br/>"
                "• <code>Probabilidad de sacar 3 casos favorables de 10 totales</code><br/>"
                "• <code>Si 5 de 20 alumnos prefieren azul, ¿qué porcentaje?</code><br/>"
                "• <code>Frecuencia: 8 respuestas positivas de 40 encuestados</code>"
            ),
            "expected_answer": None,
            "topic": "estadistica",
            "hint_type": "stat_error",
            "next_step": 0
        }
    
    tipo, nums = parsed
    
    # Interpretación: primeros 2 números → casos favorables / totales
    if len(nums) >= 2:
        favorables, total = nums[0], nums[1]
    else:
        return {
            "status": "ask",
            "message": "❌ Necesito al menos dos números: casos favorables y total de casos.",
            "expected_answer": None,
            "topic": "estadistica",
            "hint_type": "stat_error",
            "next_step": 0
        }
    
    if total == 0:
        return {
            "status": "ask",
            "message": "❌ El total de casos no puede ser cero.",
            "expected_answer": None,
            "topic": "estadistica",
            "hint_type": "stat_error",
            "next_step": 0
        }
    
    prob_decimal = favorables / total
    prob_percent = prob_decimal * 100
    
    tipo_nombre = "probabilidad" if tipo == "probabilidad" else "frecuencia relativa"
    
    # ──────────────────────────────────────────────────────────
    # PASO 0: Identificar la fracción
    # ──────────────────────────────────────────────────────────
    if step == 0:
        # Si no hay respuesta todavía, hacer la pregunta
        if _canon(answer) == "":
            msg = (
                f"✨ Vamos a calcular la <b>{tipo_nombre}</b>.<br/><br/>"
                f"📝 <b>Datos:</b><br/>"
                f"• Casos favorables: <b>{_format_number(favorables)}</b><br/>"
                f"• Total de casos: <b>{_format_number(total)}</b><br/><br/>"
                f"💡 <b>Paso 1:</b> Para calcular la {tipo_nombre}, dividimos:<br/>"
                f"<b>casos favorables ÷ total de casos</b><br/><br/>"
                f"✏️ Escribe la fracción (ejemplo: <code>3/10</code> o <code>5/20</code>)"
            )
            
            expected = f"{int(favorables) if favorables == int(favorables) else favorables}/{int(total) if total == int(total) else total}"
            
            return {
                "status": "ask",
                "message": msg,
                "expected_answer": expected,
                "topic": "estadistica",
                "hint_type": "stat_intro",
                "next_step": 1
            }
        
        # Validar respuesta del usuario
        user_answer = _canon(answer)
        
        # Construir expected con diferentes formatos aceptables
        expected_formats = [
            f"{int(favorables)}/{int(total)}",
            f"{favorables}/{total}",
        ]
        
        # Validar si coincide con algún formato
        is_correct = any(user_answer == _canon(fmt) for fmt in expected_formats)
        
        # También validar si es una fracción equivalente simplificada
        if "/" in user_answer:
            try:
                parts = user_answer.split("/")
                user_num = float(parts[0])
                user_den = float(parts[1])
                # Verificar si la fracción es equivalente
                if abs((user_num / user_den) - (favorables / total)) < 0.001:
                    is_correct = True
            except:
                pass
        
        if is_correct:
            return {
                "status": "ask",
                "message": "✅ ¡Correcto! Ahora vamos a calcular el valor decimal.",
                "expected_answer": f"{int(favorables)}/{int(total)}",
                "topic": "estadistica",
                "hint_type": "stat_intro",
                "next_step": 1
            }
        else:
            return {
                "status": "feedback",
                "message": (
                    f"❌ No es exactamente.<br/><br/>"
                    f"💡 La fracción es: <b>{int(favorables)}/{int(total)}</b>"
                ),
                "expected_answer": f"{int(favorables)}/{int(total)}",
                "topic": "estadistica",
                "hint_type": "stat_intro",
                "next_step": 0
            }
    
    # ──────────────────────────────────────────────────────────
    # PASO 1: Calcular probabilidad decimal
    # ──────────────────────────────────────────────────────────
    elif step == 1:
        # Si no hay respuesta todavía, hacer la pregunta
        if _canon(answer) == "":
            msg = (
                f"📝 <b>Paso 2:</b> Ahora calcula el valor decimal.<br/><br/>"
                f"💡 <b>Operación:</b> Divide los casos favorables entre el total:<br/>"
                f"<b>{_format_number(favorables)} ÷ {_format_number(total)}</b><br/><br/>"
                f"✏️ ¿Cuál es el resultado? (redondea a 3 decimales si es necesario)"
            )
            
            return {
                "status": "ask",
                "message": msg,
                "expected_answer": _format_number(prob_decimal),
                "topic": "estadistica",
                "hint_type": "stat_decimal",
                "next_step": 2
            }
        
        # Validar respuesta del usuario
        try:
            user_value = float(_canon(answer))
            expected_value = prob_decimal
            
            # Tolerancia de 0.01 para redondeos
            if abs(user_value - expected_value) < 0.01:
                return {
                    "status": "ask",
                    "message": f"✅ ¡Perfecto! La {tipo_nombre} es <b>{_format_number(prob_decimal)}</b>. Ahora vamos a expresarlo en porcentaje.",
                    "expected_answer": _format_number(prob_decimal),
                    "topic": "estadistica",
                    "hint_type": "stat_decimal",
                    "next_step": 2
                }
            else:
                return {
                    "status": "feedback",
                    "message": (
                        f"❌ No es correcto.<br/><br/>"
                        f"💡 Recuerda: {_format_number(favorables)} ÷ {_format_number(total)}"
                    ),
                    "expected_answer": _format_number(prob_decimal),
                    "topic": "estadistica",
                    "hint_type": "stat_decimal",
                    "next_step": 1
                }
        
        except ValueError:
            return {
                "status": "feedback",
                "message": "❌ Eso no es un número válido. Intenta de nuevo.",
                "expected_answer": _format_number(prob_decimal),
                "topic": "estadistica",
                "hint_type": "stat_decimal",
                "next_step": 1
            }
    
    # ──────────────────────────────────────────────────────────
    # PASO 2: Convertir a porcentaje
    # ──────────────────────────────────────────────────────────
    elif step == 2:
        # Si no hay respuesta todavía, hacer la pregunta
        if _canon(answer) == "":
            msg = (
                f"📝 <b>Paso 3:</b> Ahora convierte a porcentaje.<br/><br/>"
                f"💡 <b>Operación:</b> Multiplica por 100:<br/>"
                f"<b>{_format_number(prob_decimal)} × 100</b><br/><br/>"
                f"✏️ ¿Cuál es el porcentaje? (puedes incluir el símbolo % o no)"
            )
            
            return {
                "status": "ask",
                "message": msg,
                "expected_answer": f"{_format_number(prob_percent)}",
                "topic": "estadistica",
                "hint_type": "stat_percent",
                "next_step": 3
            }
        
        # Validar respuesta del usuario
        try:
            user_answer_clean = _canon(answer)
            user_value = float(user_answer_clean)
            expected_value = prob_percent
            
            # Tolerancia de 0.1 para redondeos
            if abs(user_value - expected_value) < 0.1:
                return {
                    "status": "done",
                    "message": (
                        f"🎉 ¡Excelente! La <b>{tipo_nombre}</b> es:<br/><br/>"
                        f"• <b>Fracción:</b> {int(favorables)}/{int(total)}<br/>"
                        f"• <b>Decimal:</b> {_format_number(prob_decimal)}<br/>"
                        f"• <b>Porcentaje:</b> {_format_number(prob_percent)}%<br/><br/>"
                        f"✅ Esto significa que ocurrirá aproximadamente <b>{_format_number(prob_percent)}%</b> de las veces. ¡Muy buen trabajo! 🌟<br/><br/>"
                        f"📚 <b>Interpretación:</b><br/>"
                        f"De cada 100 casos, aproximadamente {int(round(prob_percent))} serán favorables."
                    ),
                    "expected_answer": f"{_format_number(prob_percent)}%",
                    "topic": "estadistica",
                    "hint_type": "stat_result",
                    "next_step": 3
                }
            else:
                return {
                    "status": "feedback",
                    "message": (
                        f"❌ No es correcto.<br/><br/>"
                        f"💡 Recuerda: {_format_number(prob_decimal)} × 100"
                    ),
                    "expected_answer": f"{_format_number(prob_percent)}",
                    "topic": "estadistica",
                    "hint_type": "stat_percent",
                    "next_step": 2
                }
        
        except ValueError:
            return {
                "status": "feedback",
                "message": "❌ Eso no es un número válido. Intenta de nuevo.",
                "expected_answer": f"{_format_number(prob_percent)}",
                "topic": "estadistica",
                "hint_type": "stat_percent",
                "next_step": 2
            }
    
    # ──────────────────────────────────────────────────────────
    # PASO 3: Ejercicio completado
    # ──────────────────────────────────────────────────────────
    else:
        return {
            "status": "done",
            "message": (
                f"✅ ¡Ejercicio completado!<br/><br/>"
                f"Has aprendido a calcular <b>{tipo_nombre}</b> y expresarla en diferentes formatos. 🎉"
            ),
            "expected_answer": f"{_format_number(prob_percent)}%",
            "topic": "estadistica",
            "hint_type": "stat_complete",
            "next_step": 4
        }