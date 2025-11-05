# -*- coding: utf-8 -*-
"""
text_generator.py
---------------------------------
Generador de textos de lectura apropiados para cada nivel educativo.
Usa GPT-4 para generar textos adaptados al currículo LOMLOE de España.
"""

import os
import logging
from typing import Optional
from openai import OpenAI, OpenAIError

logger = logging.getLogger("tutorin.text_generator")

# Cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Configuración por nivel (1º a 6º de Primaria)
LEVEL_CONFIG = {
    "1": {
        "words": 80,
        "complexity": "muy simple",
        "sentences": "oraciones muy cortas (5-8 palabras)",
        "vocabulary": "vocabulario básico y cotidiano",
        "description": "1º de Primaria (6-7 años)"
    },
    "2": {
        "words": 120,
        "complexity": "simple",
        "sentences": "oraciones cortas (8-12 palabras)",
        "vocabulary": "vocabulario sencillo",
        "description": "2º de Primaria (7-8 años)"
    },
    "3": {
        "words": 150,
        "complexity": "moderada",
        "sentences": "oraciones de longitud media (10-15 palabras)",
        "vocabulary": "vocabulario apropiado con algunas palabras nuevas",
        "description": "3º de Primaria (8-9 años)"
    },
    "4": {
        "words": 200,
        "complexity": "normal",
        "sentences": "oraciones variadas (12-18 palabras)",
        "vocabulary": "vocabulario variado y enriquecedor",
        "description": "4º de Primaria (9-10 años)"
    },
    "5": {
        "words": 250,
        "complexity": "elaborada",
        "sentences": "oraciones complejas pero comprensibles (15-20 palabras)",
        "vocabulary": "vocabulario amplio con términos específicos",
        "description": "5º de Primaria (10-11 años)"
    },
    "6": {
        "words": 300,
        "complexity": "compleja",
        "sentences": "oraciones complejas y estructuradas (18-25 palabras)",
        "vocabulary": "vocabulario rico y diverso",
        "description": "6º de Primaria (11-12 años)"
    }
}


async def generate_text_with_gpt4(
    topic: str,
    level: str = "3"
) -> str:
    """
    Genera un texto de lectura apropiado para el nivel educativo.

    Args:
        topic: Tema del texto (ej: "dinosaurios", "espacio", "deportes")
        level: Nivel educativo ("1" a "6")

    Returns:
        Texto generado

    Raises:
        OpenAIError: Si hay error en la API de OpenAI
        ValueError: Si el nivel no es válido
    """
    # Validar nivel
    if level not in LEVEL_CONFIG:
        logger.warning(f"⚠️ Nivel {level} no válido, usando nivel 3 por defecto")
        level = "3"

    config = LEVEL_CONFIG[level]

    # Temas predefinidos (mejorar el prompt si es uno de estos)
    topic_enhancements = {
        "dinosaurios": "los dinosaurios, sus características y su extinción",
        "deportes": "deportes populares, sus reglas y beneficios",
        "espacio": "el sistema solar, planetas y exploración espacial",
        "animales": "animales fascinantes, sus hábitats y comportamientos",
        "naturaleza": "la naturaleza, ecosistemas y medio ambiente",
        "sorpréndeme": "un tema fascinante e interesante para niños"
    }

    enhanced_topic = topic_enhancements.get(topic.lower(), topic)

    prompt = f"""Eres Tutorín, un profesor virtual que crea textos educativos para estudiantes de Primaria en España (currículo LOMLOE).

NIVEL: {config['description']}

TEMA: {enhanced_topic}

REQUISITOS:
1. Longitud: aproximadamente {config['words']} palabras
2. Estructura: 2-3 párrafos bien organizados
3. Complejidad: {config['complexity']}
4. Oraciones: {config['sentences']}
5. Vocabulario: {config['vocabulary']}
6. Lenguaje: español de España (no usar americanismos)
7. Tono: educativo pero ameno e interesante
8. Contenido: información verídica y apropiada para la edad

IMPORTANTE:
- Escribe un texto informativo y educativo
- Incluye datos interesantes que capten la atención
- Usa un estilo narrativo claro y directo
- NO incluyas título ni preguntas en el texto
- NO uses formato markdown ni asteriscos
- Escribe SOLO el texto de lectura, sin prólogo ni introducción

Genera el texto ahora:"""

    try:
        logger.info(f"🤖 Generando texto sobre '{topic}' para nivel {level}...")

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un profesor experto en crear textos educativos para Primaria."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,  # Un poco más de creatividad
            max_tokens=800
        )

        # Extraer contenido
        text = response.choices[0].message.content.strip()

        # Limpiar posibles marcadores
        if text.startswith("**") or text.startswith("#"):
            # Remover títulos markdown
            lines = text.split('\n')
            text = '\n'.join([line for line in lines if not line.startswith('#') and not (line.startswith('**') and line.endswith('**'))])
            text = text.strip()

        # Validar longitud mínima
        word_count = len(text.split())
        if word_count < 50:
            logger.error(f"❌ Texto demasiado corto: {word_count} palabras")
            raise ValueError("El texto generado es demasiado corto")

        logger.info(f"✅ Texto generado correctamente ({word_count} palabras)")
        return text

    except OpenAIError as e:
        logger.error(f"❌ Error de OpenAI API: {e}")
        raise

    except Exception as e:
        logger.error(f"❌ Error inesperado generando texto: {e}")
        raise


def get_available_topics() -> list:
    """
    Devuelve lista de temas predefinidos disponibles.
    """
    return [
        {"id": "dinosaurios", "name": "🦖 Dinosaurios", "emoji": "🦖"},
        {"id": "deportes", "name": "⚽ Deportes", "emoji": "⚽"},
        {"id": "espacio", "name": "🚀 Espacio", "emoji": "🚀"},
        {"id": "animales", "name": "🐕 Animales", "emoji": "🐕"},
        {"id": "naturaleza", "name": "🌍 Naturaleza", "emoji": "🌍"},
        {"id": "sorpréndeme", "name": "✨ Sorpréndeme", "emoji": "✨"}
    ]


def get_available_levels() -> list:
    """
    Devuelve lista de niveles disponibles.
    """
    return [
        {"id": "1", "name": "1º Primaria"},
        {"id": "2", "name": "2º Primaria"},
        {"id": "3", "name": "3º Primaria"},
        {"id": "4", "name": "4º Primaria"},
        {"id": "5", "name": "5º Primaria"},
        {"id": "6", "name": "6º Primaria"}
    ]
