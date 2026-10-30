#!/usr/bin/env python3
# ==============================================================================
# REMI_CORE - MÓDULO DE INTEGRACIÓN DE HERRAMIENTAS TUI (BINSIDER, BANDWHICH)
# ==============================================================================
import subprocess
import shutil
import os

class RemiSystemTools:
    @staticmethod
    def auditar_binario(ruta_binario: str) -> str:
        """Utiliza Binsider para inspeccionar un ejecutable ELF de forma estática."""
        binsider_path = shutil.which("binsider") or "/home/ramon/.cargo/bin/binsider"
        if not os.path.exists(binsider_path):
            return "⚠️ 'binsider' no está disponible en el sistema."
        try:
            res = subprocess.run([binsider_path, "--info", ruta_binario], capture_output=True, text=True, timeout=10)
            return res.stdout if res.returncode == 0 else res.stderr
        except Exception as e:
            return f"Error ejecutando binsider: {e}"

    @staticmethod
    def verificar_red_bandwhich() -> str:
        """Verifica la disponibilidad de bandwhich para el monitoreo de tráfico."""
        bandwhich_path = shutil.which("bandwhich") or "/home/ramon/.cargo/bin/bandwhich"
        if os.path.exists(bandwhich_path):
            return f"🟢 Bandwhich listo en: {bandwhich_path} (Ejecutar con sudo para captura de paquetes)."
        return "⚠️ Bandwhich no encontrado."

    @staticmethod
    def conexiones_activas_seguras() -> str:
        """Lista conexiones de red utilizando herramientas nativas y seguras del kernel (ss)."""
        try:
            res = subprocess.run(["ss", "-tulpn"], capture_output=True, text=True, timeout=5)
            return res.stdout if res.returncode == 0 else "Error al consultar conexiones."
        except Exception as e:
            return f"Excepción al ejecutar ss: {e}"

if __name__ == "__main__":
    print("🛠️ Módulo de Herramientas de Sistema REMI_CORE inicializado correctamente.")
    print(RemiSystemTools.verificar_red_bandwhich())
    print("\n--- Auditoría Rápida de Puertos (Kernel Nativo) ---")
    print(RemiSystemTools.conexiones_activas_seguras()[:400] + "\n[...]")
