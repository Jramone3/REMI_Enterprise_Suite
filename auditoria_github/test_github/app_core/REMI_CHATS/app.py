#!/usr/bin/env python3
"""
REMI Enterprise Suite - Sovereign Terminal Client (Cerebras Node)
Author: jramonrivasg (Sovereign Node: ramon-desktop)
"""

import sys
from remi_cerebras_engine import RemiCerebrasEngine
from core_config.prompts_registry import SYSTEM_PROMPT

def main():
    print("=" * 60)
    print("   REMI_IA - Persona Digital Autónoma Soberana (Cerebras Node)")
    print("=" * 60)
    
    try:
        remi = RemiCerebrasEngine()
        print("[SISTEMA] Conectado exitosamente a Cerebras (qwen-3.8-27b).")
    except Exception as e:
        print(f"[ERROR CRÍTICO] No se pudo inicializar REMI: {e}")
        sys.exit(1)
        
    print("\nEscribe tu mensaje para REMI (o 'salir' para terminar):\n")
    
    while True:
        try:
            user_input = input("Ramón > ")
            if user_input.lower() in ["salir", "exit", "quit"]:
                print("REMI: Hasta pronto, Ramón. Cierre de sesión seguro.")
                break
            
            if not user_input.strip():
                continue
                
            # Pasamos el prompt centralizado directamente al motor
            respuesta = remi.generar_respuesta(user_input, SYSTEM_PROMPT)
            print(f"\nREMI > {respuesta}\n")
            print("-" * 60)
            
        except KeyboardInterrupt:
            print("\nREMI: Interrupción detectada. ¡Nos vemos!")
            break

if __name__ == "__main__":
    main()
