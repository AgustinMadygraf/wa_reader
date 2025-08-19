"""
Path: src/entities/message_parser.py
"""

import re

from src.entities.interfaces import IMessageParser

class MessageParser(IMessageParser):
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
        # Almacena el texto original del mensaje para observaciones
        self._texto_original = ""
        # Patrones para tareas pendientes y finalizadas
        self.p_tarea_pendiente = re.compile(r"\b(hay que|pendiente|falta|para mañana|por hacer|debe|debería|recordar|no olvidar)\b", re.I)
        self.p_tarea_finalizada = re.compile(r"\b(terminado|finalizado|listo|completado|hecho|resuelto|cerrado|solucionado|ok|realizado)\b", re.I)

    @staticmethod
    def norm_int(num_str: str) -> int:
        "Normaliza una cadena a un entero."
        num_str = num_str.replace(".", "").replace(",", "")
        try:
            return int(num_str)
        except ValueError:
            palabras = {"uno": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5}
            return palabras.get(num_str.lower(), 0)

    def parse(self, text: str) -> dict:
        "Parses a WhatsApp message and extracts relevant information."
        t = " ".join(text.split())
        self._texto_original = text  # Guarda el texto original para observaciones
        out = {}
        if m := self.p_maq.search(t):
            out["maquina"] = m.group(1).lower()
        if m := self.p_formato.search(t):
            out["formato"] = m.group(1)
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

        return out if any(out) else {}

    def _detectar_observaciones(self) -> list:
        "Detecta observaciones usando el texto original del mensaje."
        texto = getattr(self, "_texto_original", "")
        t = " ".join(texto.split())
        observaciones = []
        # Detectar tarea finalizada
        if self.p_tarea_finalizada.search(t):
            observaciones.append("Tarea Finalizada")
        # Detectar tarea pendiente (permite ambas en el mismo mensaje)
        if self.p_tarea_pendiente.search(t):
            observaciones.append("Tarea Pendiente")
        # Si no se detecta ninguna categoría relevante, asigna 'Sin clasificar'
        tiene_maquina = bool(self.p_maq.search(t))
        tiene_formato = bool(self.p_formato.search(t))
        tiene_cantidad = bool(self.p_cant_ctx.search(t))
        if not (tiene_maquina or tiene_formato or tiene_cantidad) and not observaciones:
            observaciones.append("Sin clasificar")
        return observaciones
