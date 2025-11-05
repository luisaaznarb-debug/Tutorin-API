# -*- coding: utf-8 -*-
"""
app.py
----------------------------------
App Factory principal de Tutorín.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Routers principales
from routes.analyze_prompt import router as analyze_router
from routes.solve import router as solve_router
from routes.analyze_image import router as image_router  # ✅ LÍNEA NUEVA
from routes.reading_setup import router as reading_router  # ✅ Sistema de lectura

def create_app() -> FastAPI:
    app = FastAPI(
        title="Tutorín API",
        description="Backend educativo de Tutorín: análisis y resolución paso a paso.",
        version="1.0.0"
    )

    # CORS
    origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://tutorin.netlify.app",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ✅ AÑADIR: Middleware para asegurar UTF-8 en todas las respuestas
    @app.middleware("http")
    async def add_charset_to_content_type(request, call_next):
        response = await call_next(request)
        if "application/json" in response.headers.get("content-type", ""):
            response.headers["content-type"] = "application/json; charset=utf-8"
        return response

    # Rutas principales
    app.include_router(analyze_router, prefix="/analyze", tags=["Analyze"])
    app.include_router(solve_router, prefix="/solve", tags=["Solve"])
    app.include_router(image_router, prefix="/analyze", tags=["Image Analysis"])  # ✅ LÍNEA NUEVA
    app.include_router(reading_router, prefix="/reading", tags=["Reading"])  # ✅ Comprensión lectora

    @app.get("/")
    def root():
        return {
            "message": "👋 Hola, soy Tutorín API.",
            "status": "online",
            "routes": ["/analyze/text", "/analyze/image", "/solve", "/reading"]  # ✅ ACTUALIZADO
        }

    return app

app = create_app()