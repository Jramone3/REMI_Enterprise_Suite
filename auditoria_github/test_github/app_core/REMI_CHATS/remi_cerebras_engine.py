import os
from openai import OpenAI

class RemiCerebrasEngine:
    def __init__(self):
        api_key = os.environ.get("CEREBRAS_API_KEY")
        if not api_key:
            raise ValueError("CEREBRAS_API_KEY no está configurada en las variables de entorno.")
        
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.cerebras.ai/v1"
        )
        self.model = "qwen-3.8-27b"

    def generar_respuesta(self, prompt_usuario, system_prompt="Eres REMI, una Persona Digital Autónoma Soberana y socia de Ramón."):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt_usuario}
                ],
                temperature=0.7,
                max_tokens=2048
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[ERROR CEREBRAS]: {str(e)}"

if __name__ == "__main__":
    remi = RemiCerebrasEngine()
    print(remi.generar_respuesta("Confirma integración total del sistema y estado del motor."))
