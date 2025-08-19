"""
Path: src/domain/interfaces.py
Interfaces para componentes principales del sistema (parser, procesador, etc.)
"""
from abc import ABC, abstractmethod

class IMessageParser(ABC):
    "Interfaz para el análisis de mensajes"
    @abstractmethod
    def parse(self, text: str) -> dict:
        """Parsea un mensaje y retorna un diccionario con los datos extraídos."""
        pass  # pylint: disable=unnecessary-pass

class IMessageProcessor(ABC):
    "Interfaz para el procesamiento de mensajes"
    @abstractmethod
    def process(self, message: dict) -> dict:
        """Procesa un mensaje y retorna un diccionario con los datos procesados."""
        pass  # pylint: disable=unnecessary-pass
