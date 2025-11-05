# -*- coding: utf-8 -*-
"""
answer_generator.py
---------------------------------
Generador de respuestas esperadas para preguntas de comprensión lectora.
Usa GPT-4 para generar respuestas basadas en el texto.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI, OpenAIError

logger = logging.getLogger("tutorin.answer_generator")

# Cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def generate_answers_for_questions(
    text: str,
    questions: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Genera respuestas esperadas para una lista de preguntas basadas en un texto.

    Args:
        text: Texto de lectura
        questions: Lista de preguntas [{"q": "...", "answer": "", "type": "..."}]

    Returns:
        Lista de preguntas con respuestas generadas

    Raises:
        OpenAIError: Si hay error en la API de OpenAI
    """
    if not questions:
        logger.warning("⚠️ No hay preguntas para generar respuestas")
        return []

    # Construir lista de preguntas para el prompt
    questions_list = "\n".join([
        f"{i+1}. {q['q']}" for i, q in enumerate(questions)
    ])

    prompt = f"""Eres Tutorín, un profesor virtual de Primaria experto en comprensión lectora.

TEXTO:
{text}

PREGUNTAS:
{questions_list}

Tu tarea es generar respuestas esperadas para cada pregunta basándote ÚNICAMENTE en el texto proporcionado.

INSTRUCCIONES:
1. Las respuestas deben ser concisas (1-2 oraciones máximo)
2. Usar lenguaje apropiado para estudiantes de Primaria
3. Basarse SOLO en la información del texto
4. Para preguntas de vocabulario, dar definiciones simples
5. Para preguntas de inferencia, proporcionar la conclusión lógica

Devuelve un JSON con este formato exacto:
{{
  "answers": [
    "respuesta a pregunta 1",
    "respuesta a pregunta 2",
    ...
  ]
}}

IMPORTANTE: Devuelve SOLO el JSON, sin texto adicional."""

    try:
        logger.info(f"🤖 Generando respuestas para {len(questions)} preguntas...")

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un profesor experto en comprensión lectora. Respondes en formato JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=1000
        )

        # Extraer contenido
        content = response.choices[0].message.content.strip()

        # Limpiar posibles marcadores de código
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()

        # Parsear JSON
        result = json.loads(content)
        answers = result.get("answers", [])

        if len(answers) != len(questions):
            logger.warning(
                f"⚠️ Se esperaban {len(questions)} respuestas, "
                f"se recibieron {len(answers)}"
            )

        # Agregar respuestas a las preguntas
        for i, q in enumerate(questions):
            if i < len(answers):
                q["answer"] = answers[i]
            else:
                q["answer"] = ""

        logger.info(f"✅ Respuestas generadas correctamente")
        return questions

    except json.JSONDecodeError as e:
        logger.error(f"❌ Error parseando JSON de GPT-4: {e}")
        logger.error(f"Contenido recibido: {content[:200]}...")
        # Devolver preguntas sin respuestas
        return questions

    except OpenAIError as e:
        logger.error(f"❌ Error de OpenAI API: {e}")
        raise

    except Exception as e:
        logger.error(f"❌ Error inesperado generando respuestas: {e}")
        raise


async def generate_answer_for_single_question(
    text: str,
    question: str,
    question_type: str = "comprehension"
) -> str:
    """
    Genera una respuesta para una sola pregunta.

    Args:
        text: Texto de lectura
        question: Pregunta
        question_type: Tipo de pregunta

    Returns:
        Respuesta generada
    """
    try:
        questions = [{"q": question, "answer": "", "type": question_type}]
        result = await generate_answers_for_questions(text, questions)

        if result and len(result) > 0:
            return result[0].get("answer", "")

        return ""

    except Exception as e:
        logger.error(f"❌ Error generando respuesta única: {e}")
        return ""
