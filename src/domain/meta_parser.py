"""
Path: src/domain/meta_parser.py
"""
import re

class MetaParser:
    "Parser para extraer información del campo meta de mensajes de WhatsApp"
    AUTHOR_ROLES = {
        "Mariano Montenegro Madygraf": "Operario",
        "Maria De Los Angeles Madygraf": "Operaria",
        "🌸Eri 2": "Operaria",
        "Cele Mady 2": "Operaria",
        "PolloArriondo RRD": "Operario",
        "Nico Malo Mady": "Coordinador",
        "Loco Medina Mady": "Operario",
        "Emiliana Madygraf": "Operaria",
    }

    @classmethod
    def get_cargo(cls, autor: str) -> str:
        "Devuelve el cargo del autor, o 'Sin definir' si no está en el diccionario."
        return cls.AUTHOR_ROLES.get(autor, "Sin definir")

    META_REGEX = re.compile(r"\[(.+?),\s*(.+?)\]\s*(.+?):")

    @classmethod
    def parse(cls, meta: str) -> dict:
        """Extrae fecha y autor del campo meta. Retorna dict con 'fecha' y 'autor'."""
        m = cls.META_REGEX.match(meta)
        if m:
            return {
                "fecha": m.group(2),
                "autor": m.group(3)
            }
        return {
            "fecha": "",
            "autor": ""
        }
