from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ ERROR: OPENAI_API_KEY no está configurada")
else:
    print(f"✅ API key encontrada: {api_key[:20]}...")
    
    try:
        # CORRECTO: Solo pasar api_key
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Di hola"}],
            max_tokens=10
        )
        print("✅ OpenAI funciona correctamente!")
        print(f"Respuesta: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ Error al conectar con OpenAI: {e}")