import sys

class PatchValidator:
    def __init__(self):
        print("[REMI CORE] Running mitigation assessment for Optimism Core...")
        self.balances = {"0xAttackerContract": 1000}
        self.reentrancy_guard = False

    def secure_withdraw(self, user, amount):
        print(f"\n[REMI MONITOR] Secure hook intercepting user transaction...")
        
        # Simulación de Modificador nonReentrant
        if self.reentrancy_guard:
            print("[🛡️ SEGURIDAD] LLAMADA RECHAZADA: Intento de reentrada bloqueado por el Guard.")
            return False
            
        if self.balances.get(user, 0) >= amount:
            self.reentrancy_guard = True # Bloqueo activo
            
            # Efecto seguro antes de la interacción externa
            print(f"[REMI MONITOR] Aplicando Efecto: Descontando balance antes de llamada externa.")
            self.balances[user] -= amount 
            
            # Interacción
            print(f"[CALL] Transfiriendo control a {user}...")
            # Intento simulado de reentrada del atacante
            self.secure_withdraw(user, amount)
            
            self.reentrancy_guard = False # Liberación
            return True
        else:
            print(f"[REMI MONITOR] Transacción denegada: Fondos insuficientes.")
            return False

if __name__ == "__main__":
    validator = PatchValidator()
    validator.secure_withdraw("0xAttackerContract", 1000)
    print(f"\n[RESULTADO] Balance final controlado: {validator.balances}")
