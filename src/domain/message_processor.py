"""
Path: src/domain/message_processor.py
"""

import hashlib
from datetime import datetime
from src.domain.message_parser import MessageParser
from src.domain.interfaces import IMessageProcessor


class MessageProcessor(IMessageProcessor):
    "Procesador de mensajes de WhatsApp con soporte para estrategias"
    def __init__(self, config, parser_strategy=None):
        self.config = config
        # Permite inyectar una estrategia de análisis, por defecto usa MessageParser
        if parser_strategy is None:
            self.parser = MessageParser()
        else:
            self.parser = parser_strategy
        self.seen_messages = set()

    def process(self, message: dict) -> dict | None:
        "Procesa un mensaje de WhatsApp."
        key = hashlib.sha1((message["meta"] + "\n" + message["body"]).encode("utf-8")).hexdigest()
        if key in self.seen_messages:
            return None
        self.seen_messages.add(key)
        parsed = self.parser.parse(message["body"])
        if not parsed:
            return None
        return {
            "fecha": datetime.now(self.config.tz_local).strftime("%Y-%m-%d"),
            "maquina": parsed.get("maquina", ""),
            "formato": parsed.get("formato", ""),
            "cantidad": parsed.get("cantidad", 0),
            "turno": parsed.get("turno", ""),
            "personas": parsed.get("personas", ""),
            "obs": parsed.get("obs", "")
        }
