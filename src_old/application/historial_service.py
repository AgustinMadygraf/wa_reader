"""
Path: src/application/historial_service.py
"""

import logging
from src.shared.app_config import AppConfig
from src.interface_adapters.gateways.whatsapp_client import WhatsAppClient
from src.uses_cases.message_processor import MessageProcessor
from datetime import datetime
from src.interface_adapters.gateways.ingest_service import IngestService
from src_old.application.historial_presenter import HistorialPresenter
from src_old.domain.meta_parser import MetaParser


class HistorialService:
    "Servicio para gestionar el historial de mensajes de WhatsApp"
    def __init__(self, config: AppConfig, processor=None):
        self.config = config
        self.logger = logging.getLogger("wa_reader.historial")
        self.ingest_service = IngestService(config.ingest_url)
        def get_fecha():
            return datetime.now(config.tz_local).strftime("%Y-%m-%d")
        if processor is None:
            self.processor = MessageProcessor(get_fecha)
        else:
            self.processor = processor

    def revisar(self):
        "Revisa el historial de mensajes de WhatsApp y muestra por CLI o envía por API"
        logger = logging.getLogger("wa_reader.historial")
        ingest_service = IngestService(self.config.ingest_url)
        def get_fecha():
            return datetime.now(self.config.tz_local).strftime("%Y-%m-%d")
        processor = MessageProcessor(get_fecha)
        presenter = HistorialPresenter()
        try:
            with WhatsAppClient(self.config) as wa_client:
                logger.info("Inicializando cliente de WhatsApp...")
                wa_client.initialize()
                logger.info("Abriendo chat: %s", self.config.chat_name)
                wa_client.open_chat(self.config.chat_name)
                logger.info("Extrayendo historial de mensajes...")
                messages = wa_client.get_messages()
                logger.debug("Total mensajes obtenidos: %d", len(messages))
                procesados = 0
                tabla = []
                tabla_prev = []
                for msg in reversed(messages):
                    meta = msg.get("meta", "")
                    body = msg.get("body", "")
                    meta_info = MetaParser.parse(meta)
                    fecha = meta_info["fecha"]
                    autor = meta_info["autor"]
                    tabla_prev.append([fecha, autor, body])
                    logger.debug("Procesando mensaje: %s %s", meta, body[:50])
                    try:
                        payload = processor.process(msg)
                    except (ValueError, KeyError, TypeError) as e:
                        logger.error("Error procesando mensaje: %s", e)
                        continue
                    if payload:
                        if self.config.output_mode == "cli":
                            logger.debug("Mostrando resultados en CLI...")
                            tabla.append([
                                payload.get("fecha") or "s/d",
                                payload.get("maquina") or "s/d",
                                payload.get("formato") or "s/d",
                                (
                                    payload.get("cantidad")
                                    if payload.get("cantidad") not in (None, "", 0)
                                    else "s/d"
                                ),
                                payload.get("turno") or "s/d",
                                payload.get("personas") or "s/d",
                                payload.get("obs") if payload.get("obs") else "sin clasificar",
                                "TodoPlastic"  # Columna cliente
                            ])
                        else:
                            try:
                                status = ingest_service.send(payload)
                                estado = status if status is not None else "ERROR_RED"
                                if status == 200:
                                    logger.info("Enviado correctamente: %s", payload)
                                else:
                                    logger.warning("Respuesta inesperada [%s] para: %s",
                                                   estado, payload)
                            except (ConnectionError, TimeoutError, ValueError) as e:
                                logger.error("Error enviando payload: %s", e)
                        procesados += 1
                if self.config.output_mode == "cli":
                    logger.info("Mostrando resultados en CLI...")
                    presenter.mostrar_tabla_autor_cargo(tabla_prev, self.config.chat_name)
                logger.info(
                    "Historial procesado: %d de %d mensajes revisados.",
                    procesados,
                    len(messages)
                )
        except (ImportError, AttributeError, RuntimeError) as e:
            logger.error("Error crítico en revisión de historial: %s", e)
