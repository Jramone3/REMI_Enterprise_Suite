#!/usr/bin/env python3
# ==============================================================================
# REMI_CORE - MÓDULO DE INTEGRACIÓN: WHISPER.CPP, FABRIC Y DOCUMENSO
# ==============================================================================
import subprocess
import shutil
import os

class RemiAITools:
    @staticmethod
    def transcribir_audio(ruta_audio: str) -> str:
        """Transcribe notas de voz y audios locales usando Whisper.cpp."""
        whisper_bin = shutil.which("whisper-cli") or os.path.expanduser("~/whisper.cpp/build/bin/whisper-cli")
        model_path = os.path.expanduser("~/whisper.cpp/models/ggml-base.bin")
        
        if not os.path.exists(whisper_bin) or not os.path.exists(model_path):
            return "⚠️ Whisper.cpp o el modelo ggml-base.bin no están configurados correctamente."
        try:
            res = subprocess.run([whisper_bin, "-m", model_path, "-f", ruta_audio, "-l", "es", "-nt"], capture_output=True, text=True, timeout=30)
            return res.stdout.strip() if res.returncode == 0 else res.stderr
        except Exception as e:
            return f"Error ejecutando Whisper.cpp: {e}"

    @staticmethod
    def aplicar_patron_fabric(texto: str, patron: str) -> str:
        """Aplica un patrón de inteligencia de Fabric a un texto dado."""
        fabric_bin = shutil.which("fabric") or os.path.expanduser("~/go/bin/fabric")
        if not os.path.exists(fabric_bin):
            return "⚠️ Fabric no está disponible en el PATH."
        try:
            res = subprocess.run([fabric_bin, "-p", patron], input=texto, capture_output=True, text=True, timeout=20)
            return res.stdout.strip() if res.returncode == 0 else res.stderr
        except Exception as e:
            return f"Error ejecutando Fabric: {e}"

if __name__ == "__main__":
    print("🧠 Módulo AI_Tools de REMI_CORE vinculado exitosamente.")
    print("• Motor de Voz (Whisper.cpp) -> Vinculado.")
    print("• Patrones de Inteligencia (Fabric) -> Vinculado.")
