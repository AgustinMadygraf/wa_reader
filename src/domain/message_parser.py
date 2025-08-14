"""
Path: src/domain/message_parser.py
"""

import re
import logging
from src.common.logging_config import setup_logging

setup_logging(debug=True)
logger = logging.getLogger("wa_reader.message_parser")

class MessageParser:
    "Parser de mensajes de WhatsApp"
    def __init__(self):
        # Formato: 22x10x30, 30x12x32, etc.
        self.p_formato = re.compile(r"\b(\d{2}x\d{2}x\d{2})\b", re.I)
        # Máquina: maquina de bolsas, maquina de manijas, producción de maquina de manijas, etc.
        self.p_maq = re.compile(
            (
                r"(?:maquina|máquina|producción de maquina|producción de máquina)\s+"
                r"(?:de\s+)?(bolsas|manijas)"
            ),
            re.I
        )
        # Cantidad: saldo de bobina 2773, hicimos 6800 bolsas, etc.
        self.p_cant_ctx = re.compile(
            (
                r"(?:saldo de bobina\s*)?"
                r"(\d{1,3}(?:[.,]\d{3})*|\d+)\s*"
                r"(?:bolsa[s]?|manija[s]?|bobina|total|hicimos|se\s+hizo(?:\s+un)?|"
                r"se\s+hici[eo]ron|se\s+produjo|produjimos|trabajamos|terminamos|"
                r"faltan|pedido|stock)?"
            ),
            re.I,
        )
        # Personas: trabajamos con tres personas, con 3 personas, etc.
        self.p_personas = re.compile(
            (
                r"(?:con\s+|\btrabajamos\s+con\s+)"
                r"(\d+|uno|dos|tres|cuatro|cinco|seis|"
                r"siete|ocho|nueve|diez)\s+personas\b"
            ),
            re.I
        )
        # Turno: turno tarde, turno mañana, etc.
        self.p_turno = re.compile(r"turno\s+(mañana|tarde|noche)", re.I)

    @staticmethod
    def norm_int(num_str: str) -> int:
        "Normaliza una cadena a un entero."
        num_str = num_str.replace(".", "").replace(",", "")
        palabras = {
            "uno": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5,
            "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10
        }
        try:
            return int(num_str)
        except ValueError:
            return palabras.get(num_str.lower(), 0)

    def parse(self, text: str) -> dict:
        "Parses a WhatsApp message and extracts relevant information."
        t = " ".join(text.split())
        out = {}
        if m := self.p_maq.search(t):
            out["maquina"] = m.group(1).lower()
        else:
            logger.debug("No se detectó máquina en: %s", t)
        if m := self.p_formato.search(t):
            out["formato"] = m.group(1)
        else:
            logger.debug("No se detectó formato en: %s", t)
        if m := self.p_turno.search(t):
            out["turno"] = m.group(1).lower()
        if m := self.p_personas.search(t):
            val = m.group(1)
            out["personas"] = self.norm_int(val)

        obs = self._detectar_observaciones()
        if obs:
            out["obs"] = "; ".join(obs)

        cantidades = [self.norm_int(x) for x in self.p_cant_ctx.findall(t)]
        if cantidades:
            out["cantidad"] = max(cantidades)
        else:
            logger.debug("No se detectó cantidad en: %s", t)

        return out if any(out) else {}

    def _detectar_observaciones(self) -> list:
        # Implementa tu lógica de observaciones aquí si es necesario
        return []
