# -*- coding: utf-8 -*-
"""
decimals_engine.py
Motor para operaciones con números decimales.
✅ VERSIÓN CORREGIDA:
- SUMA y RESTA: Ahora se hacen DIRECTAMENTE sin quitar la coma
- DIVISIÓN: Corregido el cálculo de conversión para no perder decimales
- MULTIPLICACIÓN: Mantiene método correcto (convertir a enteros)
"""

import re
from typing import Dict, Any, Optional, Tuple

# ══════════════════════════════════════════════════════════════
# FUNCIONES AUXILIARES
# ══════════════════════════════════════════════════════════════

def _canon(s: str) -> str:
    """Normaliza texto para comparación."""
    return str(s or "").strip().lower().replace(",", ".")

def _extract_operation(expr: str) -> Optional[Tuple[float, str, float]]:
    """
    Extrae números decimales y operador de una expresión.
    Retorna: (a, operador, b) o None si no es válida
    """
    expr = expr.replace(",", ".")
    m = re.search(r"(\d+(?:\.\d+)?)\s*([+\-×x*/÷:])\s*(\d+(?:\.\d+)?)", expr)
    if not m:
        return None
    
    a_str, op, b_str = m.groups()
    a, b = float(a_str), float(b_str)
    
    # Normalizar operador
    if op in ("x", "×", "*"):
        op = "×"
    elif op in ("/", ":", "÷"):
        op = "÷"
    
    return a, op, b

def _count_decimals(num: float) -> int:
    """Cuenta las cifras decimales de un número."""
    s = str(num).rstrip('0').rstrip('.')
    return len(s.split('.')[-1]) if '.' in s else 0

def _to_integer(num: float) -> int:
    """Convierte un decimal a entero eliminando la coma."""
    decimals = _count_decimals(num)
    return int(round(num * (10 ** decimals)))

def _format_number(num: float) -> str:
    """Formatea un número eliminando ceros innecesarios."""
    return f"{num:g}"

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
    Maneja operaciones con decimales paso a paso.
    
    Flujos diferentes según operación:
    - SUMA/RESTA: Operación directa (sin quitar coma)
    - MULTIPLICACIÓN: Convertir a enteros, operar, colocar coma
    - DIVISIÓN: Ajustar por decimales del divisor
    """
    
    # ──────────────────────────────────────────────────────────
    # VALIDAR Y EXTRAER OPERACIÓN
    # ──────────────────────────────────────────────────────────
    parsed = _extract_operation(prompt)
    if not parsed:
        return {
            "status": "ask",
            "message": (
                "📝 Necesito una operación con números decimales.<br/><br/>"
                "💡 <b>Ejemplos válidos:</b><br/>"
                "• <code>0.254 × 0.2</code><br/>"
                "• <code>3.2 + 1.45</code><br/>"
                "• <code>5.6 - 2.34</code><br/>"
                "• <code>8.4 ÷ 2.1</code>"
            ),
            "expected_answer": None,
            "topic": "decimales",
            "hint_type": "decimal_error",
            "next_step": 0
        }
    
    a, op, b = parsed
    
    # ──────────────────────────────────────────────────────────
    # SELECCIONAR FLUJO SEGÚN OPERACIÓN
    # ──────────────────────────────────────────────────────────
    if op in ("+", "-"):
        return _handle_addition_subtraction(a, op, b, step, answer, cycle)
    elif op == "×":
        return _handle_multiplication(a, b, step, answer, cycle)
    elif op == "÷":
        return _handle_division(a, b, step, answer, cycle)
    
    return {
        "status": "done",
        "message": "❌ Operación no reconocida.",
        "expected_answer": None,
        "topic": "decimales",
        "hint_type": "decimal_error",
        "next_step": 3
    }


# ══════════════════════════════════════════════════════════════
# ✅ SUMA Y RESTA (MÉTODO CORRECTO: SIN QUITAR LA COMA)
# ══════════════════════════════════════════════════════════════

def _handle_addition_subtraction(
    a: float, 
    op: str, 
    b: float, 
    step: int, 
    answer: str, 
    cycle: str
) -> Dict[str, Any]:
    """
    Maneja suma y resta CON la coma (método escolar correcto).
    NO se convierten a enteros - se alinean las comas y se opera.
    """
    
    op_name = "suma" if op == "+" else "resta"
    op_symbol = "+" if op == "+" else "−"
    
    # ─────────────────────────────────────────────────────────
    # PASO 0: Explicar método y pedir resultado directo
    # ─────────────────────────────────────────────────────────
    if step == 0:
        # Calcular resultado correcto
        result = a + b if op == "+" else a - b
        
        msg = (
            f"✨ Vamos a hacer una <b>{op_name} con decimales</b>: <b>{_format_number(a)} {op_symbol} {_format_number(b)}</b><br/><br/>"
            f"📝 <b>Método escolar:</b><br/>"
            f"Alineamos las comas y sumamos/restamos como con números enteros.<br/><br/>"
            f"💡 <b>Así se ve:</b><br/>"
            f"<pre style='background: #e3f2fd; padding: 10px; border-radius: 5px; font-family: monospace;'>"
            f"  {_format_number(a):>6}\n"
            f"{op_symbol} {_format_number(b):>6}\n"
            f"--------\n"
            f"  ?\n"
            f"</pre><br/>"
            f"✏️ Escribe el resultado de <b>{_format_number(a)} {op_symbol} {_format_number(b)}</b>"
        )
        
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": str(_format_number(result)),
            "topic": "decimales",
            "hint_type": f"decimal_{op_name}",
            "next_step": 1
        }
    
    # ─────────────────────────────────────────────────────────
    # PASO 1: Validar y terminar
    # ─────────────────────────────────────────────────────────
    else:
        result = a + b if op == "+" else a - b
        
        return {
            "status": "done",
            "message": (
                f"🎉 ¡Perfecto! El resultado de <b>{_format_number(a)} {op_symbol} {_format_number(b)}</b> es <b>{_format_number(result)}</b>.<br/><br/>"
                f"✅ Has completado la {op_name} con decimales correctamente. ¡Muy bien! 🌟<br/><br/>"
                f"📚 <b>Recuerda:</b> En suma y resta con decimales, <u>NO quitamos la coma</u>. Solo la alineamos y operamos."
            ),
            "expected_answer": str(_format_number(result)),
            "topic": "decimales",
            "hint_type": "decimal_result",
            "next_step": 2
        }


# ══════════════════════════════════════════════════════════════
# ✅ MULTIPLICACIÓN (MANTENER MÉTODO ACTUAL: CONVERTIR A ENTEROS)
# ══════════════════════════════════════════════════════════════

def _handle_multiplication(
    a: float, 
    b: float, 
    step: int, 
    answer: str, 
    cycle: str
) -> Dict[str, Any]:
    """
    Maneja multiplicación con decimales (método escolar correcto).
    1. Convertir ambos a enteros
    2. Multiplicar
    3. Colocar coma sumando decimales
    """
    
    decimals_a = _count_decimals(a)
    decimals_b = _count_decimals(b)
    int_a = _to_integer(a)
    int_b = _to_integer(b)
    
    # ─────────────────────────────────────────────────────────
    # PASO 0: Convertir ambos decimales a enteros
    # ─────────────────────────────────────────────────────────
    if step == 0:
        msg = (
            f"✨ Vamos a hacer una <b>multiplicación con decimales</b>: <b>{_format_number(a)} × {_format_number(b)}</b><br/><br/>"
            f"📝 <b>Paso 1:</b> Convierte ambos números a enteros eliminando las comas.<br/><br/>"
            f"💡 <b>¿Cómo se hace?</b><br/>"
            f"Mueve la coma hacia la derecha hasta que desaparezca.<br/><br/>"
            f"🔹 Ejemplo: <b>2.5</b> → mueves 1 posición → <b>25</b><br/>"
            f"🔹 Ejemplo: <b>0.34</b> → mueves 2 posiciones → <b>34</b><br/><br/>"
            f"✏️ Convierte <b>{_format_number(a)}</b> y <b>{_format_number(b)}</b><br/>"
            f"Escribe los dos números sin coma, separados por un espacio."
        )
        
        expected = f"{int_a} {int_b}"
        
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": expected,
            "topic": "decimales",
            "hint_type": "decimal_convert",
            "next_step": 1
        }
    
    # ─────────────────────────────────────────────────────────
    # PASO 1: Multiplicar los enteros
    # ─────────────────────────────────────────────────────────
    elif step == 1:
        int_result = int_a * int_b
        
        msg = (
            f"✅ ¡Excelente! Ahora tienes <b>{int_a}</b> y <b>{int_b}</b> sin comas.<br/><br/>"
            f"📝 <b>Paso 2:</b> Multiplica: <b>{int_a} × {int_b}</b><br/><br/>"
            f"💡 Puedes usar papel y lápiz si lo necesitas.<br/>"
            f"Escribe el resultado."
        )
        
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": str(int_result),
            "topic": "decimales",
            "hint_type": "decimal_multiplicacion",
            "next_step": 2
        }
    
    # ─────────────────────────────────────────────────────────
    # PASO 2: Colocar coma en el resultado
    # ─────────────────────────────────────────────────────────
    elif step == 2:
        int_result = int_a * int_b
        final_result = a * b
        total_decimals = decimals_a + decimals_b
        
        msg = (
            f"✅ ¡Muy bien! La multiplicación de <b>{int_a} × {int_b}</b> es <b>{int_result}</b>.<br/><br/>"
            f"📝 <b>Paso 3:</b> Ahora coloca la coma en el lugar correcto.<br/><br/>"
            f"💡 <b>Regla clave:</b><br/>"
            f"• <b>{_format_number(a)}</b> tiene <b>{decimals_a}</b> cifra(s) decimal(es)<br/>"
            f"• <b>{_format_number(b)}</b> tiene <b>{decimals_b}</b> cifra(s) decimal(es)<br/>"
            f"• Total: {decimals_a} + {decimals_b} = <b>{total_decimals}</b> decimales<br/><br/>"
            f"✏️ Toma <b>{int_result}</b> y coloca la coma contando <b>{total_decimals} posiciones desde la derecha</b>.<br/>"
            f"Escribe el resultado final con la coma."
        )
        
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": str(_format_number(final_result)),
            "topic": "decimales",
            "hint_type": "decimal_final",
            "next_step": 3
        }
    
    # ─────────────────────────────────────────────────────────
    # PASO 3: Terminar
    # ─────────────────────────────────────────────────────────
    else:
        final_result = a * b
        
        return {
            "status": "done",
            "message": (
                f"🎉 ¡Perfecto! El resultado de <b>{_format_number(a)} × {_format_number(b)}</b> es <b>{_format_number(final_result)}</b>.<br/><br/>"
                f"✅ Has completado la multiplicación con decimales correctamente. ¡Muy buen trabajo! 🌟<br/><br/>"
                f"📚 <b>Recuerda los pasos:</b><br/>"
                f"1️⃣ Convertir decimales a enteros<br/>"
                f"2️⃣ Multiplicar<br/>"
                f"3️⃣ Colocar la coma sumando las cifras decimales"
            ),
            "expected_answer": str(_format_number(final_result)),
            "topic": "decimales",
            "hint_type": "decimal_result",
            "next_step": 4
        }


# ══════════════════════════════════════════════════════════════
# ✅ DIVISIÓN (CORREGIDO: NO PIERDE DECIMALES)
# ══════════════════════════════════════════════════════════════

def _handle_division(
    a: float, 
    b: float, 
    step: int, 
    answer: str, 
    cycle: str
) -> Dict[str, Any]:
    """
    Maneja división con decimales (método escolar correcto).
    Solo mueve la coma del divisor y ajusta el dividendo.
    """
    
    decimals_b = _count_decimals(b)
    
    # ─────────────────────────────────────────────────────────
    # PASO 0: Contar decimales del divisor
    # ─────────────────────────────────────────────────────────
    if step == 0:
        msg = (
            f"✨ Vamos a dividir <b>{_format_number(a)} ÷ {_format_number(b)}</b><br/><br/>"
            f"📝 <b>Paso 1:</b> Para dividir con decimales, primero mira el <b>divisor</b> (el número que divide).<br/><br/>"
            f"💡 <b>Regla clave:</b><br/>"
            f"Debemos <b>eliminar la coma del divisor</b> y mover la coma del dividendo la misma cantidad de posiciones.<br/><br/>"
            f"❓ ¿Cuántas cifras decimales (cifras después de la coma) tiene el divisor <b>{_format_number(b)}</b>?"
        )
        
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": str(decimals_b),
            "topic": "decimales",
            "hint_type": "decimal_div_count",
            "next_step": 1
        }
    
    # ─────────────────────────────────────────────────────────
    # PASO 1: Calcular dividendo y divisor ajustados
    # ─────────────────────────────────────────────────────────
    elif step == 1:
        # ✅ CORREGIDO: Mover la coma manteniendo decimales restantes
        # Ejemplo: 0.231 con 3 decimales, mover 1 posición → 2.31 (2 decimales)
        new_dividend = a * (10 ** decimals_b)
        new_divisor = b * (10 ** decimals_b)
        
        # Formatear para mostrar correctamente
        new_dividend_str = _format_number(new_dividend)
        new_divisor_str = _format_number(new_divisor)
        
        msg = (
            f"✅ ¡Correcto! El divisor tiene <b>{decimals_b}</b> cifra(s) decimal(es).<br/><br/>"
            f"📝 <b>Paso 2:</b> Al mover la coma <b>{decimals_b}</b> posición(es):<br/>"
            f"• Dividendo: <b>{_format_number(a)}</b> → <b>{new_dividend_str}</b><br/>"
            f"• Divisor: <b>{_format_number(b)}</b> → <b>{new_divisor_str}</b><br/><br/>"
            f"✏️ Ahora divide: <b>{new_dividend_str} ÷ {new_divisor_str}</b><br/>"
            f"Escribe el resultado (puede ser un número con decimales)."
        )
        
        # Calcular resultado esperado
        if b == 0:
            expected_result = 0
        else:
            expected_result = a / b
        
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": str(_format_number(expected_result)),
            "topic": "decimales",
            "hint_type": "decimal_div_calculate",
            "next_step": 2
        }
    
    # ─────────────────────────────────────────────────────────
    # PASO 2: Validar resultado final
    # ─────────────────────────────────────────────────────────
    else:
        if b == 0:
            return {
                "status": "done",
                "message": "⚠️ No se puede dividir entre cero.",
                "expected_answer": None,
                "topic": "decimales",
                "hint_type": "decimal_error",
                "next_step": 3
            }
        
        final_result = a / b
        
        return {
            "status": "done",
            "message": (
                f"🎉 ¡Perfecto! El resultado de <b>{_format_number(a)} ÷ {_format_number(b)}</b> es <b>{_format_number(final_result)}</b>.<br/><br/>"
                f"✅ Has completado la división con decimales correctamente. ¡Muy bien! 🌟"
            ),
            "expected_answer": str(_format_number(final_result)),
            "topic": "decimales",
            "hint_type": "decimal_result",
            "next_step": 3
        }