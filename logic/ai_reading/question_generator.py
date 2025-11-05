# -*- coding: utf-8 -*-
"""
question_generator.py
---------------------------------
Generador de preguntas de comprensión lectora.
Usa GPT-4 para generar exactamente 4 preguntas de diferentes tipos.
"""

import os
import json
import logging
from typing import List, Dict, Any
from openai import OpenAI, OpenAIError

logger = logging.getLogger("tutorin.question_generator")

# Cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def generate_questions_with_gpt4(
    text: str,
    level: str = "3"
) -> List[Dict[str, Any]]:
    """
    Genera exactamente 4 preguntas de comprensión lectora de diferentes tipos.

    Tipos de preguntas:
    1. DETALLE: información explícita en el texto
    2. IDEA PRINCIPAL: tema central del texto
    3. VOCABULARIO: significado de palabras
    4. INFERENCIA: conclusiones o deducciones

    Args:
        text: Texto de lectura
        level: Nivel educativo ("1" a "6")

    Returns:
        Lista de 4 preguntas con respuestas: [{"q": "...", "answer": "...", "type": "..."}]

    Raises:
        OpenAIError: Si hay error en la API de OpenAI
    """
    # Adaptar complejidad según nivel
    level_hints = {
        "1": "preguntas muy simples y directas",
        "2": "preguntas sencillas",
        "3": "preguntas claras pero que requieran cierta reflexión",
        "4": "preguntas que requieran comprensión profunda",
        "5": "preguntas que estimulen el pensamiento crítico",
        "6": "preguntas desafiantes que fomenten el análisis"
    }

    complexity_hint = level_hints.get(level, level_hints["3"])

    prompt = f"""Eres Tutorín, un profesor virtual experto en comprensión lectora para Primaria.

TEXTO:
{text}

Tu tarea es generar EXACTAMENTE 4 preguntas de comprensión lectora sobre este texto, una de cada tipo:

1. DETALLE (detail): Pregunta sobre información específica que está explícitamente en el texto
   - Usa palabras como: ¿Cuándo?, ¿Dónde?, ¿Quién?, ¿Cuántos?, ¿Cómo se llama?

2. IDEA PRINCIPAL (main_idea): Pregunta sobre el tema central del texto
   - Usa palabras como: ¿De qué trata?, ¿Cuál es la idea principal?, ¿Qué tema?

3. VOCABULARIO (vocabulary): Pregunta sobre el significado de una palabra del texto
   - Usa palabras como: ¿Qué significa?, ¿Qué quiere decir?

4. INFERENCIA (inference): Pregunta que requiere deducir o concluir algo no explícito
   - Usa palabras como: ¿Por qué?, ¿Qué crees que?, ¿Por qué razón?

REQUISITOS:
- Nivel educativo: {level}º de Primaria
- Complejidad: {complexity_hint}
- Respuestas: concisas (1-2 oraciones), basadas SOLO en el texto
- Lenguaje: español de España, apropiado para la edad
- Formato: las preguntas deben terminar con "?"

Devuelve un JSON con este formato EXACTO:
{{
  "questions": [
    {{"type": "detail", "q": "pregunta de detalle", "answer": "respuesta"}},
    {{"type": "main_idea", "q": "pregunta de idea principal", "answer": "respuesta"}},
    {{"type": "vocabulary", "q": "pregunta de vocabulario", "answer": "respuesta"}},
    {{"type": "inference", "q": "pregunta de inferencia", "answer": "respuesta"}}
  ]
}}

IMPORTANTE: Devuelve SOLO el JSON, sin texto adicional."""

    try:
        logger.info(f"🤖 Generando 4 preguntas para nivel {level}...")

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un profesor experto en crear preguntas de comprensión lectora. Respondes en formato JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5,
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
        questions = result.get("questions", [])

        # Validar que haya exactamente 4 preguntas
        if len(questions) != 4:
            logger.warning(
                f"⚠️ Se esperaban 4 preguntas, se recibieron {len(questions)}"
            )

        # Validar tipos
        expected_types = {"detail", "main_idea", "vocabulary", "inference"}
        for q in questions:
            if "type" not in q or q["type"] not in expected_types:
                logger.warning(f"⚠️ Tipo de pregunta inválido: {q.get('type')}")
                q["type"] = "comprehension"

            # Asegurar campos necesarios
            if "q" not in q:
                q["q"] = ""
            if "answer" not in q:
                q["answer"] = ""

        logger.info(f"✅ {len(questions)} preguntas generadas correctamente")
        return questions

    except json.JSONDecodeError as e:
        logger.error(f"❌ Error parseando JSON de GPT-4: {e}")
        logger.error(f"Contenido recibido: {content[:200]}...")
        raise ValueError("No se pudo parsear la respuesta de GPT-4")

    except OpenAIError as e:
        logger.error(f"❌ Error de OpenAI API: {e}")
        raise

    except Exception as e:
        logger.error(f"❌ Error inesperado generando preguntas: {e}")
        raise


def validate_generated_questions(questions: List[Dict[str, Any]]) -> bool:
    """
    Valida que las preguntas generadas sean correctas.

    Args:
        questions: Lista de preguntas generadas

    Returns:
        True si las preguntas son válidas
    """
    if not questions or len(questions) == 0:
        return False

    required_fields = ["q", "answer", "type"]
    valid_types = {"detail", "main_idea", "vocabulary", "inference", "comprehension"}

    for q in questions:
        # Verificar campos requeridos
        for field in required_fields:
            if field not in q or not q[field]:
                logger.error(f"❌ Campo faltante o vacío: {field}")
                return False

        # Verificar tipo válido
        if q["type"] not in valid_types:
            logger.error(f"❌ Tipo inválido: {q['type']}")
            return False

        # Verificar que la pregunta termine en ?
        if not q["q"].strip().endswith("?"):
            logger.warning(f"⚠️ Pregunta sin '?': {q['q']}")

    return True
