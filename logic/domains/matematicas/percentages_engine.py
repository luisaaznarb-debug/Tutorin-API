# -*- coding: utf-8 -*-
"""
percentages_engine.py
Motor para cálculo de porcentajes.
✅ VERSIÓN CORREGIDA V3:
- Ahora tiene 3 pasos reales de cálculo
- No da resultados antes de tiempo
- Más explicación en cada paso
"""

import re
from typing import Dict, Any, Optional, Tuple

# ══════════════════════════════════════════════════════════════
# FUNCIONES AUXILIARES
# ══════════════════════════════════════════════════════════════

def _canon(s: str) -> str:
    """Normaliza texto para comparación."""
    return str(s or "").strip().lower().replace(" ", "").replace(",", ".")

def _parse_percentage(question: str) -> Optional[Tuple[int, int]]:
    """
    Detecta expresiones tipo '25% de 80' o '30 por ciento de 50'.
    Retorna: (porcentaje, cantidad_base) o None
    """
    q = question.lower().replace("por ciento", "%").replace("percent", "%")
    m = re.search(r"(\d+)\s*%\s*(de|of)?\s*(\d+)", q)
    if m:
        percent = int(m.group(1))
        base = int(m.group(3))
        return percent, base
    return None

def _format_number(num: float) -> str:
    """Formatea un número eliminando ceros innecesarios."""
    # Si es entero, mostrar sin decimales
    if num == int(num):
        return str(int(num))
    # Si tiene decimales, mostrar con precisión
    return f"{num:.2f}".rstrip('0').rstrip('.')

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
    Maneja cálculo de porcentajes paso a paso.
    
    Pasos:
    - 0: Convertir porcentaje a fracción (75% → 75/100)
    - 1: Calcular multiplicación (25 × 75 = ?)
    - 2: Dividir entre 100 (resultado ÷ 100 = ?)
    - 3: Done
    """
    
    # ──────────────────────────────────────────────────────────
    # VALIDAR Y EXTRAER OPERACIÓN
    # ──────────────────────────────────────────────────────────
    parsed = _parse_percentage(prompt)
    if not parsed:
        return {
            "status": "ask",
            "message": (
                "📝 Necesito una pregunta sobre porcentajes.<br/><br/>"
                "💡 <b>Ejemplos válidos:</b><br/>"
                "• <code>25% de 80</code><br/>"
                "• <code>30 por ciento de 50</code><br/>"
                "• <code>15% de 200</code>"
            ),
            "expected_answer": None,
            "topic": "porcentajes",
            "hint_type": "percent_error",
            "next_step": 0
        }
    
    percent, base = parsed
    multiplication_result = percent * base
    final_result = multiplication_result / 100
    
    # ──────────────────────────────────────────────────────────
    # PASO 0: Convertir porcentaje a fracción
    # ──────────────────────────────────────────────────────────
    if step == 0:
        # Si no hay respuesta todavía, hacer la pregunta
        if _canon(answer) == "":
            msg = (
                f"✨ Vamos a calcular el <b>{percent}% de {base}</b>.<br/><br/>"
                f"📝 <b>Paso 1:</b> Convertir el porcentaje a fracción.<br/><br/>"
                f"💡 <b>Recuerda:</b> El símbolo <b>%</b> significa <i>'de cada 100'</i>.<br/>"
                f"Por ejemplo: <b>25%</b> = <b>25/100</b><br/><br/>"
                f"✏️ Escribe <b>{percent}%</b> como fracción (ejemplo: <code>25/100</code>)"
            )
            
            return {
                "status": "ask",
                "message": msg,
                "expected_answer": f"{percent}/100",
                "topic": "porcentajes",
                "hint_type": "perc_frac",
                "next_step": 1
            }
        
        # Validar respuesta del usuario
        user_answer = _canon(answer)
        expected_answer = _canon(f"{percent}/100")
        
        if user_answer == expected_answer:
            return {
                "status": "ask",
                "message": "✅ ¡Correcto! Ahora vamos a calcular el resultado.",
                "expected_answer": f"{percent}/100",
                "topic": "porcentajes",
                "hint_type": "perc_frac",
                "next_step": 1
            }
        else:
            return {
                "status": "feedback",
                "message": f"❌ No es exactamente. Recuerda que {percent}% = {percent}/100",
                "expected_answer": f"{percent}/100",
                "topic": "porcentajes",
                "hint_type": "perc_frac",
                "next_step": 0
            }
    
    # ──────────────────────────────────────────────────────────
    # PASO 1: Calcular la multiplicación (base × porcentaje)
    # ──────────────────────────────────────────────────────────
    elif step == 1:
        # Si no hay respuesta todavía, hacer la pregunta
        if _canon(answer) == "":
            msg = (
                f"📝 <b>Paso 2:</b> Ahora vamos a multiplicar.<br/><br/>"
                f"💡 <b>¿Por qué multiplicamos?</b><br/>"
                f"Para calcular el <b>{percent}% de {base}</b>, primero necesitamos hacer: <b>{base} × {percent}</b><br/><br/>"
                f"🔹 <b>Explicación:</b><br/>"
                f"• Estamos calculando {percent} partes de cada 100<br/>"
                f"• Por eso multiplicamos {base} (la cantidad total) por {percent} (las partes que queremos)<br/><br/>"
                f"✏️ ¿Cuánto es <b>{base} × {percent}</b>?<br/>"
                f"<small>(Puedes usar la calculadora si lo necesitas)</small>"
            )
            
            return {
                "status": "ask",
                "message": msg,
                "expected_answer": str(multiplication_result),
                "topic": "porcentajes",
                "hint_type": "perc_multiply",
                "next_step": 2
            }
        
        # Validar respuesta del usuario
        try:
            user_value = int(_canon(answer))
            
            if user_value == multiplication_result:
                return {
                    "status": "ask",
                    "message": (
                        f"✅ ¡Correcto! <b>{base} × {percent} = {multiplication_result}</b><br/><br/>"
                        f"Ahora falta el último paso. 🎯"
                    ),
                    "expected_answer": str(multiplication_result),
                    "topic": "porcentajes",
                    "hint_type": "perc_multiply",
                    "next_step": 2
                }
            else:
                return {
                    "status": "feedback",
                    "message": (
                        f"❌ No es correcto.<br/><br/>"
                        f"💡 Intenta calcular de nuevo: <b>{base} × {percent}</b>"
                    ),
                    "expected_answer": str(multiplication_result),
                    "topic": "porcentajes",
                    "hint_type": "perc_multiply",
                    "next_step": 1
                }
        
        except ValueError:
            return {
                "status": "feedback",
                "message": "❌ Eso no es un número válido. Intenta de nuevo.",
                "expected_answer": str(multiplication_result),
                "topic": "porcentajes",
                "hint_type": "perc_multiply",
                "next_step": 1
            }
    
    # ──────────────────────────────────────────────────────────
    # PASO 2: Dividir entre 100
    # ──────────────────────────────────────────────────────────
    elif step == 2:
        # Si no hay respuesta todavía, hacer la pregunta
        if _canon(answer) == "":
            msg = (
                f"📝 <b>Paso 3:</b> Ahora divide entre 100.<br/><br/>"
                f"💡 <b>¿Por qué dividir entre 100?</b><br/>"
                f"Porque el porcentaje significa <i>'de cada 100'</i>. Al dividir entre 100, obtenemos el resultado final.<br/><br/>"
                f"🔹 <b>Cálculo:</b><br/>"
                f"Ya tenemos: <b>{multiplication_result}</b><br/>"
                f"Ahora hacemos: <b>{multiplication_result} ÷ 100</b> = <b>?</b><br/><br/>"
                f"💡 <b>Truco rápido:</b> Mover la coma dos posiciones a la izquierda:<br/>"
                f"<code>{multiplication_result}</code> → <code>{multiplication_result / 10}</code> → <code>?</code><br/><br/>"
                f"✏️ ¿Cuánto es <b>{multiplication_result} ÷ 100</b>?"
            )
            
            return {
                "status": "ask",
                "message": msg,
                "expected_answer": _format_number(final_result),
                "topic": "porcentajes",
                "hint_type": "perc_divide",
                "next_step": 3
            }
        
        # Validar respuesta del usuario
        try:
            user_value = float(_canon(answer))
            
            # Tolerancia de 0.01 para decimales
            if abs(user_value - final_result) < 0.01:
                return {
                    "status": "done",
                    "message": (
                        f"🎉 ¡Perfecto! El <b>{percent}% de {base}</b> es <b>{_format_number(final_result)}</b>.<br/><br/>"
                        f"✅ Has completado todos los pasos correctamente. ¡Excelente trabajo! 🌟<br/><br/>"
                        f"📚 <b>Resumen del proceso:</b><br/>"
                        f"1️⃣ {percent}% = {percent}/100<br/>"
                        f"2️⃣ {base} × {percent} = {multiplication_result}<br/>"
                        f"3️⃣ {multiplication_result} ÷ 100 = <b>{_format_number(final_result)}</b><br/><br/>"
                        f"💡 <b>Recuerda:</b> Para calcular porcentajes, multiplica y luego divide entre 100."
                    ),
                    "expected_answer": _format_number(final_result),
                    "topic": "porcentajes",
                    "hint_type": "perc_result",
                    "next_step": 3
                }
            else:
                return {
                    "status": "feedback",
                    "message": (
                        f"❌ No es correcto.<br/><br/>"
                        f"💡 Recuerda: <b>{multiplication_result} ÷ 100</b><br/>"
                        f"Puedes mover la coma dos posiciones a la izquierda."
                    ),
                    "expected_answer": _format_number(final_result),
                    "topic": "porcentajes",
                    "hint_type": "perc_divide",
                    "next_step": 2
                }
        
        except ValueError:
            return {
                "status": "feedback",
                "message": "❌ Eso no es un número válido. Intenta de nuevo.",
                "expected_answer": _format_number(final_result),
                "topic": "porcentajes",
                "hint_type": "perc_divide",
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
                f"Has aprendido a calcular el <b>{percent}% de {base} = {_format_number(final_result)}</b>. 🎉"
            ),
            "expected_answer": _format_number(final_result),
            "topic": "porcentajes",
            "hint_type": "perc_complete",
            "next_step": 4
        }
