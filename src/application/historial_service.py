"""
Path: src/application/historial_service.py
"""

import logging
import re
from src.adapters.app_config import AppConfig
from src.infrastructure.whatsapp_client import WhatsAppClient
from src.domain.message_processor import MessageProcessor
from src.infrastructure.ingest_service import IngestService
from src.application.historial_presenter import HistorialPresenter

class HistorialService:
    "Servicio para gestionar el historial de mensajes de WhatsApp"
    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = logging.getLogger("wa_reader.historial")
        self.ingest_service = IngestService(config.ingest_url)
        self.processor = MessageProcessor(config)

    def revisar(self):
        "Revisa el historial de mensajes de WhatsApp y muestra por CLI o envía por API"
        logger = logging.getLogger("wa_reader.historial")
        ingest_service = IngestService(self.config.ingest_url)
        processor = MessageProcessor(self.config)
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
                    m = re.match(r"\[(.+?),\s*(.+?)\]\s*(.+?):", meta)
                    if m:
                        fecha = m.group(2)
                        autor = m.group(3)
                    else:
                        fecha = ""
                        autor = ""
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
                                payload.get("obs") if payload.get("obs") else "sin clasificar"
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
                    presenter.mostrar_tabla_cruda(tabla_prev, self.config.chat_name)
                    presenter.mostrar_tabla_procesada(tabla, self.config.chat_name)
                logger.info(
                    "Historial procesado: %d de %d mensajes revisados.",
                    procesados,
                    len(messages)
                )
        except (ImportError, AttributeError, RuntimeError) as e:
            logger.error("Error crítico en revisión de historial: %s", e)
