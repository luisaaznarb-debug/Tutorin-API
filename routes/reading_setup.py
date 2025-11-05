# -*- coding: utf-8 -*-
"""
routes/reading_setup.py
---------------------------------
Endpoints para configurar ejercicios de comprensión lectora.
Permite 3 flujos: texto manual, generación automática, o desde foto.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uuid
import json
import logging
import base64

from logic.ai_reading.question_parser import parse_questions, validate_questions
from logic.ai_reading.answer_generator import generate_answers_for_questions
from logic.ai_reading.text_generator import generate_text_with_gpt4, get_available_topics, get_available_levels
from logic.ai_reading.question_generator import generate_questions_with_gpt4, validate_generated_questions
from logic.ai_reading.photo_parser import parse_reading_from_photo, validate_extracted_text
import db

logger = logging.getLogger("tutorin.reading_setup")

router = APIRouter()

# ═══════════════════════════════════════════════════════════════
# MODELOS DE DATOS
# ═══════════════════════════════════════════════════════════════

class SetupReadingRequest(BaseModel):
    """Request para configurar ejercicio con texto manual"""
    text: str = Field(..., min_length=50, description="Texto para leer (mínimo 50 caracteres)")
    questions_text: Optional[str] = Field(None, description="Preguntas del libro (opcional)")
    level: Optional[str] = Field("3", description="Nivel educativo (1-6)")


class GenerateReadingRequest(BaseModel):
    """Request para generar ejercicio automático"""
    topic: str = Field(..., description="Tema del texto")
    level: str = Field("3", description="Nivel educativo (1-6)")


class ReadingExerciseResponse(BaseModel):
    """Response con ejercicio de lectura"""
    exercise_id: str
    exercise: Dict[str, Any]
    message: str


# ═══════════════════════════════════════════════════════════════
# FUNCIONES AUXILIARES
# ═══════════════════════════════════════════════════════════════

def _validate_text(text: str) -> tuple[bool, str]:
    """
    Valida que el texto tenga al menos 50 palabras.
    Returns: (is_valid, error_message)
    """
    if not text or not text.strip():
        return False, "El texto no puede estar vacío"

    word_count = len(text.split())
    if word_count < 10:
        return False, f"El texto es demasiado corto ({word_count} palabras). Necesita al menos 10 palabras."

    return True, ""


def _create_exercise(text: str, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Crea un ejercicio en el formato esperado por reading_engine.py
    """
    return {
        "text": text,
        "questions": questions
    }


# ═══════════════════════════════════════════════════════════════
# ENDPOINT 1: CONFIGURAR CON TEXTO MANUAL
# ═══════════════════════════════════════════════════════════════

@router.post("/setup", response_model=ReadingExerciseResponse)
async def setup_reading_exercise(request: SetupReadingRequest):
    """
    Configura un ejercicio de lectura con texto proporcionado por el usuario.

    Flujos:
    1. Si viene questions_text: parsear y generar respuestas con GPT-4
    2. Si NO viene questions_text: generar preguntas automáticamente con GPT-4
    """
    try:
        # Validar texto
        is_valid, error_msg = _validate_text(request.text)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        questions = []

        # CASO 1: Usuario proporciona preguntas
        if request.questions_text and request.questions_text.strip():
            logger.info("📝 Usuario proporcionó preguntas, parseando...")

            # Parsear preguntas
            questions = parse_questions(request.questions_text)

            if not questions:
                raise HTTPException(
                    status_code=400,
                    detail="No se pudieron detectar preguntas válidas en el texto proporcionado. "
                           "Asegúrate de que las preguntas estén numeradas o en líneas separadas."
                )

            # Validar preguntas
            if not validate_questions(questions):
                raise HTTPException(
                    status_code=400,
                    detail="Las preguntas detectadas no tienen el formato correcto. "
                           "Deben ser preguntas completas que terminen en '?'."
                )

            logger.info(f"✅ {len(questions)} preguntas parseadas correctamente")

            # Generar respuestas con GPT-4
            logger.info("🤖 Generando respuestas esperadas con GPT-4...")
            questions = await generate_answers_for_questions(request.text, questions)

        # CASO 2: Generar preguntas automáticamente
        else:
            logger.info("🤖 Generando preguntas automáticamente con GPT-4...")
            questions = await generate_questions_with_gpt4(request.text, request.level)

            if not validate_generated_questions(questions):
                raise HTTPException(
                    status_code=500,
                    detail="Error al generar preguntas automáticamente. Inténtalo de nuevo."
                )

        # Crear ejercicio
        exercise = _create_exercise(request.text, questions)

        # Generar ID único
        exercise_id = str(uuid.uuid4())

        # Guardar en DB
        db.save_reading_exercise(exercise_id, exercise)

        logger.info(f"✅ Ejercicio creado: {exercise_id} con {len(questions)} preguntas")

        return ReadingExerciseResponse(
            exercise_id=exercise_id,
            exercise=exercise,
            message=f"Ejercicio creado con {len(questions)} preguntas"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error configurando ejercicio: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al configurar el ejercicio: {str(e)}"
        )


# ═══════════════════════════════════════════════════════════════
# ENDPOINT 2: GENERAR EJERCICIO AUTOMÁTICO
# ═══════════════════════════════════════════════════════════════

@router.post("/generate", response_model=ReadingExerciseResponse)
async def generate_reading_exercise(request: GenerateReadingRequest):
    """
    Genera un ejercicio completo (texto + preguntas) automáticamente con GPT-4.
    """
    try:
        # Validar nivel
        if request.level not in ["1", "2", "3", "4", "5", "6"]:
            raise HTTPException(
                status_code=400,
                detail="El nivel debe ser entre 1 y 6"
            )

        logger.info(f"🤖 Generando ejercicio sobre '{request.topic}' para nivel {request.level}...")

        # 1. Generar texto con GPT-4
        logger.info("📝 Generando texto...")
        text = await generate_text_with_gpt4(request.topic, request.level)

        if not text or len(text.split()) < 50:
            raise HTTPException(
                status_code=500,
                detail="El texto generado es demasiado corto. Inténtalo de nuevo."
            )

        # 2. Generar preguntas con GPT-4
        logger.info("❓ Generando preguntas...")
        questions = await generate_questions_with_gpt4(text, request.level)

        if not validate_generated_questions(questions):
            raise HTTPException(
                status_code=500,
                detail="Error al generar preguntas. Inténtalo de nuevo."
            )

        # Crear ejercicio
        exercise = _create_exercise(text, questions)

        # Generar ID único
        exercise_id = str(uuid.uuid4())

        # Guardar en DB
        db.save_reading_exercise(exercise_id, exercise)

        logger.info(f"✅ Ejercicio generado: {exercise_id}")

        return ReadingExerciseResponse(
            exercise_id=exercise_id,
            exercise=exercise,
            message=f"Ejercicio generado sobre '{request.topic}' con {len(questions)} preguntas"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error generando ejercicio: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar el ejercicio: {str(e)}"
        )


# ═══════════════════════════════════════════════════════════════
# ENDPOINT 3: EJERCICIO DESDE FOTO
# ═══════════════════════════════════════════════════════════════

@router.post("/from-photo", response_model=ReadingExerciseResponse)
async def reading_from_photo(
    file: UploadFile = File(...),
    level: Optional[str] = Form("3")
):
    """
    Crea un ejercicio de lectura desde una foto usando GPT-4 Vision.

    Flujo:
    1. Extraer texto y preguntas de la foto con GPT-4 Vision
    2. Si no hay preguntas, generarlas automáticamente
    3. Si las preguntas no tienen respuestas, generarlas
    """
    try:
        # Validar que sea una imagen
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="El archivo debe ser una imagen (JPG, PNG, etc.)"
            )

        # Leer imagen
        image_bytes = await file.read()

        # Convertir a base64
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')

        logger.info("📸 Procesando foto con GPT-4 Vision...")

        # Extraer texto y preguntas
        result = await parse_reading_from_photo(image_b64)

        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=result["message"]
            )

        text = result["text"]
        questions = result["questions"]

        # Validar texto mínimo
        if not await validate_extracted_text(text):
            raise HTTPException(
                status_code=400,
                detail="El texto extraído es demasiado corto o no es adecuado. "
                       "Por favor, sube una foto más clara con un texto de al menos 50 palabras."
            )

        # Si no hay preguntas, generarlas
        if not questions or len(questions) == 0:
            logger.info("🤖 No se encontraron preguntas, generándolas automáticamente...")
            questions = await generate_questions_with_gpt4(text, level)

        # Si las preguntas no tienen respuestas, generarlas
        needs_answers = any(not q.get("answer") or not q["answer"].strip() for q in questions)
        if needs_answers:
            logger.info("🤖 Generando respuestas para las preguntas...")
            questions = await generate_answers_for_questions(text, questions)

        # Crear ejercicio
        exercise = _create_exercise(text, questions)

        # Generar ID único
        exercise_id = str(uuid.uuid4())

        # Guardar en DB
        db.save_reading_exercise(exercise_id, exercise)

        logger.info(f"✅ Ejercicio creado desde foto: {exercise_id}")

        return ReadingExerciseResponse(
            exercise_id=exercise_id,
            exercise=exercise,
            message=result["message"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error procesando foto: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar la foto: {str(e)}"
        )


# ═══════════════════════════════════════════════════════════════
# ENDPOINTS INFORMATIVOS
# ═══════════════════════════════════════════════════════════════

@router.get("/topics")
async def get_topics():
    """Devuelve lista de temas disponibles para generación automática"""
    return {"topics": get_available_topics()}


@router.get("/levels")
async def get_levels():
    """Devuelve lista de niveles educativos disponibles"""
    return {"levels": get_available_levels()}
