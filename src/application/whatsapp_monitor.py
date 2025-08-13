"""
Path: src/Application/WhatsAppMonitor.py
"""
import hashlib
from datetime import datetime
import time
from urllib.parse import urlencode
from src.adapters.app_config import AppConfig
from src.domain.message_parser import MessageParser
from src.infrastructure.ingest_service import IngestService
from src.infrastructure.whatsapp_client import WhatsAppClient

class WhatsAppMonitor:
    "Monitor de WhatsApp"
    def __init__(self, config: AppConfig):
        self.config = config
        self.parser = MessageParser()
        self.ingest_service = IngestService(config.INGEST_URL)
        self.seen_messages = set()

    def process_message(self, message: dict) -> dict | None:
        """Procesa un mensaje y devuelve payload si es válido"""
        key = hashlib.sha1((message["meta"] + "\n" + message["body"]).encode("utf-8")).hexdigest()
        if key in self.seen_messages:
            return None

        self.seen_messages.add(key)
        parsed = self.parser.parse(message["body"])
        if not parsed:
            return None

        return {
            "fecha": datetime.now(self.config.TZ_LOCAL).strftime("%Y-%m-%d"),
            "maquina": parsed.get("maquina", ""),
            "formato": parsed.get("formato", ""),
            "cantidad": parsed.get("cantidad", 0),
            "turno": parsed.get("turno", ""),
            "personas": parsed.get("personas", ""),
            "obs": parsed.get("obs", "")
        }

    def run(self):
        "Ejecuta el monitor de WhatsApp."
        with WhatsAppClient(self.config) as wa_client:
            wa_client.initialize()
            wa_client.open_chat(self.config.CHAT_NAME)

            while True:
                messages = wa_client.get_messages()
                for msg in messages:
                    if payload := self.process_message(msg):
                        status = self.ingest_service.send(payload)
                        estado = status if status is not None else "ERROR_RED"
                        print(f"→ GET {self.config.INGEST_URL}?{urlencode(payload)}  [{estado}]")
                time.sleep(self.config.POLL_SEC)
