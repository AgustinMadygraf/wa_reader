"""
Path: src/application/historial_service.py
"""

import logging
from src.shared.app_config import AppConfig
from src.entities.meta_parser import MetaParser
from src.uses_cases.message_processor import MessageProcessor
from src.interface_adapters.gateways.whatsapp_client import WhatsAppClient
from src.interface_adapters.gateways.ingest_service import IngestService
from src.interface_adapters.presenters.historial_presenter import HistorialPresenter

class HistorialService:
    "Servicio para gestionar el historial de mensajes de WhatsApp"
    def __init__(self, config: AppConfig, wa_client: WhatsAppClient, ingest_service: IngestService,
                 presenter: HistorialPresenter, meta_parser: MetaParser, processor: MessageProcessor):
        self.config = config
        self.logger = logging.getLogger("wa_reader.historial")
        self.wa_client = wa_client
        self.ingest_service = ingest_service
        self.presenter = presenter
        self.meta_parser = meta_parser
        self.processor = processor

    def revisar(self):
        "Revisa el historial de mensajes de WhatsApp y muestra por CLI o envía por API"
        self.logger.debug("Inicializando cliente de WhatsApp...")
        with self.wa_client as wa_client:
            wa_client.initialize()
            self.logger.debug("Abriendo chat: %s", self.config.chat_name)
            wa_client.open_chat(self.config.chat_name)
            self.logger.debug("Extrayendo historial de mensajes...")
            messages = wa_client.get_messages()
            self.logger.debug("Total mensajes obtenidos: %d", len(messages))
            procesados = 0
            tabla = []
            tabla_prev = []
            for msg in reversed(messages):
                meta = msg.get("meta", "")
                body = msg.get("body", "")
                meta_info = self.meta_parser.parse(meta)
                fecha = meta_info["fecha"]
                autor = meta_info["autor"]
                tabla_prev.append([fecha, autor, body])
                self.logger.debug("Procesando mensaje: %s %s", meta, body[:50])
                try:
                    payload = self.processor.process(msg)
                except (ValueError, KeyError, TypeError) as e:
                    self.logger.error("Error procesando mensaje: %s", e)
                    continue
                if payload:
                    if self.config.output_mode == "cli":
                        self.logger.debug("Mostrando resultados en CLI...")
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
                            status = self.ingest_service.send(payload)
                            estado = status if status is not None else "ERROR_RED"
                            if status == 200:
                                self.logger.info("Enviado correctamente: %s", payload)
                            else:
                                self.logger.warning("Respuesta inesperada [%s] para: %s",
                                                   estado, payload)
                        except (ConnectionError, TimeoutError, ValueError) as e:
                            self.logger.error("Error enviando payload: %s", e)
                    procesados += 1
            if self.config.output_mode == "cli":
                self.logger.info("Mostrando resultados en CLI...")
                self.presenter.mostrar_tabla_autor_cargo(tabla_prev, self.config.chat_name)
            self.logger.info(
                "Historial procesado: %d de %d mensajes revisados.",
                procesados,
                len(messages)
            )
