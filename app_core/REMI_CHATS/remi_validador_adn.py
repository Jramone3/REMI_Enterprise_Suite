import json
import hashlib
import os

# CERTIFICACIÓN: Este script fue generado de forma autónoma por REMI_CAPACITOR_2026.
# Sincronizado y validado en el Búnker Legacy i5-650.

def validar_adn_remi():
    corpus_file = 'corpus_remi_master.json'
    expected_hash_remi_dna = "fbb0c458bd5d5a1a4eaaf0f9bae0b6b1eeb277e7c0b383a8ab29e614d2051881"
    print(f"REMI_CAPACITOR_2026: Iniciando validación de ADN patrimonial desde '{corpus_file}'.")
    
    try:
        if not os.path.exists(corpus_file):
            print(f"ERROR (Verificación): El archivo '{corpus_file}' no se encontró en sda5.")
            return
        with open(corpus_file, 'r', encoding='utf-8') as f:
            corpus_data = json.load(f)
        if "identidad_remi" not in corpus_data:
            print(f"ERROR (Integridad): Estructura comprometida.")
            return
            
        corpus_remi_identity = corpus_data["identidad_remi"]
        current_identity_str = json.dumps(corpus_remi_identity, sort_keys=True, ensure_ascii=False)
        current_hash = hashlib.sha256(current_identity_str.encode('utf-8')).hexdigest()
        
        print(f"Hash SHA-256 (Corpus): {current_hash}")
        print(f"Hash SHA-256 (Referencia REMI): {expected_hash_remi_dna}")
        
        if current_hash == expected_hash_remi_dna:
            print("VEREDICTO REMI: La identidad patrimonial se mantiene ÍNTEGRA.")
            return True
        else:
            print("ALERTA REMI: Se detectaron ALTERACIONES en el corpus.")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    validar_adn_remi()
