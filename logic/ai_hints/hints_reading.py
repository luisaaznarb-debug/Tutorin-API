# -*- coding: utf-8 -*-
"""
hints_reading.py
Pistas progresivas para comprensión lectora
"""
import re
from typing import Optional, Tuple

# ═══════════════════════════════════════════════════════════════
# FUNCIONES DE EXTRACCIÓN DE CONTEXTO
# ═══════════════════════════════════════════════════════════════

def _extract_text_and_question(context: str) -> Tuple[str, str]:
    """
    Extrae el texto y la pregunta del contexto.
    Formato esperado: "texto|||pregunta"
    """
    if "|||" in context:
        parts = context.split("|||", 1)
        return parts[0].strip(), parts[1].strip()
    return context, ""

def _extract_key_words(text: str, max_words: int = 5) -> list:
    """Extrae palabras clave del texto (sin stopwords comunes)"""
    stopwords = {
        "el", "la", "los", "las", "un", "una", "unos", "unas",
        "de", "del", "en", "a", "por", "para", "con", "sin",
        "y", "o", "pero", "si", "no", "que", "es", "son", "está", "están",
        "fue", "era", "ser", "estar", "su", "sus", "mi", "mis", "tu", "tus"
    }

    words = re.findall(r'\b[a-záéíóúñ]{4,}\b', text.lower())
    key_words = [w for w in words if w not in stopwords]

    # Contar frecuencias
    word_freq = {}
    for word in key_words:
        word_freq[word] = word_freq.get(word, 0) + 1

    # Ordenar por frecuencia
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

    return [word for word, freq in sorted_words[:max_words]]

# ═══════════════════════════════════════════════════════════════
# PISTAS PARA INTRODUCCIÓN (PASO 0)
# ═══════════════════════════════════════════════════════════════

def _hint_intro(context: str, error_count: int) -> str:
    """Pistas para la fase de lectura inicial del texto"""

    if error_count == 1:
        return (
            "📖 <b>Primera lectura:</b><br>"
            "Lee el texto completo sin prisa. No te preocupes si no entiendes todo a la primera.<br>"
            "Cuando termines, escribe 'listo' o 'sí'."
        )
    elif error_count == 2:
        return (
            "📚 <b>Consejo de lectura:</b><br>"
            "Lee el texto párrafo por párrafo. Tómate tu tiempo.<br>"
            "Si encuentras una palabra que no conoces, trata de entenderla por el contexto.<br>"
            "Cuando hayas leído todo, escribe 'listo'."
        )
    else:
        return (
            "👀 <b>Lee con atención:</b><br>"
            "Asegúrate de leer todo el texto antes de continuar.<br>"
            "Puedes releerlo las veces que necesites.<br>"
            "Escribe 'listo' cuando estés preparado para las preguntas."
        )

# ═══════════════════════════════════════════════════════════════
# PISTAS PARA IDEA PRINCIPAL
# ═══════════════════════════════════════════════════════════════

def _hint_main_idea(context: str, error_count: int) -> str:
    """Pistas para identificar la idea principal"""
    text, question = _extract_text_and_question(context)

    if error_count == 1:
        return (
            "💡 <b>Busca la idea principal:</b><br>"
            "La idea principal es el tema más importante del texto.<br>"
            "Pregúntate: ¿De qué trata principalmente este texto?"
        )
    elif error_count == 2:
        key_words = _extract_key_words(text, 3)
        key_words_str = ", ".join(key_words) if key_words else "las palabras más importantes"

        return (
            f"💡 <b>Pista:</b><br>"
            f"Fíjate en las palabras que más se repiten: <b>{key_words_str}</b>.<br>"
            f"La idea principal suele relacionarse con estas palabras clave."
        )
    else:
        # Extraer primera oración o parte del texto como guía
        first_sentence = text.split('.')[0] if '.' in text else text[:100]

        return (
            f"💡 <b>Te ayudo:</b><br>"
            f"Lee de nuevo el comienzo: <i>\"{first_sentence}...\"</i><br>"
            f"¿De qué tema principal habla el autor?"
        )

# ═══════════════════════════════════════════════════════════════
# PISTAS PARA DETALLES ESPECÍFICOS
# ═══════════════════════════════════════════════════════════════

def _hint_detail(context: str, error_count: int) -> str:
    """Pistas para encontrar detalles específicos"""
    text, question = _extract_text_and_question(context)

    if error_count == 1:
        return (
            "🔍 <b>Busca el detalle:</b><br>"
            "Lee la pregunta con atención y busca esa información específica en el texto.<br>"
            "La respuesta está escrita explícitamente."
        )
    elif error_count == 2:
        # Extraer palabras clave de la pregunta
        question_words = re.findall(r'\b[a-záéíóúñ]{4,}\b', question.lower())
        question_keywords = [w for w in question_words[:3]]

        if question_keywords:
            keywords_str = ", ".join(question_keywords)
            return (
                f"🔍 <b>Busca estas palabras en el texto:</b><br>"
                f"<b>{keywords_str}</b><br>"
                f"La respuesta está cerca de donde aparecen estas palabras."
            )
        else:
            return (
                "🔍 <b>Relee con atención:</b><br>"
                "La información que buscas está en el texto.<br>"
                "Lee cada párrafo buscando la respuesta específica."
            )
    else:
        return (
            "🔍 <b>Última pista:</b><br>"
            "Vuelve a leer el texto completo, párrafo por párrafo.<br>"
            "Cuando encuentres la información que responde a la pregunta, escríbela con tus propias palabras."
        )

# ═══════════════════════════════════════════════════════════════
# PISTAS PARA VOCABULARIO
# ═══════════════════════════════════════════════════════════════

def _hint_vocabulary(context: str, error_count: int) -> str:
    """Pistas para preguntas de vocabulario"""
    text, question = _extract_text_and_question(context)

    if error_count == 1:
        return (
            "📖 <b>Contexto:</b><br>"
            "Para entender una palabra desconocida, lee la oración completa.<br>"
            "Las palabras alrededor te dan pistas sobre su significado."
        )
    elif error_count == 2:
        return (
            "📖 <b>Estrategia:</b><br>"
            "1. Lee la oración completa donde está la palabra<br>"
            "2. Piensa en qué palabra tendría sentido en ese lugar<br>"
            "3. Verifica si tu respuesta hace que la oración tenga sentido"
        )
    else:
        return (
            "📖 <b>Te ayudo:</b><br>"
            "Busca la palabra en el texto y lee las oraciones antes y después.<br>"
            "El contexto te dirá qué significa o a qué se refiere."
        )

# ═══════════════════════════════════════════════════════════════
# PISTAS PARA INFERENCIAS
# ═══════════════════════════════════════════════════════════════

def _hint_inference(context: str, error_count: int) -> str:
    """Pistas para preguntas que requieren inferencia"""
    text, question = _extract_text_and_question(context)

    if error_count == 1:
        return (
            "🤔 <b>Haz una inferencia:</b><br>"
            "La respuesta no está escrita directamente en el texto.<br>"
            "Usa lo que leíste y lo que ya sabes para deducir la respuesta."
        )
    elif error_count == 2:
        return (
            "🤔 <b>Piensa:</b><br>"
            "¿Qué pistas te da el texto?<br>"
            "Combina lo que dice el texto con tu conocimiento para llegar a una conclusión."
        )
    else:
        return (
            "🤔 <b>Razona:</b><br>"
            "Aunque no esté escrito explícitamente, el texto te da información suficiente.<br>"
            "Lee de nuevo y pregúntate: ¿Qué puedo concluir con esta información?"
        )

# ═══════════════════════════════════════════════════════════════
# PISTAS PARA COMPRENSIÓN GENERAL
# ═══════════════════════════════════════════════════════════════

def _hint_comprehension(context: str, error_count: int) -> str:
    """Pistas genéricas de comprensión"""
    text, question = _extract_text_and_question(context)

    if error_count == 1:
        return (
            "📝 <b>Lee con atención:</b><br>"
            "Vuelve a leer la pregunta y busca la respuesta en el texto.<br>"
            "Tómate tu tiempo para pensar."
        )
    elif error_count == 2:
        return (
            "📝 <b>Estrategia:</b><br>"
            "1. Lee la pregunta dos veces<br>"
            "2. Busca en el texto la parte que habla sobre eso<br>"
            "3. Responde con tus propias palabras"
        )
    else:
        return (
            "📝 <b>Sigue estos pasos:</b><br>"
            "1. Lee el texto completo otra vez<br>"
            "2. Identifica la información que responde la pregunta<br>"
            "3. Formula tu respuesta de manera clara y completa"
        )

# ═══════════════════════════════════════════════════════════════
# PISTAS DE FINALIZACIÓN
# ═══════════════════════════════════════════════════════════════

def _hint_complete(context: str, error_count: int) -> str:
    """Mensaje de finalización"""
    return (
        "🎉 <b>¡Excelente trabajo!</b><br>"
        "Has completado este ejercicio de comprensión lectora.<br>"
        "Sigue practicando para mejorar tu lectura."
    )

# ═══════════════════════════════════════════════════════════════
# PISTAS DE ERROR
# ═══════════════════════════════════════════════════════════════

def _hint_error(context: str, error_count: int) -> str:
    """Mensaje de error en el formato"""
    return (
        "⚠️ <b>Formato incorrecto:</b><br>"
        "Verifica que el ejercicio tenga el formato correcto.<br>"
        "Debe incluir un texto y preguntas de comprensión."
    )

# ═══════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL DE ROUTING
# ═══════════════════════════════════════════════════════════════

def get_hint(hint_type: str, error_count: int, context: str = "", answer: str = "") -> str:
    """
    Función principal para obtener pistas de lectura.

    Args:
        hint_type: Tipo de pista (read_intro, read_main_idea, read_detail, etc.)
        error_count: Número de errores cometidos
        context: Contexto del ejercicio (texto|||pregunta)
        answer: Respuesta del estudiante (no usado actualmente)

    Returns:
        str: Pista en formato HTML
    """
    # Eliminar prefijo "read_" si existe
    hint_key = hint_type.replace("read_", "") if hint_type.startswith("read_") else hint_type

    hint_functions = {
        "intro": _hint_intro,
        "main_idea": _hint_main_idea,
        "detail": _hint_detail,
        "vocabulary": _hint_vocabulary,
        "inference": _hint_inference,
        "comprehension": _hint_comprehension,
        "complete": _hint_complete,
        "error": _hint_error
    }

    hint_func = hint_functions.get(hint_key, _hint_comprehension)

    try:
        return hint_func(context, error_count)
    except Exception as e:
        print(f"[HINTS_READING] ⚠️ Error generando pista {hint_type}: {e}")
        return _hint_comprehension(context, error_count)
