# -*- coding: utf-8 -*-
"""
generic_engine.py - VERSIÓN 2 MEJORADA
Motor de problemas con IA pedagógica completa.
✅ Detecta múltiples formas de pedir ayuda
✅ Validación flexible mejorada
✅ Sistema de pistas contextual robusto
"""

import re
import os
import json
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Inicializar cliente OpenAI
try:
    from openai import OpenAI
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[GENERIC_ENGINE] ⚠️ OPENAI_API_KEY no está configurada")
        AI_AVAILABLE = False
        client = None
    else:
        client = OpenAI(api_key=api_key)
        AI_AVAILABLE = True
        print("[GENERIC_ENGINE] ✅ OpenAI inicializado correctamente")
        
except Exception as e:
    print(f"[GENERIC_ENGINE] ⚠️ Error al inicializar OpenAI: {e}")
    AI_AVAILABLE = False
    client = None


# ══════════════════════════════════════════════════════════════
# 0. DETECCIÓN DE PETICIÓN DE AYUDA
# ══════════════════════════════════════════════════════════════

HELP_KEYWORDS = [
    # Variantes de "no sé"
    "no se", "no sé", "nose", "nosé", "no lo se", "no lo sé",
    # Expresiones de confusión
    "no entiendo", "no comprendo", "no lo entiendo", "no lo comprendo",
    # Peticiones directas
    "ayuda", "ayudame", "ayúdame", "ayudame por favor",
    "pista", "dame una pista", "necesito ayuda",
    # Expresiones de incertidumbre
    "no estoy seguro", "no estoy segura", "nose que hacer", "no sé qué hacer",
    "que hago", "qué hago", "como lo hago", "cómo lo hago"
]

def _is_asking_for_help(user_answer: str) -> bool:
    """Detecta si el usuario está pidiendo ayuda"""
    answer_clean = user_answer.lower().strip()
    
    # Verificar si contiene alguna palabra clave de ayuda
    for keyword in HELP_KEYWORDS:
        if keyword in answer_clean:
            print(f"[GENERIC_ENGINE] 🆘 Usuario pidió ayuda: '{keyword}' detectado")
            return True
    
    # También considerar respuestas muy cortas como "?" o "..."
    if answer_clean in ["?", "??", "???", "...", "..", ".", ""]:
        print(f"[GENERIC_ENGINE] 🆘 Usuario pidió ayuda: respuesta vacía/interrogante")
        return True
    
    return False


# ══════════════════════════════════════════════════════════════
# 1. ANÁLISIS Y DESCOMPOSICIÓN DEL PROBLEMA
# ══════════════════════════════════════════════════════════════

DECOMPOSITION_PROMPT = """Eres Tutorín, un profesor de matemáticas de primaria experto en resolver problemas paso a paso.

PROBLEMA:
{problem}

Descompón este problema siguiendo una estructura pedagógica clara que ayude al niño a comprender y resolver.

Responde SOLO con JSON en este formato exacto:

{{
  "tipo_problema": "simple" | "medio" | "complejo",
  "datos": {{
    "conocidos": ["lista de datos que da el problema"],
    "desconocido": "qué debemos calcular"
  }},
  "pasos": [
    {{
      "numero": 0,
      "tipo": "comprension",
      "descripcion": "Entender el problema y los datos",
      "operacion": "comprension",
      "pregunta": "Pregunta sobre comprensión del enunciado",
      "respuesta_esperada": "respuesta de comprensión",
      "pista_contextual": "Pista específica de este problema si dice 'no sé'"
    }},
    {{
      "numero": 1,
      "tipo": "calculo",
      "descripcion": "Descripción clara del paso",
      "operacion": "suma" | "resta" | "multiplicacion" | "division" | "conversion",
      "valores": [lista de números involucrados],
      "pregunta": "Pregunta concreta para el niño",
      "respuesta_esperada": "valor numérico exacto",
      "explicacion_adicional": "contexto o ayuda visual",
      "pista_contextual": "Pista específica si no sabe"
    }}
  ],
  "respuesta_final": "valor final del problema",
  "unidad": "unidad de medida si aplica (€, kg, metros, etc.)"
}}

REGLAS IMPORTANTES:
1. SIEMPRE incluir un paso 0 de COMPRENSIÓN del problema
2. En el paso 0, preguntar sobre los DATOS del problema o QUÉ deben calcular
3. La respuesta_esperada del paso 0 debe ser FLEXIBLE (ej: "cuanto paga alumno")
4. Problemas SIMPLES (2-3 pasos): 1 comprensión + 1-2 cálculos
5. Problemas MEDIOS (4-5 pasos): 1 comprensión + 3-4 cálculos
6. Problemas COMPLEJOS (6+ pasos): 1 comprensión + 5+ cálculos
7. Cada paso debe ser MUY CONCRETO y hacer UNA SOLA PREGUNTA
8. Para FRACCIONES: convierte a decimal en respuesta_esperada
9. La pista_contextual debe ser ESPECÍFICA del problema, no genérica
10. Las respuestas esperadas de comprensión deben ser PALABRAS CLAVE, no frases completas

Ejemplo de respuesta esperada FLEXIBLE:
- Mal: "cuanto debe pagar cada alumno exactamente"
- Bien: "cuanto paga alumno" (palabras clave: cuanto, paga, alumno)

RECUERDA: 
- El paso 0 SIEMPRE es de comprensión
- Cada pista_contextual debe mencionar números y operaciones ESPECÍFICAS del problema
- NO uses pistas genéricas como "piensa bien" o "lee con atención"
"""

def _decompose_problem(problem: str) -> Optional[Dict[str, Any]]:
    """Usa IA para descomponer el problema en pasos manejables"""
    if not AI_AVAILABLE:
        print("[GENERIC_ENGINE] ⚠️ IA no disponible para descomposición")
        return None
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Eres Tutorín, profesor de primaria experto en descomponer problemas. Respondes SOLO con JSON válido."
                },
                {
                    "role": "user",
                    "content": DECOMPOSITION_PROMPT.format(problem=problem)
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=1000
        )
        
        result_text = response.choices[0].message.content.strip()
        result = json.loads(result_text)
        
        print(f"[GENERIC_ENGINE] ✅ Problema descompuesto en {len(result.get('pasos', []))} pasos")
        print(f"[GENERIC_ENGINE] 📊 Tipo: {result.get('tipo_problema', 'desconocido')}")
        return result
        
    except Exception as e:
        print(f"[GENERIC_ENGINE] ⚠️ Error en descomposición: {e}")
        import traceback
        traceback.print_exc()
        return None


# ══════════════════════════════════════════════════════════════
# 2. GENERACIÓN DE PISTAS PROGRESIVAS
# ══════════════════════════════════════════════════════════════

HINT_PROMPT = """Eres Tutorín, un profesor de primaria paciente y pedagógico.

CONTEXTO:
Problema original: {problem}
Paso actual: {step_description}
Pregunta que hice: {question}
Respuesta del niño: {user_answer}
Respuesta correcta: {expected_answer}
Número de intentos fallidos: {error_count}
Pista contextual específica: {contextual_hint}
Explicación adicional: {extra_help}

IMPORTANTE: Usa la pista contextual específica ({contextual_hint}) como base para tu respuesta.
Esta pista está diseñada específicamente para este problema y este paso.

Genera UNA PISTA pedagógica según el nivel de error:

NIVEL 0 (primer intento - pidió ayuda): 
- USA la pista contextual específica
- Sé motivador y directo
- Menciona los números concretos del problema
- Ejemplo: "{contextual_hint}"

NIVEL 1 (1 error):
- Amplía la pista contextual con más detalles
- Menciona la operación necesaria
- Da una estrategia concreta

NIVEL 2 (2 errores):
- Proceso paso a paso muy detallado
- Usa la explicación adicional si está disponible
- Puedes mencionar herramientas (dedos, papel, etc.)

NIVEL 3+ (3+ errores):
- Explicación completa con la solución
- Muestra el cálculo exacto
- Verifica que entiendan el proceso

FORMATO DE RESPUESTA:
- Máximo 3 líneas
- Lenguaje simple de primaria
- Incluye emojis apropiados (💭💡📝👨‍🏫🎯)
- NO uses jerga matemática compleja
- SIEMPRE menciona números específicos del problema

Responde SOLO con la pista en texto plano, sin JSON ni HTML.
"""

def _generate_hint(problem: str, step_info: Dict, user_answer: str, error_count: int) -> str:
    """Genera pista pedagógica adaptada al nivel de error"""
    # Fallback primario: usar pista contextual del paso
    contextual = step_info.get("pista_contextual", "")
    
    if not AI_AVAILABLE:
        if contextual:
            print(f"[GENERIC_ENGINE] 💡 Usando pista contextual (IA no disponible): {contextual[:50]}...")
            return f"💡 {contextual}"
        return "💡 Intenta de nuevo. Piensa con calma en la operación que necesitas hacer."
    
    try:
        extra_help = step_info.get("explicacion_adicional", "")
        contextual_hint = contextual if contextual else "Lee el problema con atención y piensa en los datos que te dan."
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Eres Tutorín, profesor de primaria. Das pistas pedagógicas concisas y específicas en texto plano."
                },
                {
                    "role": "user",
                    "content": HINT_PROMPT.format(
                        problem=problem,
                        step_description=step_info.get("descripcion", ""),
                        question=step_info.get("pregunta", ""),
                        user_answer=user_answer,
                        expected_answer=step_info.get("respuesta_esperada", ""),
                        error_count=error_count,
                        contextual_hint=contextual_hint,
                        extra_help=extra_help
                    )
                }
            ],
            temperature=0.4,
            max_tokens=150
        )
        
        hint = response.choices[0].message.content.strip()
        print(f"[GENERIC_ENGINE] 💡 Pista IA generada (nivel {error_count}): {hint[:50]}...")
        return hint
        
    except Exception as e:
        print(f"[GENERIC_ENGINE] ⚠️ Error generando pista con IA: {e}")
        # Fallback: usar la pista contextual del paso
        if contextual:
            print(f"[GENERIC_ENGINE] 💡 Usando pista contextual (fallback): {contextual[:50]}...")
            return f"💡 {contextual}"
        return "💡 Revisa tu cálculo con cuidado. ¿Qué operación necesitas hacer?"


# ══════════════════════════════════════════════════════════════
# 3. VALIDACIÓN DE RESPUESTAS (MEJORADA v2)
# ══════════════════════════════════════════════════════════════

def _normalize_text(text: str) -> str:
    """Normaliza texto para comparación flexible"""
    # Convertir a minúsculas
    text = text.lower().strip()
    
    # Remover acentos comunes
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ü': 'u', 'ñ': 'n'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Remover signos de puntuación
    text = re.sub(r'[¿?¡!.,;:]', '', text)
    
    return text

def _extract_keywords(text: str) -> List[str]:
    """Extrae palabras clave significativas (>3 caracteres)"""
    normalized = _normalize_text(text)
    words = normalized.split()
    # Filtrar palabras cortas y stopwords comunes
    stopwords = ['de', 'el', 'la', 'los', 'las', 'un', 'una', 'que', 'del', 'al']
    keywords = [w for w in words if len(w) > 2 and w not in stopwords]
    return keywords

def _are_similar_words(word1: str, word2: str) -> bool:
    """Verifica si dos palabras son similares (misma raíz o una contiene a la otra)"""
    # Normalizar ambas palabras
    w1 = _normalize_text(word1)
    w2 = _normalize_text(word2)
    
    # Comparación exacta
    if w1 == w2:
        return True
    
    # Si ambas tienen al menos 4 caracteres, comparar raíz
    if len(w1) >= 4 and len(w2) >= 4:
        # Extraer raíz (primeras 4 letras)
        root1 = w1[:4]
        root2 = w2[:4]
        
        if root1 == root2:
            return True
        
        # Verificar si una palabra contiene a la otra
        if w1 in w2 or w2 in w1:
            return True
    
    # Para palabras más cortas, verificar si una está contenida en la otra
    if len(w1) >= 3 and len(w2) >= 3:
        if w1 in w2 or w2 in w1:
            return True
    
    return False

def _validate_answer(user_answer: str, expected: str, step_type: str = "calculo") -> bool:
    """
    Valida si la respuesta del usuario es correcta (con tolerancia mejorada)
    
    Args:
        user_answer: Respuesta del usuario
        expected: Respuesta esperada
        step_type: Tipo de paso ("comprension" o "calculo")
    """
    try:
        # Limpiar respuestas
        user_clean = user_answer.strip().replace(",", ".").lower()
        expected_clean = str(expected).strip().replace(",", ".").lower()
        
        print(f"[GENERIC_ENGINE] 🔍 Validando: '{user_clean}' vs '{expected_clean}' (tipo: {step_type})")
        
        # Comparación exacta primero
        if user_clean == expected_clean:
            print("[GENERIC_ENGINE] ✅ Coincidencia exacta")
            return True
        
        # Para pasos NUMÉRICOS: comparación numérica con tolerancia
        if step_type != "comprension":
            try:
                user_num = float(user_clean)
                expected_num = float(expected_clean)
                # Tolerancia del 0.01 para decimales
                is_correct = abs(user_num - expected_num) < 0.01
                if is_correct:
                    print(f"[GENERIC_ENGINE] ✅ Validación numérica: {user_num} ≈ {expected_num}")
                return is_correct
            except ValueError:
                # No es número, continuar con validación de texto
                pass
        
        # Para pasos de COMPRENSIÓN: validación flexible por palabras clave
        print("[GENERIC_ENGINE] 🔍 Validación de comprensión por palabras clave...")
        
        # Normalizar textos
        user_normalized = _normalize_text(user_clean)
        expected_normalized = _normalize_text(expected_clean)
        
        # Comparación normalizada
        if user_normalized == expected_normalized:
            print("[GENERIC_ENGINE] ✅ Coincidencia normalizada")
            return True
        
        # Extraer palabras clave de ambas respuestas
        expected_keywords = _extract_keywords(expected_clean)
        user_keywords = _extract_keywords(user_clean)
        
        if not expected_keywords:
            print("[GENERIC_ENGINE] ⚠️ No hay palabras clave en respuesta esperada")
            # Si la respuesta esperada no tiene palabras clave, aceptar cualquier respuesta no vacía
            return len(user_clean.strip()) > 0
        
        print(f"[GENERIC_ENGINE] 🔍 Palabras esperadas: {expected_keywords}")
        print(f"[GENERIC_ENGINE] 🔍 Palabras del usuario: {user_keywords}")
        
        # Contar coincidencias usando similitud de palabras
        matches = 0
        matched_words = []
        for exp_word in expected_keywords:
            for user_word in user_keywords:
                if _are_similar_words(exp_word, user_word):
                    matches += 1
                    matched_words.append(f"{exp_word}≈{user_word}")
                    print(f"[GENERIC_ENGINE] 🔍 Palabra similar: '{exp_word}' ≈ '{user_word}'")
                    break  # Solo contar una vez por palabra esperada
        
        # Calcular ratio de coincidencia
        match_ratio = matches / len(expected_keywords)
        print(f"[GENERIC_ENGINE] 🔍 Coincidencia: {matches}/{len(expected_keywords)} = {match_ratio*100:.0f}%")
        print(f"[GENERIC_ENGINE] 🔍 Palabras coincidentes: {matched_words}")
        
        # Aceptar si al menos 50% de palabras clave coinciden (más flexible)
        if match_ratio >= 0.5:
            print(f"[GENERIC_ENGINE] ✅ Validación por similitud: {match_ratio*100:.0f}% ({matches} de {len(expected_keywords)} palabras)")
            return True
        
        # Si solo hay 1-2 palabras esperadas, ser aún más flexible
        if len(expected_keywords) <= 2 and matches >= 1:
            print(f"[GENERIC_ENGINE] ✅ Validación flexible (pocas palabras): {matches} coincidencia(s)")
            return True
        
        print(f"[GENERIC_ENGINE] ❌ No hay suficiente coincidencia ({match_ratio*100:.0f}%)")
        return False
            
    except Exception as e:
        print(f"[GENERIC_ENGINE] ⚠️ Error validando: {e}")
        import traceback
        traceback.print_exc()
        return False


# ══════════════════════════════════════════════════════════════
# 4. MOTOR PRINCIPAL
# ══════════════════════════════════════════════════════════════

# Cache global para almacenar la descomposición del problema
_problem_cache = {}

def handle_step(question: str, step_now: int, last_answer: str, error_count: int, cycle: str = "c2"):
    """
    Motor principal con IA pedagógica completa.
    Maneja problemas de cualquier complejidad con guía paso a paso.
    
    ✅ NUEVO: Detecta peticiones de ayuda automáticamente
    """
    
    print(f"[GENERIC_ENGINE] 🔄 handle_step llamado: step={step_now}, last_answer='{last_answer}', errors={error_count}")
    
    # Paso 0: Descomponer el problema
    if step_now == 0:
        print(f"[GENERIC_ENGINE] 🔍 Analizando problema: {question[:80]}...")
        
        decomposition = _decompose_problem(question)
        
        if not decomposition:
            return {
                "status": "done",
                "message": (
                    "<div style='padding:15px;background:#fee;border-radius:8px'>"
                    "<b>⚠️ No pude analizar el problema</b><br><br>"
                    "La inteligencia artificial no está disponible.<br>"
                    "Por favor, verifica tu conexión e intenta de nuevo."
                    "</div>"
                ),
                "expected_answer": "error",
                "topic": "problemas",
                "hint_type": "problem_error",
                "next_step": step_now + 1
            }
        
        # Guardar en cache (usando hash del problema como key)
        cache_key = hash(question)
        _problem_cache[cache_key] = decomposition
        
        tipo = decomposition.get("tipo_problema", "medio")
        num_pasos = len(decomposition.get("pasos", []))
        datos = decomposition.get("datos", {})
        conocidos = datos.get("conocidos", [])
        desconocido = datos.get("desconocido", "la solución")
        
        # Mensaje inicial atractivo con datos
        tipo_emoji = {"simple": "😊", "medio": "🤔", "complejo": "🎯"}
        tipo_text = {"simple": "sencillo", "medio": "interesante", "complejo": "¡desafiante!"}
        
        # Formatear datos conocidos
        datos_html = "<br>".join([f"• {dato}" for dato in conocidos]) if conocidos else "• (detectando datos...)"
        
        return {
            "status": "ask",
            "message": (
                f"<div style='padding:15px;background:#e3f2fd;border-radius:8px;border-left:4px solid #2196f3'>"
                f"<b>🎓 ¡Vamos a resolver este problema {tipo_text[tipo]}!</b><br><br>"
                f"📖 <i>{question}</i><br><br>"
                f"<div style='background:white;padding:12px;border-radius:6px;margin-top:10px'>"
                f"<b>📊 DATOS DEL PROBLEMA:</b><br>"
                f"<div style='margin-left:10px;margin-top:5px'>"
                f"{datos_html}"
                f"</div><br>"
                f"<b>❓ DEBEMOS CALCULAR:</b><br>"
                f"<div style='margin-left:10px'>"
                f"• {desconocido}"
                f"</div>"
                f"</div><br>"
                f"<div style='background:#fff3e0;padding:10px;border-radius:6px;margin-top:10px'>"
                f"{tipo_emoji[tipo]} <b>He preparado {num_pasos} pasos</b> para resolverlo paso a paso.<br>"
                f"Primero vamos a asegurarnos de que entiendes bien el problema. ¡Vamos allá!"
                f"</div><br>"
                f"<b>💡 Escribe 'empezar' cuando estés listo.</b>"
                f"</div>"
            ),
            "expected_answer": "empezar",
            "topic": "problemas",
            "hint_type": "problem_start",
            "next_step": 1
        }
    
    # Pasos 1+: Ejecución paso a paso
    cache_key = hash(question)
    decomposition = _problem_cache.get(cache_key)
    
    if not decomposition:
        # Reanalizar si perdimos el cache
        print(f"[GENERIC_ENGINE] 🔄 Cache perdido, reanalizando...")
        decomposition = _decompose_problem(question)
        if decomposition:
            _problem_cache[cache_key] = decomposition
    
    if not decomposition:
        return {
            "status": "done",
            "message": "⚠️ Error: No pude recuperar el análisis del problema.",
            "expected_answer": "error",
            "topic": "problemas",
            "hint_type": "problem_error",
            "next_step": step_now + 1
        }
    
    pasos = decomposition.get("pasos", [])
    current_step_index = step_now - 1
    
    # Verificar si terminamos todos los pasos
    if current_step_index >= len(pasos):
        respuesta_final = decomposition.get("respuesta_final", "")
        unidad = decomposition.get("unidad", "")
        
        # Limpiar cache
        if cache_key in _problem_cache:
            del _problem_cache[cache_key]
        
        return {
            "status": "done",
            "message": (
                f"<div style='padding:15px;background:#e8f5e9;border-radius:8px;text-align:center'>"
                f"<b>🎉 ¡EXCELENTE TRABAJO!</b><br><br>"
                f"<div style='font-size:1.2em;margin:15px 0'>"
                f"Has completado todos los pasos correctamente 💪<br>"
                f"<b>Respuesta final: {respuesta_final} {unidad}</b>"
                f"</div>"
                f"<div style='background:white;padding:10px;border-radius:6px;margin-top:10px'>"
                f"🌟 Has demostrado que puedes resolver problemas complejos paso a paso.<br>"
                f"¡Sigue practicando así!"
                f"</div>"
                f"</div>"
            ),
            "expected_answer": str(respuesta_final),
            "topic": "problemas",
            "hint_type": "problem_complete",
            "next_step": step_now + 1
        }
    
    # Obtener paso actual
    current_step = pasos[current_step_index]
    step_num = current_step.get("numero", current_step_index + 1)
    step_type = current_step.get("tipo", "calculo")
    pregunta = current_step.get("pregunta", "")
    respuesta_esperada = str(current_step.get("respuesta_esperada", ""))
    
    print(f"[GENERIC_ENGINE] 📝 Paso {step_num}/{len(pasos)} (tipo: {step_type}): esperando '{respuesta_esperada}'")
    
    # ✅ NUEVO: Detectar si el usuario pidió ayuda
    asking_for_help = _is_asking_for_help(last_answer)
    
    if asking_for_help:
        print(f"[GENERIC_ENGINE] 🆘 Usuario pidió ayuda, generando pista...")
        # Tratar como si fuera un error para generar pista
        if error_count == 0:
            error_count = 1  # Asegurar que se genere pista
    
    # Progreso visual
    progress_bar = ""
    for i in range(len(pasos)):
        if i < current_step_index:
            progress_bar += "✅ "
        elif i == current_step_index:
            progress_bar += "▶️ "
        else:
            progress_bar += "⚪ "
    
    # Construir mensaje del paso según el tipo
    if step_type == "comprension":
        # Paso de comprensión: mostrar los datos
        datos = decomposition.get("datos", {})
        conocidos = datos.get("conocidos", [])
        desconocido = datos.get("desconocido", "la solución")
        datos_html = "<br>".join([f"• {dato}" for dato in conocidos]) if conocidos else ""
        
        message = (
            f"<div style='padding:15px;background:#e8f5e9;border-radius:8px'>"
            f"<div style='margin-bottom:10px;font-size:0.9em;color:#666'>"
            f"{progress_bar} (Paso {step_num} de {len(pasos)})"
            f"</div>"
            f"<b>📚 Paso {step_num}: COMPRENSIÓN DEL PROBLEMA</b><br><br>"
            f"<div style='background:white;padding:10px;border-radius:6px;margin-bottom:10px'>"
            f"<b>📊 Datos que tenemos:</b><br>"
            f"{datos_html}<br><br>"
            f"<b>❓ Qué debemos calcular:</b><br>"
            f"• {desconocido}"
            f"</div>"
            f"<b>🤔 {pregunta}</b>"
            f"</div>"
        )
    else:
        # Paso de cálculo normal
        message = (
            f"<div style='padding:15px;background:#fff3e0;border-radius:8px'>"
            f"<div style='margin-bottom:10px;font-size:0.9em;color:#666'>"
            f"{progress_bar} (Paso {step_num} de {len(pasos)})"
            f"</div>"
            f"<b>📝 Paso {step_num}:</b><br>"
            f"{pregunta}"
            f"</div>"
        )
    
    # Si hay errores O pidió ayuda, añadir pista CONTEXTUAL
    if error_count > 0 or asking_for_help:
        hint = _generate_hint(question, current_step, last_answer, error_count)
        message += (
            f"<div style='padding:10px;background:#fff9c4;border-radius:6px;margin-top:10px;border-left:3px solid #fbc02d'>"
            f"{hint}"
            f"</div>"
        )
    
    return {
        "status": "ask",
        "message": message,
        "expected_answer": respuesta_esperada,
        "topic": "problemas",
        "hint_type": f"problem_step_{step_num}",
        "next_step": step_now + 1,
        "step_type": step_type  # ← Enviar el tipo de paso para validación correcta
    }


# ══════════════════════════════════════════════════════════════
# 5. FUNCIÓN DE VERIFICACIÓN (para solve.py)
# ══════════════════════════════════════════════════════════════

def verify_answer(user_answer: str, expected_answer: str, step_type: str = "calculo") -> bool:
    """
    Función pública para que solve.py valide respuestas.
    Usa la validación mejorada con detección de ayuda.
    
    Returns:
        bool: True si la respuesta es correcta, False si no
        
    Nota: Si el usuario pide ayuda, retorna False para que se incremente error_count
    """
    # Si el usuario está pidiendo ayuda, no es una respuesta correcta
    if _is_asking_for_help(user_answer):
        print(f"[GENERIC_ENGINE] 🆘 verify_answer: Usuario pidió ayuda")
        return False
    
    # Validar la respuesta normalmente
    return _validate_answer(user_answer, expected_answer, step_type)