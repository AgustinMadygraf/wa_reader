"""
Path: src/entities/ingest_service_interface.py
"""

from abc import ABC, abstractmethod

class IIngestService(ABC):
    "Interfaz para el servicio de ingestión de datos"
    @abstractmethod
    def send(self, payload: dict) -> str:
        "Envía un payload al servicio de ingestión."
        pass
