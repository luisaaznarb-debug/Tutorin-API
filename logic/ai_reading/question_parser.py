# -*- coding: utf-8 -*-
"""
question_parser.py
---------------------------------
Parser de preguntas de comprensión lectora.
Detecta múltiples formatos y clasifica tipos de preguntas.
"""

import re
from typing import List, Dict, Any


def _detect_question_type(question: str) -> str:
    """
    Detecta el tipo de pregunta según palabras clave.

    Tipos:
    - main_idea: idea principal, tema, resumen
    - vocabulary: significado, definición
    - inference: por qué, deduce, opinas, piensas
    - detail: cuándo, dónde, quién, cuántos, cómo se llama
    - comprehension: por defecto
    """
    q_lower = question.lower()

    # Idea principal
    if any(keyword in q_lower for keyword in [
        "idea principal", "tema principal", "trata", "resumen",
        "idea central", "principalmente", "tema del texto"
    ]):
        return "main_idea"

    # Vocabulario
    if any(keyword in q_lower for keyword in [
        "significa", "significado", "quiere decir", "definición",
        "qué es", "a qué se refiere", "se entiende por"
    ]):
        return "vocabulary"

    # Inferencia
    if any(keyword in q_lower for keyword in [
        "por qué", "porque", "crees que", "opinas", "piensas",
        "deduce", "infiere", "concluye", "razón", "causa"
    ]):
        return "inference"

    # Detalle
    if any(keyword in q_lower for keyword in [
        "cuándo", "cuando", "dónde", "donde", "quién", "quien",
        "cuántos", "cuantos", "cuántas", "cuantas",
        "cómo se llama", "como se llama", "nombre de"
    ]):
        return "detail"

    # Por defecto
    return "comprehension"


def parse_questions(text: str) -> List[Dict[str, Any]]:
    """
    Parsea preguntas de un texto en múltiples formatos.

    Formatos soportados:
    - "1. ¿Pregunta?" o "1) ¿Pregunta?"
    - "a. ¿Pregunta?" o "a) ¿Pregunta?"
    - "• ¿Pregunta?" o "- ¿Pregunta?"
    - Una pregunta por línea terminando en "?"

    Args:
        text: Texto con preguntas

    Returns:
        Lista de diccionarios: [{"q": "...", "answer": "", "type": "..."}]
    """
    if not text or not text.strip():
        return []

    questions = []

    # Normalizar saltos de línea
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    lines = text.split('\n')

    # Patrones de numeración
    patterns = [
        r'^\s*(\d+)[.)\-:]\s*(.+)',      # 1. o 1) o 1- o 1:
        r'^\s*([a-zA-Z])[.)\-:]\s*(.+)', # a. o a) o a- o a:
        r'^\s*[•\-\*]\s*(.+)',            # • o - o *
        r'^\s*([IVX]+)[.)\-:]\s*(.+)',   # I. II. III. (números romanos)
    ]

    for line in lines:
        line = line.strip()

        # Ignorar líneas vacías o muy cortas
        if not line or len(line) < 5:
            continue

        question_text = None

        # Intentar parsear con patrones
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                # Tomar el último grupo (el texto de la pregunta)
                question_text = match.groups()[-1].strip()
                break

        # Si no matcheó ningún patrón pero termina en ?, es una pregunta
        if not question_text and line.endswith('?'):
            question_text = line

        # Si encontramos una pregunta válida
        if question_text:
            # Limpiar espacios extras
            question_text = ' '.join(question_text.split())

            # Detectar tipo
            q_type = _detect_question_type(question_text)

            questions.append({
                "q": question_text,
                "answer": "",
                "type": q_type
            })

    return questions


def validate_questions(questions: List[Dict[str, Any]]) -> bool:
    """
    Valida que las preguntas parseadas tengan sentido.

    Args:
        questions: Lista de preguntas parseadas

    Returns:
        True si las preguntas son válidas
    """
    if not questions:
        return False

    for q in questions:
        # Debe tener el campo 'q' no vacío
        if not q.get('q') or not q['q'].strip():
            return False

        # Debe tener al menos 10 caracteres
        if len(q['q']) < 10:
            return False

        # Debe terminar en ? o contener palabras interrogativas
        q_text = q['q'].lower()
        if not (q_text.endswith('?') or any(word in q_text for word in [
            'qué', 'que', 'cuál', 'cual', 'cómo', 'como',
            'quién', 'quien', 'dónde', 'donde', 'cuándo', 'cuando',
            'por qué', 'porque'
        ])):
            return False

    return True
