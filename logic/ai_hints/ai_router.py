# -*- coding: utf-8 -*-
"""
ai_router.py
Sistema de pistas para Tutorín:
- Usa pistas internas por tipo de operación (suma, fracción, decimales, etc.)
- Si no hay pista definida, genera una con IA.
✅ VERSIÓN CORREGIDA: Con nombres de módulos correctos
"""

import re
import os
from importlib import import_module

# === Importar validador de hint_types ===
from logic.core.hint_validator import is_valid_hint

# === Importar funciones públicas de pistas ===
# ✅ CORREGIDO: Nombres correctos en inglés
try:
    from .hints_addition import get_hint as get_addition_hint
except ImportError:
    get_addition_hint = None

try:
    from .hints_subtraction import get_hint as get_subtraction_hint
except ImportError:
    get_subtraction_hint = None

try:
    from .hints_multiplication import get_hint as get_multiplication_hint
except ImportError:
    get_multiplication_hint = None

try:
    from .hints_division import get_hint as get_division_hint
except ImportError:
    get_division_hint = None

try:
    from .hints_fractions import (
        _frac_inicio_hint,
        _frac_mcm_hint,
        _frac_equiv_hint,
        _frac_operacion_hint,
        _frac_simplificar_hint,
        get_hint as get_fractions_hint
    )
except ImportError:
    _frac_inicio_hint = None
    _frac_mcm_hint = None
    _frac_equiv_hint = None
    _frac_operacion_hint = None
    _frac_simplificar_hint = None
    get_fractions_hint = None

try:
    from .hints_decimals import get_hint as get_decimals_hint
except ImportError:
    get_decimals_hint = None

try:
    from .hints_geometry import get_hint as get_geometry_hint
except ImportError:
    get_geometry_hint = None

try:
    from .hints_measures import get_hint as get_measures_hint
except ImportError:
    get_measures_hint = None

try:
    from .hints_percentages import get_hint as get_percentages_hint
except ImportError:
    get_percentages_hint = None

try:
    from .hints_statistics import get_hint as get_statistics_hint
except ImportError:
    get_statistics_hint = None

try:
    from .hints_reading import get_hint as get_reading_hint
except ImportError:
    get_reading_hint = None

# === IA opcional ===
try:
    from openai import OpenAI
    _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    _USE_AI = bool(os.getenv("OPENAI_API_KEY"))
except Exception:
    _client = None
    _USE_AI = False


# === Función auxiliar para fracciones ===
def _ensure_frac_marker(ctx: str) -> str:
    """Reconstruye el marcador oculto de fracciones si falta."""
    text = ctx or ""
    if "[FRAC:" in text:
        return text

    m = re.search(r"(\d+)\s*/\s*(\d+)\s*([+\-])\s*(\d+)\s*/\s*(\d+)", text)
    if m:
        a, b, op, c, d = m.groups()
        return text + f"<span style='display:none'>[FRAC:{a}/{b}{op}{c}/{d}]</span>"
    return text


# === IA: generación de pista cuando no hay módulo ===
def _generate_ai_hint(prompt: str, step: str, error_count: int, context: str = "") -> str:
    """Genera una pista usando IA si no existe pista interna."""
    if not _USE_AI or not _client:
        return "Pista: piensa paso a paso, revisa el número y vuelve a intentarlo."

    try:
        sys_msg = (
            "Eres Tutorín, un profesor de Primaria en España. "
            "Da una pista breve, concreta y motivadora para ayudar al alumno "
            "a avanzar en su razonamiento sin resolverle todo."
        )
        user_msg = f"Consigna: {prompt}\nPaso: {step}\nErrores: {error_count}\nContexto: {context}"
        chat = _client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.5,
        )
        return chat.choices[0].message.content.strip()
    except Exception as e:
        print(f"[AI_ROUTER] Error generando pista IA: {e}")
        return "No tengo una pista clara ahora mismo, intenta explicar cómo lo estás haciendo."


# === Generador principal de pistas ===
def generate_hint_with_ai(
    topic: str,
    step: str,
    question_or_context: str,
    answer: str = "",
    error_count: int = 1,
    cycle: str = "c2"
) -> str:
    """
    Genera una pista según el tema y el paso del ejercicio.
    - Usa pistas internas si existen.
    - Si no, intenta cargar el módulo hints_<topic>.
    - Si tampoco existe, usa IA como último recurso.
    """
    t = (topic or "").lower().strip()
    c = cycle or "c2"
    ctx = question_or_context or ""

    # Validar número de errores
    try:
        e = int(error_count)
    except Exception:
        e = 1
    e = max(1, min(e, 9))

    # --- Suma --- ✅ ACEPTA TEMA EN ESPAÑOL O INGLÉS
    if t in ("suma", "addition") and get_addition_hint:
        actual_step = step or "add_col"
        hint = get_addition_hint(actual_step, e, ctx, answer)
        _validate_hint_type("suma", actual_step)
        return hint

    # --- Resta --- ✅ ACEPTA TEMA EN ESPAÑOL O INGLÉS
    if t in ("resta", "subtraction") and get_subtraction_hint:
        actual_step = step or "sub_col"
        hint = get_subtraction_hint(actual_step, e, ctx, answer)
        _validate_hint_type("resta", actual_step)
        return hint

    # --- Multiplicación --- ✅ ACEPTA TEMA EN ESPAÑOL O INGLÉS
    if t in ("multiplicacion", "multiplication") and get_multiplication_hint:
        actual_step = step or "mult_parcial"
        hint = get_multiplication_hint(actual_step, e, ctx, answer)
        _validate_hint_type("multiplicacion", actual_step)
        return hint

    # --- División --- ✅ ACEPTA TEMA EN ESPAÑOL O INGLÉS
    if t in ("division",) and get_division_hint:
        actual_step = step or "div_qdigit"
        hint = get_division_hint(actual_step, e, ctx, answer)
        _validate_hint_type("division", actual_step)
        return hint

    # --- Fracciones --- ✅ ACEPTA TEMA EN ESPAÑOL O INGLÉS
    if t in ("fracciones", "fractions"):
        ctx = _ensure_frac_marker(ctx)
        if step == "frac_inicio" and _frac_inicio_hint:
            _validate_hint_type("fracciones", step)
            return _frac_inicio_hint(ctx, e, c)
        if step == "frac_mcm" and _frac_mcm_hint:
            _validate_hint_type("fracciones", step)
            return _frac_mcm_hint(ctx, e, c)
        if step == "frac_equiv" and _frac_equiv_hint:
            _validate_hint_type("fracciones", step)
            return _frac_equiv_hint(ctx, e, c)
        if step == "frac_operacion" and _frac_operacion_hint:
            _validate_hint_type("fracciones", step)
            return _frac_operacion_hint(ctx, e, c)
        if step == "frac_simplificar" and _frac_simplificar_hint:
            _validate_hint_type("fracciones", step)
            return _frac_simplificar_hint(ctx, e, c)

    # --- Decimales --- ✅ CORREGIDO: Ahora pasa los 4 parámetros
    if t in ("decimales", "decimals") and get_decimals_hint:
        hint = get_decimals_hint(step, e, ctx, answer)
        _validate_hint_type("decimales", step)
        return hint

    # --- Geometría --- ✅ CORREGIDO: Ahora pasa los 4 parámetros
    if t in ("geometria", "geometry") and get_geometry_hint:
        hint = get_geometry_hint(step, e, ctx, answer)
        _validate_hint_type("geometria", step)
        return hint

    # --- Medidas --- ✅ CORREGIDO: Ahora pasa los 4 parámetros
    if t in ("medidas", "measures") and get_measures_hint:
        hint = get_measures_hint(step, e, ctx, answer)
        _validate_hint_type("medidas", step)
        return hint

    # --- Porcentajes --- ✅ CORREGIDO: Ahora pasa los 4 parámetros
    if t in ("porcentajes", "percentages") and get_percentages_hint:
        hint = get_percentages_hint(step, e, ctx, answer)
        _validate_hint_type("porcentajes", step)
        return hint

    # --- Estadística --- ✅ CORREGIDO: Ahora pasa los 4 parámetros
    if t in ("estadistica", "probabilidad", "statistics", "probability"):
        if get_statistics_hint:
            hint = get_statistics_hint(step, e, ctx, answer)
            _validate_hint_type("estadistica", step)
            return hint

    # --- Lectura / Reading --- ✅ NUEVO: Soporte para comprensión lectora
    if t in ("lectura", "reading", "comprension", "comprehension") and get_reading_hint:
        hint = get_reading_hint(step, e, ctx, answer)
        _validate_hint_type("lectura", step)
        return hint

    # --- Carga dinámica genérica ---
    try:
        # Intentar con nombre en inglés primero
        hints_module = import_module(f"logic.ai_hints.hints_{t}")
        if hasattr(hints_module, "get_hint"):
            hint = hints_module.get_hint(step, e, ctx, answer)
            _validate_hint_type(t, step)
            return hint
    except ModuleNotFoundError:
        pass
    except Exception as ex:
        print(f"[AI_ROUTER] Error importando hints dinámicos ({t}):", ex)

    # --- Último recurso: IA ---
    hint = _generate_ai_hint(topic, step, e, ctx)
    _validate_hint_type("general", "ai_generated")
    return hint


# === VALIDACIÓN SILENCIOSA DE hint_types ===
def _validate_hint_type(topic: str, hint_type: str) -> None:
    """
    Valida silenciosamente si un hint_type es válido según hint_types.json.
    No interrumpe la ejecución, solo muestra advertencias en consola.
    """
    if not is_valid_hint(topic, hint_type):
        print(f"[AI_ROUTER] ⚠️ Hint_type desconocido '{hint_type}' para tema '{topic}'.")