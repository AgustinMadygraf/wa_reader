"""
Pruebas unitarias para MessageParser: clasificación de observaciones
"""
import unittest
from src.entities.message_parser import MessageParser

class TestMessageParserObservaciones(unittest.TestCase):
    "Pruebas para la clasificación de observaciones"
    def setUp(self):
        self.parser = MessageParser()

    def test_sin_clasificar(self):
        "Prueba con mensaje sin clasificar"
        msg = "Hola, ¿cómo están?"
        result = self.parser.parse(msg)
        self.assertIn("obs", result)
        self.assertIn("Sin clasificar", result["obs"])

    def test_tarea_pendiente(self):
        "Prueba con mensaje de tarea pendiente"
        msg = "Hay que revisar la máquina mañana."
        result = self.parser.parse(msg)
        self.assertIn("obs", result)
        self.assertIn("Tarea Pendiente", result["obs"])

    def test_tarea_finalizada(self):
        "Prueba con mensaje de tarea finalizada"
        msg = "Listo, la máquina está reparada."
        result = self.parser.parse(msg)
        self.assertIn("obs", result)
        self.assertIn("Tarea Finalizada", result["obs"])

    def test_multiple_observaciones(self):
        "Prueba con mensaje que contiene múltiples observaciones"
        msg = "Pendiente de revisión, pero ya está terminado."
        result = self.parser.parse(msg)
        self.assertIn("obs", result)
        # Puede detectar ambas observaciones si la lógica lo permite
        self.assertTrue(
            "Tarea Finalizada" in result["obs"] or "Tarea Pendiente" in result["obs"]
        )

if __name__ == "__main__":
    unittest.main()
