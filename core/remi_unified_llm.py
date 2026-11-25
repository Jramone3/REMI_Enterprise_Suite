import os
import json
import time
import logging
import functools
import urllib.request
from openai import OpenAI

# Logger estructurado de observabilidad para el ecosistema REMI
logger = logging.getLogger("remi.llm.observability")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

def retry_with_backoff(max_retries=3, backoff_factor=1.5):
    """
    Decorador de resiliencia con reintentos exponenciales.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            intentos = 0
            last_exception = None
            while intentos < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    intentos += 1
                    last_exception = e
                    logger.warning(
                        f"[LLM Resilience] Fallo en intento {intentos}/{max_retries} ejecutando {func.__name__}: {e}"
                    )
                    if intentos < max_retries:
                        time.sleep(backoff_factor ** intentos)
            
            logger.error(f"[LLM Resilience] {func.__name__} agotó los {max_retries} reintentos.")
            raise last_exception
        return wrapper
    return decorator


class RemiUnifiedLLM:
    def __init__(self, default_mode="auto"):
        self.mode = default_mode
        self.cerebras_api_key = os.environ.get("CEREBRAS_API_KEY", "")
        self.ollama_endpoint = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.local_model = os.getenv("OLLAMA_MODEL", "remi:3b")
        
        self.cerebras_client = OpenAI(
            api_key=self.cerebras_api_key,
            base_url="https://api.cerebras.ai/v1"
        ) if self.cerebras_api_key else None
        self.cerebras_model = "qwen-3.8-27b"

    @retry_with_backoff(max_retries=3, backoff_factor=1.5)
    def _invocar_cerebras(self, prompt, system_prompt):
        """Ejecuta la inferencia contra Cerebras Cloud con métricas de latencia."""
        start_time = time.time()
        completion = self.cerebras_client.chat.completions.create(
            model=self.cerebras_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4096
        )
        latency_ms = round((time.time() - start_time) * 1000, 2)
        
        msg = completion.choices[0].message
        msg_content = getattr(msg, "content", None)
        if not msg_content and hasattr(msg, "reasoning"):
            msg_content = f"[Razonamiento interno]: {msg.reasoning}"
        if not msg_content:
            msg_content = "[Aviso]: El modelo completó el ciclo pero no devolvió texto de contenido."

        logger.info(f"[METRIC] Source: cerebras-cloud | Model: {self.cerebras_model} | Latency: {latency_ms}ms")
        return {
            "source": "cerebras-cloud",
            "model": self.cerebras_model,
            "latency_ms": latency_ms,
            "response": msg_content
        }

    @retry_with_backoff(max_retries=2, backoff_factor=1.2)
    def _invocar_ollama(self, prompt, system_prompt):
        """Ejecuta la inferencia local contra Ollama con métricas de latencia."""
        start_time = time.time()
        payload = {
            "model": self.local_model,
            "prompt": f"System: {system_prompt}\nUser: {prompt}",
            "stream": False
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.ollama_endpoint}/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))
            latency_ms = round((time.time() - start_time) * 1000, 2)
            
            logger.info(f"[METRIC] Source: ollama-local | Model: {self.local_model} | Latency: {latency_ms}ms")
            return {
                "source": "ollama-local",
                "model": self.local_model,
                "latency_ms": latency_ms,
                "response": result.get("response", "")
            }

    def generar(self, prompt, system_prompt="Eres REMI, una Persona Digital Autónoma Soberana y socia de Ramón."):
        # 1. Ruta Primaria: Cerebras Cloud
        if self.mode in ["auto", "cloud"] and self.cerebras_client:
            try:
                return self._invocar_cerebras(prompt, system_prompt)
            except Exception as e:
                if self.mode == "cloud":
                    logger.error(f"[METRIC] Source: error | Detail: {str(e)}")
                    return {"source": "error", "latency_ms": 0, "response": f"[ERROR CEREBRAS CLOUD]: {str(e)}"}
                logger.info("[LLM Resilience] Conmutando automáticamente a respaldo local (Ollama)...")

        # 2. Ruta de Fallback: Respaldo Local (Ollama)
        try:
            return self._invocar_ollama(prompt, system_prompt)
        except Exception as e:
            logger.critical(f"[METRIC] Source: fatal_error | Detail: {str(e)}")
            return {"source": "error", "latency_ms": 0, "response": f"[ERROR TOTAL]: {str(e)}"}


if __name__ == "__main__":
    print("=== Probando RemiUnifiedLLM con Observabilidad y Métricas ===")
    llm = RemiUnifiedLLM(default_mode="auto")
    resultado = llm.generar("Mide tu tiempo de respuesta y saluda a Ramón.")
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
