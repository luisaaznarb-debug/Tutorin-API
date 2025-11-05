# -*- coding: utf-8 -*-
"""
photo_parser.py
---------------------------------
Parser de fotos de ejercicios de lectura.
Usa GPT-4 Vision para extraer texto y preguntas de imágenes.
"""

import os
import json
import logging
from typing import Dict, Any, List
from openai import OpenAI, OpenAIError

logger = logging.getLogger("tutorin.photo_parser")

# Cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def parse_reading_from_photo(image_base64: str) -> Dict[str, Any]:
    """
    Extrae texto y preguntas de una foto de ejercicio de lectura.

    Args:
        image_base64: Imagen en formato base64 (sin el prefijo data:image/...)

    Returns:
        Diccionario con formato:
        {
            "text": "texto extraído",
            "questions": [
                {"q": "pregunta", "answer": "", "type": "comprensión"},
                ...
            ],
            "success": True/False,
            "message": "mensaje informativo"
        }

    Raises:
        OpenAIError: Si hay error en la API de OpenAI
    """
    prompt = """Eres Tutorín, un profesor virtual experto en analizar ejercicios de lectura en libros de texto.

Tu tarea es extraer:
1. El TEXTO PRINCIPAL de lectura (si hay)
2. Las PREGUNTAS de comprensión lectora (si hay)

INSTRUCCIONES:
- Transcribe el texto tal como aparece, respetando la ortografía y puntuación
- Identifica todas las preguntas (pueden estar numeradas, con letras, con viñetas, etc.)
- Si NO hay texto de lectura claro, indica que no se encontró
- Si NO hay preguntas, deja la lista vacía
- NO inventes ni agregues nada que no esté en la imagen
- NO respondas las preguntas, solo extráelas

Devuelve un JSON con este formato EXACTO:
{
  "text": "el texto principal de lectura (o cadena vacía si no hay)",
  "questions": [
    "pregunta 1",
    "pregunta 2",
    ...
  ]
}

IMPORTANTE:
- Si la imagen NO contiene texto de lectura, pon "text": ""
- Si NO hay preguntas, pon "questions": []
- Devuelve SOLO el JSON, sin texto adicional"""

    try:
        logger.info("📸 Analizando foto de ejercicio de lectura...")

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un profesor experto en extraer texto e información de imágenes. Respondes en formato JSON."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=2000,
            temperature=0.1  # Baja temperatura para máxima precisión
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
        text = result.get("text", "").strip()
        questions_raw = result.get("questions", [])

        # Validar que se extrajo algo
        if not text and not questions_raw:
            logger.warning("⚠️ No se pudo extraer texto ni preguntas de la imagen")
            return {
                "text": "",
                "questions": [],
                "success": False,
                "message": "No se pudo identificar texto de lectura ni preguntas en la imagen. Asegúrate de que la foto sea clara y contenga un ejercicio de lectura."
            }

        # Validar texto mínimo
        if text and len(text.split()) < 10:
            logger.warning(f"⚠️ Texto muy corto: {len(text.split())} palabras")
            return {
                "text": text,
                "questions": [],
                "success": False,
                "message": "El texto extraído es demasiado corto. Por favor, sube una foto más clara del ejercicio completo."
            }

        # Convertir preguntas a formato estándar
        questions = []
        for i, q_text in enumerate(questions_raw):
            if isinstance(q_text, str) and q_text.strip():
                # Detectar tipo básico de pregunta
                q_lower = q_text.lower()
                if "idea principal" in q_lower or "trata" in q_lower:
                    q_type = "main_idea"
                elif "significa" in q_lower or "definición" in q_lower:
                    q_type = "vocabulary"
                elif "por qué" in q_lower or "crees que" in q_lower:
                    q_type = "inference"
                elif any(word in q_lower for word in ["cuándo", "dónde", "quién", "cuántos"]):
                    q_type = "detail"
                else:
                    q_type = "comprehension"

                questions.append({
                    "q": q_text.strip(),
                    "answer": "",
                    "type": q_type
                })

        # Mensaje de éxito
        word_count = len(text.split()) if text else 0
        question_count = len(questions)

        success_message = f"✅ Detecté: {word_count} palabras"
        if question_count > 0:
            success_message += f", {question_count} pregunta{'s' if question_count != 1 else ''}"
        elif text:
            success_message += ". No se encontraron preguntas, las generaré automáticamente."

        logger.info(f"✅ {success_message}")

        return {
            "text": text,
            "questions": questions,
            "success": True,
            "message": success_message
        }

    except json.JSONDecodeError as e:
        logger.error(f"❌ Error parseando JSON de GPT-4 Vision: {e}")
        logger.error(f"Contenido recibido: {content[:200]}...")
        return {
            "text": "",
            "questions": [],
            "success": False,
            "message": "Error al procesar la imagen. Por favor, inténtalo de nuevo."
        }

    except OpenAIError as e:
        logger.error(f"❌ Error de OpenAI API: {e}")
        raise

    except Exception as e:
        logger.error(f"❌ Error inesperado procesando foto: {e}")
        raise


async def validate_extracted_text(text: str) -> bool:
    """
    Valida que el texto extraído sea adecuado para comprensión lectora.

    Args:
        text: Texto extraído

    Returns:
        True si el texto es válido
    """
    if not text or not text.strip():
        return False

    # Debe tener al menos 50 palabras
    word_count = len(text.split())
    if word_count < 50:
        logger.warning(f"⚠️ Texto muy corto: {word_count} palabras (mínimo 50)")
        return False

    # Debe tener al menos 2 oraciones
    sentence_count = text.count('.') + text.count('?') + text.count('!')
    if sentence_count < 2:
        logger.warning(f"⚠️ Muy pocas oraciones: {sentence_count}")
        return False

    return True
