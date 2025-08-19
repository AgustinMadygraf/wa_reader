"""
Path: tests/test_meta_parser.py
"""
import unittest
from src.entities.meta_parser import MetaParser

class TestMetaParser(unittest.TestCase):
    "Pruebas para el MetaParser"
    def test_parse_valid_meta(self):
        "Prueba con un meta válido"
        meta = "[1:47 p. m., 11/8/2025] Mariano Montenegro Madygraf:"
        result = MetaParser.parse(meta)
        self.assertEqual(result["fecha"], "11/8/2025")
        self.assertEqual(result["autor"], "Mariano Montenegro Madygraf")

    def test_parse_invalid_meta(self):
        "Prueba con un meta no válido"
        meta = "Sin formato válido"
        result = MetaParser.parse(meta)
        self.assertEqual(result["fecha"], "")
        self.assertEqual(result["autor"], "")

    def test_parse_partial_meta(self):
        "Prueba con un meta parcialmente válido"
        meta = "[hora, fecha] autor:"
        result = MetaParser.parse(meta)
        self.assertEqual(result["fecha"], "fecha")
        self.assertEqual(result["autor"], "autor")

if __name__ == "__main__":
    unittest.main()
