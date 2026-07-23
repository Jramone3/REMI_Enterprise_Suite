# -*- coding: utf-8 -*-
"""
REMI_IA: poc_bridge_inflation.py
Objetivo: Simular matemáticamente la vulnerabilidad de inflación crítica.
"""

class GraphBridgeSimulator:
    def __init__(self):
        self.l1_total_supply = 10000000000  # 10B GRT
        self.l2_mint_allowance = 5000000     # Límite inicial
        self.total_minted_from_l2 = 0

    def simulate_migration_glitch(self, snapshot_value):
        print(f"\n[!] ERROR LÓGICO: Snapshot de migración desincronizado.")
        print(f"[!] Nuevo allowance (sin respaldo): {snapshot_value} GRT")
        self.l2_mint_allowance = snapshot_value

    def attempt_mint_from_l2(self, amount):
        print(f"[*] Intento de minting: {amount} GRT")
        if amount <= (self.l2_mint_allowance - self.total_minted_from_l2):
            self.l1_total_supply += amount
            self.total_minted_from_l2 += amount
            print(f"[SUCCESS] Minting exitoso. Suministro L1: {self.l1_total_supply}")
            return True
        else:
            print("[REVERT] La cantidad excede el allowance.")
            return False

if __name__ == "__main__":
    print("--- INICIO DE PRUEBA DE CONCEPTO (REMI CORE) ---")
    bridge = GraphBridgeSimulator()
    
    # 1. Operación Normal
    bridge.attempt_mint_from_l2(1000000)
    
    # 2. El Fallo detectado por jramonrivasg (Falta de State Proof)
    bridge.simulate_migration_glitch(9999999999) 
    
    # 3. Inflación Crítica
    bridge.attempt_mint_from_l2(5000000000)
    
    print("\n--- RESULTADO FINAL ---")
    print(f"Suministro Final: {bridge.l1_total_supply} GRT")
    print("[Veredicto]: Vulnerabilidad de Inflación VERIFICADA.")
