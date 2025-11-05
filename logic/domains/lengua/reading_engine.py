# -*- coding: utf-8 -*-
"""
reading_engine.py
--------------------------------------------------
Motor de comprensión lectora para Tutorín.
Guía al estudiante paso a paso a través de ejercicios de lectura comprensiva.

Pasos típicos:
1. Lectura del texto
2. Identificación de idea principal
3. Comprensión de detalles
4. Inferencias y conclusiones
5. Vocabulario en contexto
"""

import re
import json
from typing import Dict, Any, List, Optional, Tuple

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

def _generate_hint(hint_type: str, error_count: int, context: str) -> str:
    """Genera una pista usando el sistema de hints"""
    try:
        from logic.ai_hints.hints_reading import get_hint
        e = max(1, min(int(error_count), 9))
        return get_hint(hint_type, e, context, "")
    except Exception as e:
        print(f"[READING_ENGINE] ⚠️ Error generando pista: {e}")
        return "💡 Pista: Lee el texto con atención y busca la información relevante."

# ═══════════════════════════════════════════════════════════════
# FUNCIONES AUXILIARES
# ═══════════════════════════════════════════════════════════════

def _norm_cycle(cycle: str | None) -> str:
    """Normaliza el ciclo educativo"""
    c = (cycle or "c2").strip().lower()
    if c in {"1", "c1"}: return "c1"
    if c in {"2", "c2"}: return "c2"
    if c in {"3", "c3"}: return "c3"
    return "c2"

def _parse_reading_exercise(question: str) -> Optional[Dict[str, Any]]:
    """
    Parsea un ejercicio de lectura.
    Formato esperado:
    {
        "text": "El texto a leer...",
        "questions": [
            {"q": "¿Cuál es la idea principal?", "answer": "respuesta", "type": "main_idea"},
            {"q": "¿Qué significa...?", "answer": "respuesta", "type": "vocabulary"}
        ]
    }

    O formato simple:
    TEXTO: [texto]
    PREGUNTA: [pregunta]
    """
    try:
        # Intentar parsear JSON
        data = json.loads(question)
        if "text" in data and "questions" in data:
            return data
    except:
        pass

    # Formato simple con marcadores
    text_match = re.search(r"TEXTO:\s*(.+?)(?:PREGUNTA:|$)", question, re.DOTALL | re.IGNORECASE)
    question_match = re.search(r"PREGUNTA:\s*(.+?)(?:RESPUESTA:|$)", question, re.DOTALL | re.IGNORECASE)
    answer_match = re.search(r"RESPUESTA:\s*(.+?)$", question, re.DOTALL | re.IGNORECASE)

    if text_match and question_match:
        text = text_match.group(1).strip()
        q = question_match.group(1).strip()
        answer = answer_match.group(1).strip() if answer_match else ""

        return {
            "text": text,
            "questions": [{"q": q, "answer": answer, "type": "comprehension"}]
        }

    return None

def _format_text_display(text: str) -> str:
    """Formatea el texto para una mejor visualización"""
    return (
        f"<div style='padding:16px;background:#f9fafb;border-left:4px solid #3b82f6;"
        f"border-radius:8px;margin:12px 0;line-height:1.8'>"
        f"<div style='font-size:0.9em;color:#6b7280;margin-bottom:8px'>"
        f"<b>📖 Texto para leer:</b></div>"
        f"<div style='font-size:1.05em;color:#1f2937'>{text}</div>"
        f"</div>"
    )

def _check_answer_similarity(user_answer: str, expected_answer: str) -> Tuple[bool, float]:
    """
    Verifica similitud entre respuestas.
    Retorna (es_correcta, similitud_porcentaje)
    """
    user = user_answer.lower().strip()
    expected = expected_answer.lower().strip()

    # Coincidencia exacta
    if user == expected:
        return True, 1.0

    # Coincidencia parcial (palabras clave)
    expected_words = set(expected.split())
    user_words = set(user.split())

    if len(expected_words) == 0:
        return False, 0.0

    common_words = expected_words.intersection(user_words)
    similarity = len(common_words) / len(expected_words)

    # Si tiene más del 70% de palabras clave, considerar correcta
    is_correct = similarity >= 0.7

    return is_correct, similarity

# ═══════════════════════════════════════════════════════════════
# MENSAJES PEDAGÓGICOS
# ═══════════════════════════════════════════════════════════════

def _msg_reading_intro(text: str, cycle: str) -> str:
    """Mensaje de introducción a la lectura"""
    text_display = _format_text_display(text)

    tips = {
        "c1": "Lee con calma. Puedes leer el texto las veces que necesites.",
        "c2": "Lee con atención. Fíjate en los detalles importantes.",
        "c3": "Lee comprensivamente. Identifica ideas principales y secundarias."
    }

    tip = tips.get(cycle, tips["c2"])

    return (
        f"<div style='padding:12px;background:#dbeafe;border-radius:8px;margin-top:8px'>"
        f"🤓 <b>¡Vamos a practicar la lectura comprensiva!</b><br>"
        f"📚 {tip}"
        f"</div>"
        f"{text_display}"
        f"<div style='padding:10px;background:#f0f9ff;border-radius:6px;margin-top:12px'>"
        f"✅ <b>Cuando hayas leído el texto, escribe 'listo' o 'sí' para continuar.</b>"
        f"</div>"
    )

def _msg_question(question_data: Dict[str, Any], text: str, question_num: int, total_questions: int) -> str:
    """Mensaje para una pregunta específica"""
    text_display = _format_text_display(text)

    question_text = question_data.get("q", "")
    question_type = question_data.get("type", "comprehension")

    # Iconos según tipo de pregunta
    icons = {
        "main_idea": "💡",
        "detail": "🔍",
        "vocabulary": "📖",
        "inference": "🤔",
        "comprehension": "📝"
    }

    icon = icons.get(question_type, "❓")

    return (
        f"{text_display}"
        f"<div style='padding:12px;background:#fef3c7;border-radius:8px;margin-top:12px'>"
        f"{icon} <b>Pregunta {question_num}/{total_questions}:</b><br>"
        f"{question_text}"
        f"</div>"
    )

def _msg_correct(question_num: int, total_questions: int) -> str:
    """Mensaje de respuesta correcta"""
    emojis = ["🎉", "✨", "🌟", "🎊", "👏"]
    emoji = emojis[question_num % len(emojis)]

    return (
        f"<div style='padding:12px;background:#dcfce7;border-radius:8px;margin-top:12px'>"
        f"{emoji} <b>¡Muy bien!</b> Respuesta correcta.<br>"
        f"📊 Progreso: {question_num}/{total_questions} preguntas completadas"
        f"</div>"
    )

def _msg_partial(similarity: float) -> str:
    """Mensaje de respuesta parcialmente correcta"""
    return (
        f"<div style='padding:12px;background:#fef3c7;border-radius:8px;margin-top:12px'>"
        f"🤏 <b>Casi lo tienes...</b><br>"
        f"Tu respuesta está cerca, pero le falta algo. Inténtalo de nuevo."
        f"</div>"
    )

def _msg_completion() -> str:
    """Mensaje de finalización del ejercicio"""
    return (
        f"<div style='padding:16px;background:#dcfce7;border-radius:8px;margin-top:12px;"
        f"border-left:4px solid #10b981'>"
        f"🎉 <b>¡Excelente trabajo!</b><br>"
        f"Has completado el ejercicio de comprensión lectora.<br>"
        f"📚 ¡Sigue practicando para mejorar tu lectura!"
        f"</div>"
    )

# ════════════════════════════════════════════════════════════
# Motor principal
# ════════════════════════════════════════════════════════════

def handle_step(question: str, step_now: int, last_answer: str, error_count: int, cycle: str = "c2") -> Dict[str, Any]:
    """
    Motor principal de comprensión lectora.

    Pasos:
    0: Presentación del texto
    1-N: Preguntas de comprensión
    N+1: Finalización
    """
    parsed = _parse_reading_exercise(question)
    if not parsed:
        return {
            "status": "error",
            "message": "❌ No se pudo procesar el ejercicio de lectura. Verifica el formato.",
            "expected_answer": None,
            "topic": "lectura",
            "hint_type": "read_error",
            "next_step": 0
        }

    cycle = _norm_cycle(cycle)
    text = parsed["text"]
    questions = parsed.get("questions", [])
    total_questions = len(questions)

    # Detectar si pidió ayuda
    asking_for_help = _is_asking_for_help(last_answer)

    # ═══════════════════════════════════════════════════════════
    # PASO 0: PRESENTACIÓN DEL TEXTO
    # ═══════════════════════════════════════════════════════════
    if step_now == 0:
        msg = _msg_reading_intro(text, cycle)

        # Añadir pista si la pidió
        if asking_for_help or error_count > 0:
            hint = _generate_hint("read_intro", error_count, text)
            msg += (
                f"<div style='padding:10px;background:#fff9c4;border-radius:6px;"
                f"margin-top:10px;border-left:3px solid #fbc02d'>"
                f"💡 {hint}"
                f"</div>"
            )

        return {
            "status": "ask",
            "message": msg,
            "expected_answer": "listo",  # Respuesta flexible
            "topic": "lectura",
            "hint_type": "read_intro",
            "next_step": 1
        }

    # ═══════════════════════════════════════════════════════════
    # PASOS 1-N: PREGUNTAS DE COMPRENSIÓN
    # ═══════════════════════════════════════════════════════════
    if 1 <= step_now <= total_questions:
        question_idx = step_now - 1
        current_question = questions[question_idx]

        msg = _msg_question(current_question, text, step_now, total_questions)

        # Añadir pista si la pidió o tiene errores
        if asking_for_help or error_count > 0:
            question_type = current_question.get("type", "comprehension")
            hint_type = f"read_{question_type}"
            hint = _generate_hint(hint_type, error_count, f"{text}|||{current_question['q']}")
            msg += (
                f"<div style='padding:10px;background:#fff9c4;border-radius:6px;"
                f"margin-top:10px;border-left:3px solid #fbc02d'>"
                f"💡 {hint}"
                f"</div>"
            )

        return {
            "status": "ask",
            "message": msg,
            "expected_answer": current_question.get("answer", ""),
            "topic": "lectura",
            "hint_type": f"read_{current_question.get('type', 'comprehension')}",
            "next_step": step_now + 1
        }

    # ═══════════════════════════════════════════════════════════
    # PASO N+1: FINALIZACIÓN
    # ═══════════════════════════════════════════════════════════
    msg = _msg_completion()

    return {
        "status": "done",
        "message": msg,
        "expected_answer": None,
        "topic": "lectura",
        "hint_type": "read_complete",
        "next_step": step_now + 1
    }


# ════════════════════════════════════════════════════════════
# Función de validación personalizada para lectura
# ════════════════════════════════════════════════════════════

def validate_reading_answer(user_answer: str, expected_answer: str, step: int) -> Tuple[bool, str]:
    """
    Valida respuestas de lectura con más flexibilidad que comparación exacta.

    Returns:
        (is_correct, feedback_message)
    """
    user = user_answer.lower().strip()

    # Paso 0: aceptar cualquier confirmación
    if step == 0:
        confirmations = ["listo", "si", "sí", "ok", "vale", "entendido", "leído", "leido"]
        if user in confirmations:
            return True, "¡Perfecto! Continuemos con las preguntas."
        return False, "Tómate tu tiempo para leer el texto completo."

    # Otros pasos: verificar similitud
    is_correct, similarity = _check_answer_similarity(user_answer, expected_answer)

    if is_correct:
        return True, "¡Correcto!"
    elif similarity > 0.4:
        return False, "Tu respuesta está cerca. Revisa el texto e intenta ser más específico."
    else:
        return False, "Esa no es la respuesta. Vuelve a leer el texto con atención."
