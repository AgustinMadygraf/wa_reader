"""
Path: src/domain/meta_parser.py
"""
import re
import json
from src.shared.app_config import AppConfig

class MetaParser:
    "Parser para extraer información del campo meta de mensajes de WhatsApp"
    _author_roles = None

    @classmethod
    def _load_author_roles(cls):
        if cls._author_roles is None:
            try:
                config = AppConfig()
                with open(config.author_roles_path, encoding="utf-8") as f:
                    cls._author_roles = json.load(f)
            except (OSError, json.JSONDecodeError):
                cls._author_roles = {}
        return cls._author_roles

    @classmethod
    def get_cargo(cls, autor: str) -> str:
        "Devuelve el cargo del autor, o 'Sin definir' si no está en el diccionario."
        roles = cls._load_author_roles()
        return roles.get(autor, "Sin definir")

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
