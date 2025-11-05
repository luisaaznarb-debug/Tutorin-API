# -*- coding: utf-8 -*-
"""
routes/analyze_image.py
---------------------------------
Endpoint para analizar imágenes de ejercicios usando GPT-4 Vision
✅ CORREGIDO: Mejor detección de fracciones y formato simple
"""

from fastapi import APIRouter, UploadFile, Form, HTTPException
from typing import Optional
import base64
import os
from openai import OpenAI

router = APIRouter()

# Inicializar cliente de OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@router.post("/image")
async def analyze_image(
    file: UploadFile,
    cycle: Optional[str] = Form("c2")
):
    """
    Analiza una imagen subida por el alumno usando GPT-4 Vision.
    Extrae el ejercicio matemático y devuelve una pregunta estructurada.
    """
    try:
        # Leer la imagen
        image_bytes = await file.read()
        
        # Validar que sea una imagen
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")
        
        # Convertir a base64
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Determinar el nivel educativo
        cycle_info = {
            "c1": "1º-2º de Primaria (edades 6-8)",
            "c2": "3º-4º de Primaria (edades 8-10)",
            "c3": "5º-6º de Primaria (edades 10-12)"
        }
        nivel = cycle_info.get(cycle, "Primaria")
        
        # Llamar a GPT-4 Vision con prompt mejorado
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": f"""Eres Tutorín, un profesor virtual de Primaria experto en analizar ejercicios escritos a mano o impresos.

Tu tarea es:
1. Identificar el ejercicio matemático o de lengua en la imagen
2. Extraer los números, operaciones y texto relevante
3. Devolver el ejercicio en formato texto claro y SIMPLE

El alumno está en {nivel}.

INSTRUCCIONES IMPORTANTES:
- Si encuentras fracciones, escríbelas como 3/4 (NO como \\frac{{3}}{{4}})
- Si encuentras operaciones, escríbelas simples: 3/4 + 1/2
- Si hay varios ejercicios, devuelve solo el primero
- Si no hay ejercicio claro, di "No he podido identificar un ejercicio en la imagen"
- NO añadas explicaciones ni contexto, solo transcribe el ejercicio
- NO inventes problemas de palabras si solo ves números y operaciones

EJEMPLOS:
- Si ves fracciones: "3/4 + 1/2"
- Si ves sumas: "234 + 567"
- Si ves división: "864 ÷ 24"

NO resuelvas el ejercicio, solo transcríbelo."""
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "¿Qué ejercicio hay en esta imagen?"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_b64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500,
            temperature=0.3
        )
        
        # Extraer respuesta
        extracted_text = response.choices[0].message.content.strip()
        
        # Si no se detectó ejercicio
        if "no he podido" in extracted_text.lower() or "no encuentro" in extracted_text.lower():
            return {
                "success": False,
                "message": "📸 He visto la imagen, pero no he podido identificar un ejercicio claro. ¿Puedes escribirlo tú o subir otra foto más nítida?",
                "question": None,
                "exercise_id": None
            }
        
        # Si se detectó ejercicio
        return {
            "success": True,
            "message": f"📸 He leído: **{extracted_text}** ¿Lo resolvemos paso a paso?",
            "question": extracted_text,
            "exercise_id": None
        }
        
    except Exception as e:
        print(f"❌ Error al analizar imagen: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar la imagen: {str(e)}"
        )