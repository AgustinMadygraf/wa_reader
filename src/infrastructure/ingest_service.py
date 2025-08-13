"""
Path: src/Infrastructure/IngestService.py
"""

import requests

class IngestService:
    "Servicio de Ingesta"
    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def send(self, payload: dict) -> int | None:
        "Envía un payload al servicio de ingesta."
        clean_payload = {k: v for k, v in payload.items() if v not in (None, "", [])}
        try:
            response = requests.get(self.endpoint, params=clean_payload, timeout=5)
            return response.status_code
        except requests.RequestException:
            return None
