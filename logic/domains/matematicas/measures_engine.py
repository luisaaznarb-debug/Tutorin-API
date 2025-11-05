# -*- coding: utf-8 -*-
"""
measures_engine.py
Motor para conversión de unidades de medida.
✅ VERSIÓN CORREGIDA:
- Ahora VALIDA las respuestas del usuario
- NO revela el resultado, pide al alumno que calcule
- Paso 1 útil (pide identificar factor)
- Compatible con solve.py
"""

import re
from typing import Dict, Any, Optional, Tuple

# ══════════════════════════════════════════════════════════════
# DICCIONARIO DE EQUIVALENCIAS
# ══════════════════════════════════════════════════════════════

_CONVERSIONS = {
    # Longitud
    "km": {"m": 1000, "cm": 100000, "mm": 1000000},
    "m": {"km": 0.001, "cm": 100, "mm": 1000},
    "cm": {"m": 0.01, "km": 0.00001, "mm": 10},
    "mm": {"m": 0.001, "cm": 0.1, "km": 0.000001},
    # Masa
    "kg": {"g": 1000, "mg": 1000000},
    "g": {"kg": 0.001, "mg": 1000},
    "mg": {"g": 0.001, "kg": 0.000001},
    # Capacidad
    "l": {"ml": 1000, "cl": 100, "dl": 10},
    "ml": {"l": 0.001, "cl": 0.1, "dl": 0.01},
    "cl": {"l": 0.01, "ml": 10, "dl": 0.1},
    "dl": {"l": 0.1, "ml": 100, "cl": 10}
}

# ══════════════════════════════════════════════════════════════
# FUNCIONES AUXILIARES
# ══════════════════════════════════════════════════════════════

def _canon(s: str) -> str:
    """Normaliza texto para comparación."""
    return str(s or "").strip().lower().replace(" ", "").replace(",", ".")

def _parse_conversion(question: str) -> Optional[Tuple[float, str, str]]:
    """
    Detecta expresiones tipo '3 km a m' o '2500 ml a l'.
    Retorna: (valor, unidad_origen, unidad_destino) o None
    """
    q = question.lower().replace(",", ".")
    m = re.search(r"(\d+(?:\.\d+)?)\s*([a-z]+)\s*(a|to)\s*([a-z]+)", q)
    if not m:
        return None
    
    value = float(m.group(1))
    from_unit = m.group(2)
    to_unit = m.group(4)
    return value, from_unit, to_unit

def _find_factor(from_unit: str, to_unit: str) -> Optional[float]:
    """Busca el factor de conversión directo si existe."""
    if from_unit in _CONVERSIONS and to_unit in _CONVERSIONS[from_unit]:
        return _CONVERSIONS[from_unit][to_unit]
    return None

def _format_number(num: float) -> str:
    """Formatea un número eliminando ceros innecesarios."""
    if num == int(num):
        return str(int(num))
    return f"{num:.4f}".rstrip('0').rstrip('.')

def _get_unit_type(unit: str) -> Optional[str]:
    """Identifica el tipo de magnitud de una unidad."""
    longitud = ["km", "m", "cm", "mm"]
    masa = ["kg", "g", "mg"]
    capacidad = ["l", "ml", "cl", "dl"]
    
    if unit in longitud:
        return "longitud"
    elif unit in masa:
        return "masa"
    elif unit in capacidad:
        return "capacidad"
    return None

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
    Maneja conversión de unidades paso a paso.
    
    Pasos:
    - 0: Identificar factor de conversión
    - 1: Calcular resultado
    - 2: Done
    """
    
    # ──────────────────────────────────────────────────────────
    # VALIDAR Y EXTRAER CONVERSIÓN
    # ──────────────────────────────────────────────────────────
    parsed = _parse_conversion(prompt)
    if not parsed:
        return {
            "status": "ask",
            "message": (
                "📝 Necesito una conversión de unidades.<br/><br/>"
                "💡 <b>Ejemplos válidos:</b><br/>"
                "• <code>3 km a m</code><br/>"
                "• <code>2500 ml a l</code><br/>"
                "• <code>1.5 kg a g</code><br/>"
                "• <code>150 cm a m</code>"
            ),
            "expected_answer": None,
            "topic": "medidas",
            "hint_type": "meas_error",
            "next_step": 0
        }
    
    value, from_unit, to_unit = parsed
    factor = _find_factor(from_unit, to_unit)
    
    if factor is None:
        return {
            "status": "ask",
            "message": f"❌ No conozco la conversión entre <b>{from_unit}</b> y <b>{to_unit}</b> todavía.",
            "expected_answer": None,
            "topic": "medidas",
            "hint_type": "meas_unknown",
            "next_step": 0
        }
    
    # Validar que sean del mismo tipo
    type_from = _get_unit_type(from_unit)
    type_to = _get_unit_type(to_unit)
    
    if type_from != type_to:
        return {
            "status": "ask",
            "message": f"❌ No puedo convertir {from_unit} ({type_from}) a {to_unit} ({type_to}). Deben ser del mismo tipo.",
            "expected_answer": None,
            "topic": "medidas",
            "hint_type": "meas_error",
            "next_step": 0
        }
    
    result = value * factor
    
    # ──────────────────────────────────────────────────────────
    # PASO 0: Identificar factor de conversión
    # ──────────────────────────────────────────────────────────
    if step == 0:
        # Si no hay respuesta todavía, hacer la pregunta
        if _canon(answer) == "":
            # Determinar tabla de referencia según tipo
            tabla = ""
            if type_from == "longitud":
                tabla = (
                    "📏 <b>Tabla de longitud:</b><br/>"
                    "• 1 km = 1000 m<br/>"
                    "• 1 m = 100 cm<br/>"
                    "• 1 cm = 10 mm"
                )
            elif type_from == "masa":
                tabla = (
                    "⚖️ <b>Tabla de masa:</b><br/>"
                    "• 1 kg = 1000 g<br/>"
                    "• 1 g = 1000 mg"
                )
            elif type_from == "capacidad":
                tabla = (
                    "🥤 <b>Tabla de capacidad:</b><br/>"
                    "• 1 l = 1000 ml<br/>"
                    "• 1 l = 100 cl<br/>"
                    "• 1 l = 10 dl"
                )
            
            msg = (
                f"✨ Vamos a convertir <b>{_format_number(value)} {from_unit}</b> a <b>{to_unit}</b>.<br/><br/>"
                f"{tabla}<br/><br/>"
                f"📝 <b>Paso 1:</b> Identifica el factor de conversión.<br/><br/>"
                f"💡 <b>Pregunta:</b> ¿Por cuánto tenemos que multiplicar para pasar de <b>{from_unit}</b> a <b>{to_unit}</b>?<br/>"
                f"(Ejemplo: de km a m multiplicamos por 1000)"
            )
            
            return {
                "status": "ask",
                "message": msg,
                "expected_answer": _format_number(factor),
                "topic": "medidas",
                "hint_type": "meas_factor",
                "next_step": 1
            }
        
        # Validar respuesta del usuario
        try:
            user_value = float(_canon(answer))
            expected_value = factor
            
            # Tolerancia de 0.001 para decimales
            if abs(user_value - expected_value) < 0.001:
                return {
                    "status": "ask",
                    "message": f"✅ ¡Correcto! El factor es <b>{_format_number(factor)}</b>. Ahora vamos a calcular.",
                    "expected_answer": _format_number(factor),
                    "topic": "medidas",
                    "hint_type": "meas_factor",
                    "next_step": 1
                }
            else:
                return {
                    "status": "feedback",
                    "message": (
                        f"❌ No es exactamente.<br/><br/>"
                        f"💡 Piensa: ¿cuántos {to_unit} hay en 1 {from_unit}?"
                    ),
                    "expected_answer": _format_number(factor),
                    "topic": "medidas",
                    "hint_type": "meas_factor",
                    "next_step": 0
                }
        
        except ValueError:
            return {
                "status": "feedback",
                "message": "❌ Eso no es un número válido. Intenta de nuevo.",
                "expected_answer": _format_number(factor),
                "topic": "medidas",
                "hint_type": "meas_factor",
                "next_step": 0
            }
    
    # ──────────────────────────────────────────────────────────
    # PASO 1: Calcular resultado
    # ──────────────────────────────────────────────────────────
    elif step == 1:
        # Si no hay respuesta todavía, hacer la pregunta
        if _canon(answer) == "":
            operacion = "multiplicar" if factor >= 1 else "dividir"
            factor_mostrar = factor if factor >= 1 else (1 / factor)
            
            msg = (
                f"📝 <b>Paso 2:</b> Ahora calcula el resultado.<br/><br/>"
                f"💡 <b>Operación:</b> {operacion} <b>{_format_number(value)}</b> por <b>{_format_number(factor)}</b><br/><br/>"
                f"✏️ ¿Cuántos <b>{to_unit}</b> son <b>{_format_number(value)} {from_unit}</b>?"
            )
            
            return {
                "status": "ask",
                "message": msg,
                "expected_answer": _format_number(result),
                "topic": "medidas",
                "hint_type": "meas_calc",
                "next_step": 2
            }
        
        # Validar respuesta del usuario
        try:
            user_value = float(_canon(answer))
            expected_value = result
            
            # Tolerancia de 0.1 para redondeos
            if abs(user_value - expected_value) < 0.1:
                return {
                    "status": "done",
                    "message": (
                        f"🎉 ¡Perfecto! <b>{_format_number(value)} {from_unit}</b> = <b>{_format_number(result)} {to_unit}</b>.<br/><br/>"
                        f"✅ Has realizado correctamente la conversión de unidades. ¡Muy buen trabajo! 🌟<br/><br/>"
                        f"📚 <b>Resumen:</b><br/>"
                        f"• Factor: {_format_number(factor)}<br/>"
                        f"• Operación: {_format_number(value)} × {_format_number(factor)} = {_format_number(result)}"
                    ),
                    "expected_answer": _format_number(result),
                    "topic": "medidas",
                    "hint_type": "meas_result",
                    "next_step": 2
                }
            else:
                return {
                    "status": "feedback",
                    "message": (
                        f"❌ No es correcto.<br/><br/>"
                        f"💡 Recuerda: {_format_number(value)} × {_format_number(factor)}"
                    ),
                    "expected_answer": _format_number(result),
                    "topic": "medidas",
                    "hint_type": "meas_calc",
                    "next_step": 1
                }
        
        except ValueError:
            return {
                "status": "feedback",
                "message": "❌ Eso no es un número válido. Intenta de nuevo.",
                "expected_answer": _format_number(result),
                "topic": "medidas",
                "hint_type": "meas_calc",
                "next_step": 1
            }
    
    # ──────────────────────────────────────────────────────────
    # PASO 2: Ejercicio completado
    # ──────────────────────────────────────────────────────────
    else:
        return {
            "status": "done",
            "message": (
                f"✅ ¡Ejercicio completado!<br/><br/>"
                f"Has aprendido a convertir <b>{from_unit}</b> a <b>{to_unit}</b>. 🎉"
            ),
            "expected_answer": _format_number(result),
            "topic": "medidas",
            "hint_type": "meas_complete",
            "next_step": 3
        }