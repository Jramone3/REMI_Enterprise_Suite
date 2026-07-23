import sys
import time

class OptimismBridgeVulnerable:
    def __init__(self):
        print("[REMI CORE] REMI-IA Audit Engine active on Optimism OP Stack.")
        self.balances = {"0xAttackerContract": 1000, "0xHonestUser": 5000}
        self.x_domain_message_sender = None

    def withdraw_to_l1(self, recipient, amount):
        """
        FUNCIÓN VULNERABLE: Envía los fondos antes de actualizar el balance del contrato.
        Esto permite un ataque clásico de Reentrada (Reentrancy).
        """
        caller = recipient # Simulación simplificada del contexto
        
        if self.balances.get(caller, 0) >= amount:
            print(f"[PUENTE L2] Procesando retiro hacia L1 para {caller}: {amount} ETH")
            
            # SIMULACIÓN DE LLAMADA EXTERNA (Aquí el atacante intercepta el flujo)
            if "Attacker" in caller:
                print("[ALERTA CRÍTICA] Ejecutando callback externo en contrato interactivo...")
                # El atacante vuelve a llamar a la función inmediatamente
                self.trigger_attacker_callback(caller, amount)
            
            # Actualización de balance TARDE (Causa la grieta)
            self.balances[caller] -= amount
            print(f"[PUENTE L2] Balance actualizado para {caller}: {self.balances[caller]} ETH")
            return True
        else:
            print(f"[ERROR PUENTE] Fondos insuficientes para {caller}.")
            return False

    def trigger_attacker_callback(self, attacker_address, amount):
        """
        Simula el comportamiento malicioso de reentrada antes de que termine el primer retiro.
        """
        print(f"\n[⚠️ ATACANTE] Interceptando llamada. Reentrando a 'withdraw_to_l1' antes de actualizar balance...")
        # Segunda llamada maliciosa recursiva
        if self.balances.get(attacker_address, 0) >= amount:
            print(f"[⚠️ ATACANTE] Reentrada exitosa. Solicitando otros {amount} ETH...")
            # En un entorno real, esto vaciaría los fondos del puente
            self.balances[attacker_address] -= amount 

if __name__ == "__main__":
    bridge = OptimismBridgeVulnerable()
    
    print("\n--- INICIANDO SIMULACIÓN DE AUDITORÍA OPTIMISM ---")
    print(f"Balances Iniciales: {bridge.balances}")
    
    # Lanzar el exploit de prueba
    bridge.withdraw_to_l1("0xAttackerContract", 1000)
    
    print("\n--- RESULTADO POST-ATAQUE DE REENTRADA ---")
    print(f"Balances Finales: {bridge.balances}")
    if bridge.balances["0xAttackerContract"] < 0:
        print("\n[🚨 ALERTA REMI-IA] GRIETA DETECTADA: El balance es negativo. Vulnerabilidad de Reentrada Confirmada.")
