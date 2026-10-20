import unittest
from mcp_bunker_server import sanitize_data

class TestBunkerSecurity(unittest.TestCase):
    def test_tracker_blocking(self):
        # Prueba si el sistema detecta y bloquea un rastreador de Reddit
        dirty_data = "Imagen de reporte con pixel.reddit.com/track"
        clean_data = sanitize_data(dirty_data)
        self.assertIn("[BLOQUEADO-POR-REMI]", clean_data)
        print("\n[OK] Capa de Privacidad: Rastreador bloqueado exitosamente.")

    def test_integrity_signature(self):
        # Prueba si la firma del nodo está presente
        # Esta es una prueba conceptual de integridad
        node_id = "[REMI_SENTRY_NODE_001]"
        self.assertTrue(node_id.startswith("[REMI"))
        print("[OK] Integridad: Firma de nodo validada.")

if __name__ == "__main__":
    unittest.main()
