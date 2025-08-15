"""
Path: src/Application/WhatsAppMonitor.py
"""
import time
import logging
from urllib.parse import urlencode
import requests
from src.adapters.app_config import AppConfig
from src.domain.message_processor import MessageProcessor
from src.infrastructure.ingest_service import IngestService
from src.infrastructure.whatsapp_client import WhatsAppClient
from src.domain.meta_parser import MetaParser


class WhatsAppMonitor:
    "Monitor de WhatsApp"
    def __init__(self, config: AppConfig, processor=None):
        self.config = config
        self.ingest_service = IngestService(config.ingest_url)
        if processor is None:
            self.processor = MessageProcessor(config)
        else:
            self.processor = processor
        self.logger = logging.getLogger("wa_reader.monitor")

    def run(self):
        "Ejecuta el monitor de WhatsApp."
        self.logger.info("Iniciando monitor de WhatsApp...")
        try:
            with WhatsAppClient(self.config) as wa_client:
                self.logger.info("Inicializando cliente de WhatsApp...")
                wa_client.initialize()
                self.logger.info("Abriendo chat: %s", self.config.chat_name)
                wa_client.open_chat(self.config.chat_name)

                while True:
                    self.logger.debug("Obteniendo mensajes...")
                    messages = wa_client.get_messages()
                    self.logger.debug("Total mensajes obtenidos: %d", len(messages))
                    for msg in messages:
                        meta = msg.get("meta", "")
                        _body = msg.get("body", "")
                        meta_info = MetaParser.parse(meta)
                        _fecha = meta_info["fecha"]
                        _autor = meta_info["autor"]
                        try:
                            payload = self.processor.process(msg)
                        except (ValueError, TypeError) as e:
                            self.logger.error("Error procesando mensaje: %s", e)
                            continue
                        if payload:
                            try:
                                status = self.ingest_service.send(payload)
                                estado = status if status is not None else "ERROR_RED"
                                url = f"{self.config.ingest_url}?{urlencode(payload)}"
                                self.logger.info("→ GET %s  [%s]", url, estado)
                            except requests.RequestException as e:
                                self.logger.error("Error enviando payload: %s", e)
                    time.sleep(self.config.poll_sec)
        except KeyboardInterrupt:
            self.logger.info("Monitor detenido por el usuario.")
        except (RuntimeError, ConnectionError) as e:
            self.logger.error("Error crítico en monitor: %s", e)
