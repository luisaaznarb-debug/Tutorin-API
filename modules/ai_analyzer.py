# -*- coding: utf-8 -*-
"""
ai_analyzer.py
--------------------------------------------------
Analiza lo que el niño escribe o dice y decide:
- subject (materia)
- intent (tipo de tarea)
- engine (motor a invocar)

NUEVA LÓGICA:
1. Detecta PRIMERO si es un problema de texto contextual
2. Si es problema → usa generic_engine con IA
3. Si no → aplica reglas matemáticas para operaciones puras
✅ CORREGIDO: Detecta decimales con multiplicación y división
"""

import json
import os
import re
from typing import Dict, Any

# === IMPORTAR EL NUEVO NÚCLEO ===
from logic.core.engine_loader import load_engine
from logic.core.engine_schema import validate_output

# === CARGA DE PALABRAS CLAVE ===
_BASE = os.path.dirname(os.path.abspath(__file__))
_LABELS_PATH = os.path.join(_BASE, "nlu_labels.json")


def _load_labels() -> Dict[str, Any]:
    """Carga las palabras clave desde nlu_labels.json"""
    try:
        with open(_LABELS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[AI_ANALYZER] ⚠️ No se pudo cargar nlu_labels.json: {e}")
        return {}


_LABELS = _load_labels()

# === PALABRAS QUE INDICAN PROBLEMA DE TEXTO ===
_PROBLEM_WORDS = [
    # Contexto de personas
    "tiene", "tenía", "compró", "compra", "vendió", "vende", "reparte", "da", "dan",
    "recibe", "recibió", "gana", "ganó", "pierde", "perdió", "queda", "quedan",
    
    # Contexto de objetos/situaciones
    "manzanas", "caramelos", "cromos", "euros", "kilos", "metros", "litros",
    "casa", "cajón", "tienda", "mercado", "clase", "colegio",
    
    # Personas/nombres
    "maría", "juan", "pedro", "laura", "cecilia", "danila", "luis", "ana",
    "niño", "niños", "alumno", "alumnos", "persona", "personas",
    
    # Preguntas típicas de problemas
    "cuánto", "cuántos", "cuántas", "total", "entre todos", "en total",
    "al cabo", "después", "antes", "ahora",
    
    # Verbos narrativos
    "había", "hay", "hubo", "fueron", "van", "vinieron", "llegaron",
    
    # Conectores narrativos
    "cada uno", "cada una", "entre", "juntos", "además", "también", "pero"
]

# === PATRONES MATEMÁTICOS PUROS (solo números y operadores) ===
# ⚠️ IMPORTANTE: El orden importa - reglas más específicas primero
_PURE_MATH_PATTERNS = [
    # 1️⃣ FRACCIONES (más específico)
    (r"^\s*\d+\s*/\s*\d+\s*[\+\-]\s*\d+\s*/\s*\d+\s*$", ("matematicas", "fracciones", "fractions_engine")),
    
    # 2️⃣ DECIMALES - TODAS LAS VARIANTES (deben ir ANTES de multiplicación/división/suma/resta)
    # Caso 1: Ambos números con decimales (0.234 + 0.5)
    (r"^\s*\d+[.,]\d+\s*([+\-×x*/÷:])\s*\d+[.,]\d+\s*$", ("matematicas", "decimales", "decimals_engine")),
    
    # Caso 2: Primer número decimal, segundo entero (0.234 * 2)
    (r"^\s*\d+[.,]\d+\s*([+\-×x*/÷:])\s*\d+\s*$", ("matematicas", "decimales", "decimals_engine")),
    
    # Caso 3: Primer número entero, segundo decimal (2 * 0.234)
    (r"^\s*\d+\s*([+\-×x*/÷:])\s*\d+[.,]\d+\s*$", ("matematicas", "decimales", "decimals_engine")),
    
    # 3️⃣ PORCENTAJES
    (r"^\s*\d+\s*%\s*(?:de\s*)?\d+\s*$", ("matematicas", "porcentajes", "percentages_engine")),
    
    # 4️⃣ OPERACIONES BÁSICAS (después de decimales)
    # División pura: 24 / 6
    (r"^\s*\d+\s*(?:÷|:|/)\s*\d+\s*$", ("matematicas", "division", "division_engine")),
    
    # Multiplicación pura: 5 × 3
    (r"^\s*\d+\s*(?:×|\*|x|X|·)\s*\d+\s*$", ("matematicas", "multiplicacion", "multiplication_engine")),
    
    # Suma pura: 25 + 37
    (r"^\s*\d+\s*\+\s*\d+\s*$", ("matematicas", "suma", "addition_engine")),
    
    # Resta pura: 45 - 18
    (r"^\s*\d+\s*\-\s*\d+\s*$", ("matematicas", "resta", "subtraction_engine")),
]


# ================================================================
# 🧠 FUNCIONES AUXILIARES
# ================================================================

def _is_text_problem(text: str) -> bool:
    """
    Detecta si el texto es un problema contextual (no una operación pura).
    
    Criterios:
    - Tiene más de 30 caracteres (problemas suelen ser largos)
    - Contiene al menos 2 palabras contextuales
    - O contiene pregunta típica (¿Cuánto...?)
    """
    text_lower = text.lower()
    
    # Criterio 1: Longitud
    if len(text) < 30:
        return False
    
    # Criterio 2: Palabras contextuales
    word_count = sum(1 for word in _PROBLEM_WORDS if word in text_lower)
    if word_count >= 2:
        return True
    
    # Criterio 3: Preguntas directas
    question_patterns = [
        r"¿\s*cuánto[s]?\s+",
        r"¿\s*cuánta[s]?\s+",
        r"cuánto[s]?\s+.*\?",
        r"cuánta[s]?\s+.*\?"
    ]
    if any(re.search(pattern, text_lower) for pattern in question_patterns):
        return True
    
    return False


def _is_pure_math_operation(text: str) -> bool:
    """
    Verifica si es una operación matemática PURA (solo números y operadores).
    Ejemplo: "25 + 37" → True
    Ejemplo: "Juan tiene 25 manzanas" → False
    """
    # Eliminar espacios y verificar longitud
    clean = text.strip()
    if len(clean) < 3:
        return False
    
    # Verificar patrones puros
    for pattern, _ in _PURE_MATH_PATTERNS:
        if re.match(pattern, clean):
            return True
    
    return False


# ================================================================
# 🧠 FUNCIÓN PRINCIPAL: ANALIZAR EL PROMPT
# ================================================================
def analyze_prompt(prompt: str) -> Dict[str, Any]:
    """
    Detecta la materia, el tipo de operación (intent) y el motor asociado.
    
    PRIORIDAD:
    1. Problemas de texto → generic_engine
    2. Operaciones matemáticas puras → motores específicos
    3. Palabras clave → motores por tema
    4. Fallback → generic_engine
    """
    text = (prompt or "").strip()
    if not text:
        return {"subject": "general", "intent": "vacío", "engine": None, "confidence": 0.0}
    
    text_lower = text.lower()
    
    print(f"[AI_ANALYZER] 🔍 Analizando: {text[:60]}...")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 1️⃣ DETECCIÓN DE PROBLEMAS DE TEXTO (PRIORIDAD MÁXIMA)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if _is_text_problem(text):
        print(f"[AI_ANALYZER] ✅ Detectado como PROBLEMA DE TEXTO")
        return {
            "subject": "matematicas",
            "intent": "problemas",
            "engine": "generic_engine",
            "confidence": 0.95
        }
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 2️⃣ OPERACIONES MATEMÁTICAS PURAS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    for pattern, result in _PURE_MATH_PATTERNS:
        if re.match(pattern, text):
            subject, intent, engine = result
            print(f"[AI_ANALYZER] ✅ Detectado como OPERACIÓN PURA: {intent}")
            return {
                "subject": subject,
                "intent": intent,
                "engine": engine,
                "confidence": 0.90
            }
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 3️⃣ PALABRAS CLAVE DESDE nlu_labels.json
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    for subject, cfg in _LABELS.items():
        palabras = cfg.get("palabras_clave", [])
        engines = cfg.get("engines", {})

        for intent, engine in engines.items():
            tokens = [intent] + palabras
            if any(tok in text_lower for tok in tokens):
                print(f"[AI_ANALYZER] ✅ Detectado por palabras clave: {intent}")
                return {
                    "subject": subject,
                    "intent": intent,
                    "engine": engine,
                    "confidence": 0.70
                }
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 4️⃣ FALLBACK: Si tiene números y texto, asumir problema
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    has_numbers = bool(re.search(r"\d", text))
    has_letters = bool(re.search(r"[a-záéíóúñ]", text_lower))
    
    if has_numbers and has_letters and len(text) > 20:
        print(f"[AI_ANALYZER] ⚠️ Fallback: problema genérico")
        return {
            "subject": "matematicas",
            "intent": "problemas",
            "engine": "generic_engine",
            "confidence": 0.60
        }
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 5️⃣ ÚLTIMO RECURSO
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print(f"[AI_ANALYZER] ⚠️ No se pudo clasificar específicamente")
    return {
        "subject": "general",
        "intent": "desconocido",
        "engine": "generic_engine",
        "confidence": 0.30
    }


# ================================================================
# ⚙️ EJECUTAR MOTOR DETECTADO
# ================================================================
def run_engine_for(engine_name: str, prompt: str, step: int, answer: str, errors: int) -> Dict[str, Any]:
    """
    Carga y ejecuta el motor correspondiente usando el sistema dinámico.
    """
    if not engine_name:
        return {
            "status": "ask",
            "message": "No sé exactamente qué tipo de ejercicio es. ¿Podrías explicarlo un poco más?",
            "expected_answer": None,
            "topic": "general",
            "hint_type": "general_indefinido",
            "next_step": step
        }

    # --- 1️⃣ Cargar el motor dinámicamente ---
    engine_func = load_engine(engine_name)
    if not engine_func:
        return {
            "status": "error",
            "message": f"No se pudo encontrar el motor '{engine_name}'.",
            "expected_answer": None,
            "topic": "general",
            "hint_type": "general_error",
            "next_step": step
        }

    # --- 2️⃣ Ejecutar el motor ---
    try:
        result = engine_func(prompt, step, answer, errors)
        validate_output(result, engine_name)
        return result
    except Exception as e:
        print(f"[AI_ANALYZER] ❌ Error en motor {engine_name}: {e}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": f"Se produjo un error en el motor {engine_name}: {str(e)}",
            "expected_answer": None,
            "topic": "general",
            "hint_type": "general_error",
            "next_step": step
        }


# ================================================================
# 🧪 DIAGNÓSTICO
# ================================================================
def test_analyzer():
    """
    Prueba rápida del analizador y de la carga dinámica de motores.
    """
    examples = [
        "3 + 5",
        "2,5 + 1,25",
        "0.234 * 2",
        "2 * 0.234",
        "0.235 / 2",
        "25% de 80",
        "4/6 + 1/3",
        "dividir 24 entre 6",
        "Laura y Cecilia compraron 1/4 kilo de helado cada uno. Danila compró 1 kilo y medio, y Pedro compró 1/2 kilo. ¿Cuánto helado tienen entre todos?",
        "María tiene 5 caramelos y le dan 3 más. ¿Cuántos tiene ahora?",
        "En casa hay un cajón con 8 manteles. Al cabo de unos días se han ensuciado 6 manteles. ¿Cuántos manteles no se han ensuciado?"
    ]

    for ex in examples:
        print("\n" + "="*60)
        info = analyze_prompt(ex)
        print("🧩", ex)
        print("→", info)

        engine_name = info["engine"]
        if engine_name:
            try:
                res = run_engine_for(engine_name, ex, 0, "", 0)
                print("⚙️ Resultado:", res.get("status"), "-", res.get("message", "")[:100])
            except Exception as e:
                print(f"❌ Error ejecutando: {e}")
        else:
            print("❌ No se detectó motor.")