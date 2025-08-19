"""
Path: src_old/application/whatsapp_monitor.py
"""
import time
import logging
from urllib.parse import urlencode
import requests
from src.shared.app_config import AppConfig
from src.uses_cases.message_processor import MessageProcessor
from datetime import datetime
from src.entities.ingest_service_interface import IIngestService
from src.entities.whatsapp_client_interface import IWhatsAppClient
import json
from src_old.domain.meta_parser import MetaParser



class WhatsAppMonitor:

    "Monitor de WhatsApp"
    def __init__(self, config: AppConfig, ingest_service: IIngestService, wa_client: IWhatsAppClient, processor=None):
        self.config = config
        self.ingest_service = ingest_service
        self.wa_client = wa_client
        def get_fecha():
            return datetime.now(config.tz_local).strftime("%Y-%m-%d")
        if processor is None:
            self.processor = MessageProcessor(get_fecha)
        else:
            self.processor = processor
        self.logger = logging.getLogger("wa_reader.monitor")

        # Cargar roles de autor desde archivo y crear MetaParser
        try:
            with open(self.config.author_roles_path, encoding="utf-8") as f:
                author_roles = json.load(f)
        except (OSError, json.JSONDecodeError):
            author_roles = {}
        self.meta_parser = MetaParser(author_roles)

    def run(self):
        "Ejecuta el monitor de WhatsApp."
        self.logger.info("Iniciando monitor de WhatsApp...")
        try:
            with self.wa_client as wa_client:
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
                        meta_info = self.meta_parser.parse(meta)
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
