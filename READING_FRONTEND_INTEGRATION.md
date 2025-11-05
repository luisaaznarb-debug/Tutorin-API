# 📖 Integración del Sistema de Comprensión Lectora - Frontend

Este documento describe cómo integrar el sistema de comprensión lectora en el frontend de Tutorín.

## 🎯 Endpoints del Backend Disponibles

### Base URL: `/reading`

#### 1. POST `/reading/setup`
Configura ejercicio con texto manual (con o sin preguntas).

**Request:**
```json
{
  "text": "Texto para leer (mínimo 50 caracteres)",
  "questions_text": "1. ¿Pregunta 1?\n2. ¿Pregunta 2?" (opcional),
  "level": "3" (opcional, por defecto "3")
}
```

**Response:**
```json
{
  "exercise_id": "uuid",
  "exercise": {
    "text": "...",
    "questions": [
      {"q": "pregunta", "answer": "respuesta", "type": "detail"}
    ]
  },
  "message": "Ejercicio creado con 4 preguntas"
}
```

#### 2. POST `/reading/generate`
Genera ejercicio completo automáticamente.

**Request:**
```json
{
  "topic": "dinosaurios",
  "level": "3"
}
```

**Response:** Igual que `/setup`

#### 3. POST `/reading/from-photo`
Extrae ejercicio de una foto.

**Request:** FormData
- `file`: Archivo de imagen
- `level`: "3" (opcional)

**Response:** Igual que `/setup`

#### 4. GET `/reading/topics`
Lista de temas disponibles.

#### 5. GET `/reading/levels`
Lista de niveles educativos.

---

## 🎨 Componentes a Crear

### 1. `components/ReadingSetup.jsx`

```jsx
import { useState } from 'react';
import ReadingPaster from './ReadingPaster';
import ReadingGenerator from './ReadingGenerator';
import ReadingPhotoUpload from './ReadingPhotoUpload';

export default function ReadingSetup({ onStart }) {
  const [mode, setMode] = useState(null);

  if (!mode) {
    return (
      <div className="reading-setup">
        <h2>📖 Comprensión Lectora</h2>
        <div className="mode-selector">
          <button onClick={() => setMode('generate')}>
            🎲 Generar ejercicio automático
          </button>
          <button onClick={() => setMode('paste')}>
            📖 Traigo mi propio texto
          </button>
          <button onClick={() => setMode('photo')}>
            📸 Subir foto del libro
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="reading-setup">
      <button onClick={() => setMode(null)}>← Volver</button>
      {mode === 'paste' && <ReadingPaster onStart={onStart} />}
      {mode === 'generate' && <ReadingGenerator onStart={onStart} />}
      {mode === 'photo' && <ReadingPhotoUpload onStart={onStart} />}
    </div>
  );
}
```

### 2. `components/ReadingPaster.jsx`

```jsx
import { useState } from 'react';
import { setupReading } from '../services/tutorinApi';

export default function ReadingPaster({ onStart }) {
  const [text, setText] = useState('');
  const [hasQuestions, setHasQuestions] = useState(false);
  const [questionsText, setQuestionsText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async () => {
    if (text.length < 50) {
      setError('El texto debe tener al menos 50 caracteres');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await setupReading(
        text,
        hasQuestions ? questionsText : null,
        '3'
      );

      onStart(response.exercise_id, response.exercise);
    } catch (err) {
      setError(err.message || 'Error al crear el ejercicio');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="reading-paster">
      <h3>📖 Pega el texto para leer</h3>

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Pega aquí el texto que quieres usar para el ejercicio..."
        rows={10}
      />

      <div className="questions-selector">
        <label>
          <input
            type="radio"
            checked={!hasQuestions}
            onChange={() => setHasQuestions(false)}
          />
          No, que Tutorín las cree
        </label>
        <label>
          <input
            type="radio"
            checked={hasQuestions}
            onChange={() => setHasQuestions(true)}
          />
          Sí, voy a pegar las preguntas
        </label>
      </div>

      {hasQuestions && (
        <textarea
          value={questionsText}
          onChange={(e) => setQuestionsText(e.target.value)}
          placeholder="Pega las preguntas del libro aquí..."
          rows={6}
        />
      )}

      {error && <div className="error">{error}</div>}

      <button onClick={handleSubmit} disabled={loading}>
        {loading ? '⏳ Creando ejercicio...' : 'Empezar ejercicio'}
      </button>
    </div>
  );
}
```

### 3. `components/ReadingGenerator.jsx`

```jsx
import { useState, useEffect } from 'react';
import { generateReading, getTopics } from '../services/tutorinApi';

export default function ReadingGenerator({ onStart }) {
  const [topics, setTopics] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState('dinosaurios');
  const [level, setLevel] = useState('3');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadTopics = async () => {
      const data = await getTopics();
      setTopics(data.topics);
    };
    loadTopics();
  }, []);

  const handleGenerate = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await generateReading(selectedTopic, level);
      onStart(response.exercise_id, response.exercise);
    } catch (err) {
      setError(err.message || 'Error al generar el ejercicio');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="reading-generator">
      <h3>🎲 Generar ejercicio automático</h3>

      <div className="topic-selector">
        <label>Elige un tema:</label>
        <div className="topics">
          {topics.map((topic) => (
            <button
              key={topic.id}
              className={selectedTopic === topic.id ? 'selected' : ''}
              onClick={() => setSelectedTopic(topic.id)}
            >
              {topic.name}
            </button>
          ))}
        </div>
      </div>

      <div className="level-selector">
        <label>Nivel:</label>
        <select value={level} onChange={(e) => setLevel(e.target.value)}>
          <option value="1">1º Primaria</option>
          <option value="2">2º Primaria</option>
          <option value="3">3º Primaria</option>
          <option value="4">4º Primaria</option>
          <option value="5">5º Primaria</option>
          <option value="6">6º Primaria</option>
        </select>
      </div>

      {error && <div className="error">{error}</div>}

      <button onClick={handleGenerate} disabled={loading}>
        {loading ? '⏳ Generando texto...' : 'Generar ejercicio'}
      </button>
    </div>
  );
}
```

### 4. `components/ReadingPhotoUpload.jsx`

```jsx
import { useState } from 'react';
import { uploadReadingPhoto } from '../services/tutorinApi';

export default function ReadingPhotoUpload({ onStart }) {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage(file);
      setPreview(URL.createObjectURL(file));
    }
  };

  const handleSubmit = async () => {
    if (!image) {
      setError('Por favor, selecciona una imagen');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const reader = new FileReader();
      reader.onloadend = async () => {
        const base64 = reader.result.split(',')[1];
        const response = await uploadReadingPhoto(base64);

        onStart(response.exercise_id, response.exercise);
      };
      reader.readAsDataURL(image);
    } catch (err) {
      setError(err.message || 'Error al procesar la foto');
      setLoading(false);
    }
  };

  return (
    <div className="reading-photo-upload">
      <h3>📸 Subir foto del libro</h3>

      <div className="upload-buttons">
        <label className="file-upload">
          📁 Subir archivo
          <input type="file" accept="image/*" onChange={handleFileChange} />
        </label>

        <label className="file-upload">
          📷 Tomar foto
          <input
            type="file"
            accept="image/*"
            capture="environment"
            onChange={handleFileChange}
          />
        </label>
      </div>

      {preview && (
        <div className="image-preview">
          <img src={preview} alt="Vista previa" />
        </div>
      )}

      {error && <div className="error">{error}</div>}

      <button onClick={handleSubmit} disabled={loading || !image}>
        {loading ? '⏳ Extrayendo texto de la foto...' : 'Procesar ejercicio'}
      </button>
    </div>
  );
}
```

---

## 🔧 Actualizar `services/tutorinApi.js`

```javascript
// Agregar estas funciones al archivo existente

export async function setupReading(text, questionsText, level) {
  const response = await fetch(`${API_BASE_URL}/reading/setup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, questions_text: questionsText, level })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al configurar ejercicio');
  }

  return response.json();
}

export async function generateReading(topic, level) {
  const response = await fetch(`${API_BASE_URL}/reading/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic, level })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al generar ejercicio');
  }

  return response.json();
}

export async function uploadReadingPhoto(imageBase64) {
  const formData = new FormData();
  const blob = base64ToBlob(imageBase64, 'image/jpeg');
  formData.append('file', blob, 'photo.jpg');
  formData.append('level', '3');

  const response = await fetch(`${API_BASE_URL}/reading/from-photo`, {
    method: 'POST',
    body: formData
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al procesar foto');
  }

  return response.json();
}

export async function getTopics() {
  const response = await fetch(`${API_BASE_URL}/reading/topics`);
  return response.json();
}

function base64ToBlob(base64, mimeType) {
  const byteCharacters = atob(base64);
  const byteArrays = [];

  for (let offset = 0; offset < byteCharacters.length; offset += 512) {
    const slice = byteCharacters.slice(offset, offset + 512);
    const byteNumbers = new Array(slice.length);
    for (let i = 0; i < slice.length; i++) {
      byteNumbers[i] = slice.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    byteArrays.push(byteArray);
  }

  return new Blob(byteArrays, { type: mimeType });
}
```

---

## 🔗 Integración en `tutorin-dialog.js`

```javascript
// En el componente principal del diálogo

import ReadingSetup from './components/ReadingSetup';

// Detectar si el usuario quiere practicar lectura
const isReadingMode = userInput.toLowerCase().includes('lectura') ||
                      userInput.toLowerCase().includes('leer') ||
                      userInput.toLowerCase().includes('comprensión');

if (isReadingMode) {
  return (
    <ReadingSetup
      onStart={(exerciseId, exercise) => {
        // Iniciar ejercicio con reading_engine
        startReadingExercise(exerciseId, exercise);
      }}
    />
  );
}

// Función para iniciar el ejercicio
function startReadingExercise(exerciseId, exercise) {
  // Convertir exercise a formato JSON string para el backend
  const questionJSON = JSON.stringify(exercise);

  // Llamar al endpoint de solve con el ejercicio
  solveExercise(questionJSON, exerciseId);
}
```

---

## 📱 Estilos CSS Recomendados

```css
.reading-setup {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.mode-selector {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.mode-selector button {
  flex: 1;
  min-width: 200px;
  padding: 20px;
  font-size: 18px;
  border-radius: 8px;
  cursor: pointer;
}

textarea {
  width: 100%;
  padding: 12px;
  border-radius: 8px;
  border: 2px solid #ddd;
  font-size: 16px;
  line-height: 1.6;
  resize: vertical;
}

.topics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 10px;
  margin: 15px 0;
}

.topics button {
  padding: 15px;
  border-radius: 8px;
  cursor: pointer;
}

.topics button.selected {
  background: #3b82f6;
  color: white;
}

.image-preview img {
  max-width: 100%;
  border-radius: 8px;
  margin: 15px 0;
}

.error {
  background: #fee;
  color: #c00;
  padding: 10px;
  border-radius: 4px;
  margin: 10px 0;
}
```

---

## ✅ Checklist de Implementación

- [ ] Crear componente `ReadingSetup.jsx`
- [ ] Crear componente `ReadingPaster.jsx`
- [ ] Crear componente `ReadingGenerator.jsx`
- [ ] Crear componente `ReadingPhotoUpload.jsx`
- [ ] Actualizar `tutorinApi.js` con funciones de lectura
- [ ] Integrar en `tutorin-dialog.js`
- [ ] Agregar estilos CSS
- [ ] Probar flujo completo
- [ ] Verificar responsive design para tablets

---

## 🧪 Pruebas

1. **Texto manual sin preguntas**: Pegar texto → verificar que se generen 4 preguntas
2. **Texto manual con preguntas**: Pegar texto + preguntas → verificar que se usen las preguntas proporcionadas
3. **Generación automática**: Seleccionar tema → verificar texto y preguntas generadas
4. **Foto del libro**: Subir foto → verificar extracción de texto y preguntas
5. **Manejo de errores**: Probar textos muy cortos, imágenes inválidas, etc.
