# 📖 Sistema de Comprensión Lectora - Tutorín

Sistema completo de comprensión lectora con generación automática de textos y preguntas mediante GPT-4.

## 🎯 Características

### 3 Flujos de Uso

1. **📝 Texto Manual sin Preguntas**
   - Usuario pega texto
   - GPT-4 genera 4 preguntas automáticamente (detalle, idea principal, vocabulario, inferencia)

2. **📖 Texto Manual con Preguntas**
   - Usuario pega texto y preguntas del libro
   - Sistema parsea preguntas en múltiples formatos
   - GPT-4 genera respuestas esperadas

3. **📸 Foto del Libro**
   - Usuario sube foto del ejercicio
   - GPT-4 Vision extrae texto y preguntas
   - Si no hay preguntas, las genera automáticamente

4. **🎲 Generación Automática**
   - Usuario selecciona tema y nivel
   - GPT-4 genera texto apropiado para el nivel
   - GPT-4 genera 4 preguntas de comprensión

## 🏗️ Arquitectura

### Backend (Python FastAPI)

```
logic/
├── ai_reading/
│   ├── __init__.py
│   ├── question_parser.py      # Parser de preguntas (múltiples formatos)
│   ├── answer_generator.py     # Generador de respuestas con GPT-4
│   ├── text_generator.py       # Generador de textos con GPT-4
│   ├── question_generator.py   # Generador de preguntas con GPT-4
│   └── photo_parser.py          # Parser de fotos con GPT-4 Vision
│
├── domains/lengua/
│   └── reading_engine.py        # Motor de ejercicios (ya existente)
│
└── ai_hints/
    └── hints_reading.py         # Sistema de pistas (ya existente)

routes/
└── reading_setup.py             # Endpoints REST

db.py                            # Funciones de DB agregadas
app.py                           # Router integrado
```

### Endpoints REST

#### `POST /reading/setup`
Configura ejercicio con texto manual.

```json
{
  "text": "Texto para leer...",
  "questions_text": "1. ¿Pregunta? (opcional)",
  "level": "3"
}
```

#### `POST /reading/generate`
Genera ejercicio automático.

```json
{
  "topic": "dinosaurios",
  "level": "3"
}
```

#### `POST /reading/from-photo`
Extrae ejercicio de foto (FormData).

#### `GET /reading/topics`
Lista de temas disponibles.

#### `GET /reading/levels`
Lista de niveles educativos.

## 📝 Formatos de Preguntas Soportados

El parser detecta automáticamente:

```
1. ¿Pregunta?        # Números con punto
1) ¿Pregunta?        # Números con paréntesis

a. ¿Pregunta?        # Letras con punto
a) ¿Pregunta?        # Letras con paréntesis

• ¿Pregunta?         # Viñetas
- ¿Pregunta?         # Guiones

¿Pregunta?           # Una pregunta por línea
```

## 🎓 Tipos de Preguntas

El sistema clasifica automáticamente:

- **`detail`**: Información explícita (cuándo, dónde, quién, cuántos)
- **`main_idea`**: Idea principal o tema central
- **`vocabulary`**: Significado de palabras
- **`inference`**: Deducciones y conclusiones (por qué, crees que)
- **`comprehension`**: Comprensión general (por defecto)

## 📊 Niveles Educativos

| Nivel | Curso | Palabras | Complejidad |
|-------|-------|----------|-------------|
| 1 | 1º Primaria | 80 | Muy simple |
| 2 | 2º Primaria | 120 | Simple |
| 3 | 3º Primaria | 150 | Moderada |
| 4 | 4º Primaria | 200 | Normal |
| 5 | 5º Primaria | 250 | Elaborada |
| 6 | 6º Primaria | 300 | Compleja |

## 🧪 Tests

```bash
# Ejecutar tests
python -m pytest tests/test_reading_system.py -v

# Tests específicos
pytest tests/test_reading_system.py::TestQuestionParser -v
```

### Cobertura de Tests

- ✅ Parseo de preguntas (múltiples formatos)
- ✅ Detección de tipos de preguntas
- ✅ Validación de preguntas
- ✅ Formato compatible con reading_engine
- ⏭️ Integración con OpenAI (requiere API key)

## 🔧 Configuración

### Variables de Entorno

```bash
OPENAI_API_KEY=sk-...
```

### Dependencias

Ya incluidas en `requirements.txt`:
- `openai` (cliente oficial)
- `fastapi`
- `python-multipart` (para upload de fotos)

## 📱 Integración con Frontend

Ver `READING_FRONTEND_INTEGRATION.md` para:
- Componentes React a crear
- Funciones de API
- Integración en `tutorin-dialog.js`
- Estilos CSS recomendados

## 🎨 UX Recomendada

### Flujo del Usuario

1. Usuario escribe "quiero practicar lectura"
2. Sistema muestra 3 opciones:
   - 🎲 Generar automático
   - 📖 Traigo mi texto
   - 📸 Subir foto
3. Usuario selecciona y configura
4. Sistema crea ejercicio
5. `reading_engine.py` guía el ejercicio paso a paso

### Mensajes de Loading

- "⏳ Generando texto sobre dinosaurios..."
- "⏳ Creando preguntas..."
- "📸 Extrayendo texto de la foto..."
- "🤖 Generando respuestas esperadas..."

## 🚀 Ejemplos de Uso

### Ejemplo 1: Texto Manual sin Preguntas

```python
# Usuario pega texto
POST /reading/setup
{
  "text": "Los dinosaurios fueron animales fascinantes que vivieron hace millones de años. Había muchos tipos diferentes, como el Tyrannosaurus Rex, que era carnívoro, y el Triceratops, que era herbívoro. Los dinosaurios se extinguieron hace 65 millones de años cuando un gran meteorito chocó contra la Tierra.",
  "level": "3"
}

# Sistema responde con 4 preguntas generadas
{
  "exercise_id": "...",
  "exercise": {
    "text": "Los dinosaurios...",
    "questions": [
      {"q": "¿Cuándo vivieron los dinosaurios?", "answer": "Hace millones de años", "type": "detail"},
      {"q": "¿Cuál es la idea principal del texto?", "answer": "Los dinosaurios...", "type": "main_idea"},
      {"q": "¿Qué significa herbívoro?", "answer": "Animal que come plantas", "type": "vocabulary"},
      {"q": "¿Por qué se extinguieron los dinosaurios?", "answer": "Por un meteorito", "type": "inference"}
    ]
  }
}
```

### Ejemplo 2: Generación Automática

```python
POST /reading/generate
{
  "topic": "dinosaurios",
  "level": "3"
}

# GPT-4 genera texto de ~150 palabras apropiado para 3º
# GPT-4 genera 4 preguntas variadas
```

### Ejemplo 3: Desde Foto

```python
POST /reading/from-photo
FormData:
  file: [imagen.jpg]
  level: "3"

# GPT-4 Vision extrae texto y preguntas
# Si no hay preguntas, las genera automáticamente
```

## ⚠️ Manejo de Errores

El sistema maneja:

- ✅ Texto muy corto (< 50 palabras)
- ✅ Preguntas inválidas
- ✅ Errores de OpenAI API (rate limit, timeout)
- ✅ Imágenes ilegibles
- ✅ JSON mal formado

Todos los errores devuelven mensajes amigables al usuario.

## 📈 Mejoras Futuras

- [ ] Cache de ejercicios generados
- [ ] Más temas predefinidos
- [ ] Soporte para otros idiomas
- [ ] Estadísticas de rendimiento del alumno
- [ ] Exportar ejercicios a PDF
- [ ] Modo offline con ejercicios pregenerados

## 🤝 Contribuir

Para agregar nuevos temas:
1. Editar `text_generator.py` → `topic_enhancements`
2. Actualizar `get_available_topics()`

Para agregar nuevos tipos de preguntas:
1. Editar `question_parser.py` → `_detect_question_type()`
2. Actualizar `hints_reading.py` con pistas específicas

## 📞 Soporte

Para problemas o preguntas:
- GitHub Issues
- Documentación: `/docs`
- Tests: `pytest tests/test_reading_system.py -v`

---

**✨ Sistema completamente funcional y listo para usar**

Backend: ✅ Implementado
Frontend: 📝 Documentado (ver `READING_FRONTEND_INTEGRATION.md`)
Tests: ✅ Creados
Integración: ✅ Lista
