"""
Path: src/Application/WhatsAppMonitor.py
"""
import time
from urllib.parse import urlencode
from src.adapters.app_config import AppConfig
from src.domain.message_processor import MessageProcessor
from src.infrastructure.ingest_service import IngestService
from src.infrastructure.whatsapp_client import WhatsAppClient

class WhatsAppMonitor:
    "Monitor de WhatsApp"
    def __init__(self, config: AppConfig):
        self.config = config
        self.ingest_service = IngestService(config.ingest_url)
        self.processor = MessageProcessor(config)

    def run(self):
        "Ejecuta el monitor de WhatsApp."
        with WhatsAppClient(self.config) as wa_client:
            wa_client.initialize()
            wa_client.open_chat(self.config.chat_name)

            while True:
                messages = wa_client.get_messages()
                for msg in messages:
                    if payload := self.processor.process(msg):
                        status = self.ingest_service.send(payload)
                        estado = status if status is not None else "ERROR_RED"
                        print(f"→ GET {self.config.ingest_url}?{urlencode(payload)}  [{estado}]")
                time.sleep(self.config.poll_sec)
