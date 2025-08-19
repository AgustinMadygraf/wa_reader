"""
Path: 
"""
import time
import logging
from datetime import datetime

from src.shared.app_config import AppConfig

from src.entities.ingest_service_interface import IIngestService
from src.entities.whatsapp_client_interface import IWhatsAppClient
from src.uses_cases.message_processor import MessageProcessor

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
        # MetaParser debe ser inyectado o configurado externamente
        self.meta_parser = None  # Se recomienda inyectar desde la capa de configuración

    def run(self):
        "Ejecuta el monitor de WhatsApp. Solo orquesta, delega envío y presentación."
        self.logger.info("Iniciando monitor de WhatsApp...")
        if self.meta_parser is None:
            self.logger.error("MetaParser no configurado. Abortando.")
            return
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
                            # Delegar envío a IngestService (gateway)
                            status = self.ingest_service.send(payload)
                            estado = status if status is not None else "ERROR_RED"
                            # Delegar presentación/logging a Presenter externo
                            # Ejemplo: presenter.mostrar_envio(payload, estado)
                    time.sleep(self.config.poll_sec)
        except KeyboardInterrupt:
            self.logger.info("Monitor detenido por el usuario.")
        except (RuntimeError, ConnectionError) as e:
            self.logger.error("Error crítico en monitor: %s", e)
