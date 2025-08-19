"""
Path: src/interface_adapters/gateways/ingest_service.py
"""

import requests
from src.entities.ingest_service_interface import IIngestService

class IngestService(IIngestService):
    "Servicio de Ingesta"
    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def send(self, payload: dict) -> str:
        "Envía un payload al servicio de ingesta. Retorna el id o mensaje de respuesta."
        try:
            response = requests.post(self.endpoint, json=payload)
            response.raise_for_status()
            return response.text
        except Exception as e:
            return f"Error: {e}"

