# -*- coding: utf-8 -*-
"""
geometry_engine.py
Motor para cálculo de áreas y perímetros.
✅ VERSIÓN CORREGIDA:
- Ahora VALIDA las respuestas del usuario
- NO revela el resultado, pide al alumno que calcule
- Maneja errores correctamente
- Compatible con solve.py
"""

import re
import math
from typing import Dict, Any, Optional, Tuple, List

# ══════════════════════════════════════════════════════════════
# FUNCIONES AUXILIARES
# ══════════════════════════════════════════════════════════════

def _canon(s: str) -> str:
    """Normaliza texto para comparación."""
    return str(s or "").strip().lower().replace(" ", "").replace(",", ".").replace("×", "*").replace("x", "*")

def _parse_geometry(question: str) -> Optional[Tuple[str, str, List[float]]]:
    """
    Detecta figura geométrica, tipo de problema y valores.
    Retorna: (figura, tipo, [valores]) o None
    """
    q = question.lower().replace(",", ".")
    
    # Detectar figura
    fig = None
    if "cuadrado" in q:
        fig = "cuadrado"
    elif "rectángulo" in q or "rectangulo" in q:
        fig = "rectángulo"
    elif "triángulo" in q or "triangulo" in q:
        fig = "triángulo"
    elif "círculo" in q or "circulo" in q:
        fig = "círculo"
    
    if not fig:
        return None
    
    # Detectar magnitud
    tipo = "area"  # por defecto
    if "perímetro" in q or "perimetro" in q:
        tipo = "perimetro"
    elif "área" in q or "area" in q:
        tipo = "area"
    
    # Detectar valores numéricos
    m = re.findall(r"(\d+(?:\.\d+)?)", q)
    nums = [float(n) for n in m]
    
    return fig, tipo, nums

def _formula(fig: str, tipo: str) -> Optional[str]:
    """Retorna la fórmula para una figura y tipo de cálculo."""
    formulas = {
        ("cuadrado", "perimetro"): "4 × lado",
        ("cuadrado", "area"): "lado × lado",
        ("rectángulo", "perimetro"): "2 × (base + altura)",
        ("rectángulo", "area"): "base × altura",
        ("triángulo", "area"): "(base × altura) ÷ 2",
        ("círculo", "area"): "π × radio²",
        ("círculo", "perimetro"): "2 × π × radio",
    }
    return formulas.get((fig, tipo))

def _calculate(fig: str, tipo: str, nums: List[float]) -> Optional[float]:
    """Calcula área o perímetro según figura y valores."""
    try:
        if fig == "cuadrado":
            if tipo == "perimetro":
                return 4 * nums[0]
            else:  # area
                return nums[0] ** 2
        
        elif fig == "rectángulo":
            if len(nums) < 2:
                return None
            if tipo == "perimetro":
                return 2 * (nums[0] + nums[1])
            else:  # area
                return nums[0] * nums[1]
        
        elif fig == "triángulo":
            if len(nums) < 2:
                return None
            # Solo área (perímetro de triángulo requiere los 3 lados)
            if tipo == "area":
                return (nums[0] * nums[1]) / 2
            return None
        
        elif fig == "círculo":
            if tipo == "area":
                return math.pi * (nums[0] ** 2)
            else:  # perimetro
                return 2 * math.pi * nums[0]
        
    except (IndexError, ValueError):
        return None
    
    return None

def _format_number(num: float) -> str:
    """Formatea un número eliminando ceros innecesarios."""
    if num == int(num):
        return str(int(num))
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
    Maneja cálculo de áreas y perímetros paso a paso.
    
    Pasos:
    - 0: Identificar fórmula
    - 1: Sustituir valores
    - 2: Calcular resultado
    - 3: Done
    """
    
    # ──────────────────────────────────────────────────────────
    # VALIDAR Y EXTRAER PROBLEMA
    # ──────────────────────────────────────────────────────────
    parsed = _parse_geometry(prompt)
    if not parsed:
        return {
            "status": "ask",
            "message": (
                "📝 Necesito un problema de geometría.<br/><br/>"
                "💡 <b>Ejemplos válidos:</b><br/>"
                "• <code>Área de un cuadrado de lado 5</code><br/>"
                "• <code>Perímetro de un rectángulo de base 8 y altura 3</code><br/>"
                "• <code>Área de un triángulo de base 10 y altura 6</code><br/>"
                "• <code>Perímetro de un círculo de radio 4</code>"
            ),
            "expected_answer": None,
            "topic": "geometria",
            "hint_type": "geo_error",
            "next_step": 0
        }
    
    fig, tipo, nums = parsed
    formula = _formula(fig, tipo)
    
    if not formula:
        return {
            "status": "ask",
            "message": f"❌ No puedo calcular el {tipo} de un {fig} con estos datos.",
            "expected_answer": None,
            "topic": "geometria",
            "hint_type": "geo_error",
            "next_step": 0
        }
    
    # Validar que haya suficientes números
    required_nums = 2 if fig in ("rectángulo", "triángulo") else 1
    if len(nums) < required_nums:
        return {
            "status": "ask",
            "message": f"❌ Necesito más datos. Para un {fig} necesito {required_nums} valor(es).",
            "expected_answer": None,
            "topic": "geometria",
            "hint_type": "geo_error",
            "next_step": 0
        }
    
    tipo_nombre = "área" if tipo == "area" else "perímetro"
    
    # ──────────────────────────────────────────────────────────
    # PASO 0: Identificar fórmula
    # ──────────────────────────────────────────────────────────
    if step == 0:
        # Si no hay respuesta todavía, hacer la pregunta
        if _canon(answer) == "":
            msg = (
                f"✨ Vamos a calcular el <b>{tipo_nombre}</b> de un <b>{fig}</b>.<br/><br/>"
                f"📝 <b>Paso 1:</b> Primero necesitamos la fórmula correcta.<br/><br/>"
                f"💡 <b>Recuerda las fórmulas:</b><br/>"
            )
            
            if fig == "cuadrado":
                msg += (
                    "• Área de cuadrado: <b>lado × lado</b><br/>"
                    "• Perímetro de cuadrado: <b>4 × lado</b>"
                )
            elif fig == "rectángulo":
                msg += (
                    "• Área de rectángulo: <b>base × altura</b><br/>"
                    "• Perímetro de rectángulo: <b>2 × (base + altura)</b>"
                )
            elif fig == "triángulo":
                msg += "• Área de triángulo: <b>(base × altura) ÷ 2</b>"
            elif fig == "círculo":
                msg += (
                    "• Área de círculo: <b>π × radio²</b><br/>"
                    "• Perímetro de círculo: <b>2 × π × radio</b>"
                )
            
            msg += f"<br/><br/>✏️ Escribe la fórmula para el <b>{tipo_nombre} del {fig}</b>"
            
            return {
                "status": "ask",
                "message": msg,
                "expected_answer": formula,
                "topic": "geometria",
                "hint_type": "geo_formula",
                "next_step": 1
            }
        
        # Validar respuesta del usuario
        user_answer = _canon(answer)
        expected_answer = _canon(formula)
        
        # Comparación flexible (permitir variaciones en formato)
        if user_answer == expected_answer or user_answer.replace("(", "").replace(")", "") == expected_answer.replace("(", "").replace(")", ""):
            return {
                "status": "ask",
                "message": "✅ ¡Correcto! Ahora vamos a sustituir los valores.",
                "expected_answer": formula,
                "topic": "geometria",
                "hint_type": "geo_formula",
                "next_step": 1
            }
        else:
            return {
                "status": "feedback",
                "message": f"❌ No es exactamente. La fórmula correcta es: <b>{formula}</b>",
                "expected_answer": formula,
                "topic": "geometria",
                "hint_type": "geo_formula",
                "next_step": 0
            }
    
    # ──────────────────────────────────────────────────────────
    # PASO 1: Sustituir valores en la fórmula
    # ──────────────────────────────────────────────────────────
    elif step == 1:
        # Preparar fórmula con valores sustituidos
        formula_filled = formula
        
        if fig == "cuadrado":
            formula_filled = formula.replace("lado", str(int(nums[0]) if nums[0] == int(nums[0]) else nums[0]))
        elif fig == "rectángulo":
            base_str = str(int(nums[0]) if nums[0] == int(nums[0]) else nums[0])
            altura_str = str(int(nums[1]) if nums[1] == int(nums[1]) else nums[1])
            formula_filled = formula.replace("base", base_str).replace("altura", altura_str)
        elif fig == "triángulo":
            base_str = str(int(nums[0]) if nums[0] == int(nums[0]) else nums[0])
            altura_str = str(int(nums[1]) if nums[1] == int(nums[1]) else nums[1])
            formula_filled = formula.replace("base", base_str).replace("altura", altura_str)
        elif fig == "círculo":
            radio_str = str(int(nums[0]) if nums[0] == int(nums[0]) else nums[0])
            formula_filled = formula.replace("radio", radio_str)
        
        # Si no hay respuesta todavía, hacer la pregunta
        if _canon(answer) == "":
            msg = (
                f"📝 <b>Paso 2:</b> Sustituye los valores en la fórmula.<br/><br/>"
                f"💡 <b>Fórmula:</b> {formula}<br/>"
            )
            
            if fig == "cuadrado":
                msg += f"<b>Lado:</b> {_format_number(nums[0])}"
            elif fig in ("rectángulo", "triángulo"):
                msg += f"<b>Base:</b> {_format_number(nums[0])}<br/><b>Altura:</b> {_format_number(nums[1])}"
            elif fig == "círculo":
                msg += f"<b>Radio:</b> {_format_number(nums[0])}"
            
            msg += f"<br/><br/>✏️ Escribe la fórmula con los valores sustituidos (ejemplo: <code>5 × 5</code>)"
            
            return {
                "status": "ask",
                "message": msg,
                "expected_answer": formula_filled,
                "topic": "geometria",
                "hint_type": "geo_substitute",
                "next_step": 2
            }
        
        # Validar respuesta del usuario
        user_answer = _canon(answer)
        expected_answer = _canon(formula_filled)
        
        # Comparación flexible
        if user_answer == expected_answer or user_answer.replace("(", "").replace(")", "") == expected_answer.replace("(", "").replace(")", ""):
            return {
                "status": "ask",
                "message": "✅ ¡Perfecto! Ahora vamos a calcular el resultado.",
                "expected_answer": formula_filled,
                "topic": "geometria",
                "hint_type": "geo_substitute",
                "next_step": 2
            }
        else:
            return {
                "status": "feedback",
                "message": f"❌ No es exactamente. Debería ser: <b>{formula_filled}</b>",
                "expected_answer": formula_filled,
                "topic": "geometria",
                "hint_type": "geo_substitute",
                "next_step": 1
            }
    
    # ──────────────────────────────────────────────────────────
    # PASO 2: Calcular el resultado
    # ──────────────────────────────────────────────────────────
    elif step == 2:
        result = _calculate(fig, tipo, nums)
        
        if result is None:
            return {
                "status": "ask",
                "message": "❌ No pude calcular el resultado con estos valores.",
                "expected_answer": None,
                "topic": "geometria",
                "hint_type": "geo_error",
                "next_step": 2
            }
        
        # Si no hay respuesta todavía, hacer la pregunta
        if _canon(answer) == "":
            # Preparar expresión para mostrar
            if fig == "cuadrado":
                if tipo == "perimetro":
                    expr = f"4 × {_format_number(nums[0])}"
                else:
                    expr = f"{_format_number(nums[0])} × {_format_number(nums[0])}"
            elif fig == "rectángulo":
                if tipo == "perimetro":
                    expr = f"2 × ({_format_number(nums[0])} + {_format_number(nums[1])})"
                else:
                    expr = f"{_format_number(nums[0])} × {_format_number(nums[1])}"
            elif fig == "triángulo":
                expr = f"({_format_number(nums[0])} × {_format_number(nums[1])}) ÷ 2"
            elif fig == "círculo":
                if tipo == "area":
                    expr = f"π × {_format_number(nums[0])}²"
                else:
                    expr = f"2 × π × {_format_number(nums[0])}"
            else:
                expr = "cálculo"
            
            msg = (
                f"📝 <b>Paso 3:</b> Ahora calcula el resultado numérico.<br/><br/>"
                f"💡 <b>Operación:</b> {expr}<br/><br/>"
                f"✏️ ¿Cuál es el resultado? (puedes redondear a 2 decimales)"
            )
            
            return {
                "status": "ask",
                "message": msg,
                "expected_answer": _format_number(result),
                "topic": "geometria",
                "hint_type": "geo_calc",
                "next_step": 3
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
                        f"🎉 ¡Excelente! El <b>{tipo_nombre}</b> del <b>{fig}</b> es <b>{_format_number(result)}</b>.<br/><br/>"
                        f"✅ Has resuelto correctamente el problema de geometría. ¡Muy buen trabajo! 🌟<br/><br/>"
                        f"📚 <b>Resumen:</b><br/>"
                        f"• Fórmula: {formula}<br/>"
                        f"• Resultado: {_format_number(result)} unidades{'²' if tipo == 'area' else ''}"
                    ),
                    "expected_answer": _format_number(result),
                    "topic": "geometria",
                    "hint_type": "geo_result",
                    "next_step": 3
                }
            else:
                return {
                    "status": "feedback",
                    "message": (
                        f"❌ No es correcto.<br/><br/>"
                        f"💡 Revisa el cálculo paso a paso. El resultado debería estar cerca de {_format_number(result)}."
                    ),
                    "expected_answer": _format_number(result),
                    "topic": "geometria",
                    "hint_type": "geo_calc",
                    "next_step": 2
                }
        
        except ValueError:
            return {
                "status": "feedback",
                "message": "❌ Eso no es un número válido. Intenta de nuevo.",
                "expected_answer": _format_number(result),
                "topic": "geometria",
                "hint_type": "geo_calc",
                "next_step": 2
            }
    
    # ──────────────────────────────────────────────────────────
    # PASO 3: Ejercicio completado
    # ──────────────────────────────────────────────────────────
    else:
        result = _calculate(fig, tipo, nums)
        return {
            "status": "done",
            "message": (
                f"✅ ¡Ejercicio completado!<br/><br/>"
                f"Has aprendido a calcular el <b>{tipo_nombre} de un {fig}</b>. 🎉"
            ),
            "expected_answer": _format_number(result) if result else None,
            "topic": "geometria",
            "hint_type": "geo_complete",
            "next_step": 4
        }