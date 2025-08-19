"""
Path: src_old/domain/meta_parser.py
"""
import re

class MetaParser:
    "Parser para extraer información del campo meta de mensajes de WhatsApp"
    META_REGEX = re.compile(r"\[(.+?),\s*(.+?)\]\s*(.+?):")

    def __init__(self, author_roles: dict = None):
        self._author_roles = author_roles or {}

    def get_cargo(self, autor: str) -> str:
        "Devuelve el cargo del autor, o 'Sin definir' si no está en el diccionario."
        return self._author_roles.get(autor, "Sin definir")

    def parse(self, meta: str) -> dict:
        """Extrae fecha y autor del campo meta. Retorna dict con 'fecha' y 'autor'."""
        m = self.META_REGEX.match(meta)
        if m:
            return {
                "fecha": m.group(2),
                "autor": m.group(3)
            }
        return {
            "fecha": "",
            "autor": ""
        }
