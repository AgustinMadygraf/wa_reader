"""
Path: src/Domain/MessageParser.py
"""


class MessageParser:
    "Parser de mensajes de WhatsApp"
    def __init__(self):
        self.P_FORMATO = re.compile(r"\b(\d{2}x\d{2}x\d{2})\b", re.I)
        self.P_MAQ = re.compile(r"maquin[ao]\s+(?:de\s+)?(bolsas|manijas)", re.I)
        self.P_TURNO = re.compile(r"turno\s+(mañana|tarde|noche)", re.I)
        self.P_PERSONAS = re.compile(r"\bcon\s+(\d+)\s+personas\b", re.I)
        self.P_PROBLEMA = re.compile(r"problema[s]?\s+con\s+(.+?)(?:\.|,|;|$)", re.I)
        self.P_CANT_CTX = re.compile(
            r"(\d{1,3}(?:[.,]\d{3})*|\d+)\s*"
            r"(?:bolsa[s]?|manija[s]?|total|hicimos|se\s+hizo(?:\s+un)?|"
            r"produc[ií]mos|se\s+produjo|se\s+hici[eo]ron)",
            re.I,
        )

    @staticmethod
    def norm_int(num_str: str) -> int:
        "Normaliza una cadena a un entero."
        return int(num_str.replace('.', '').replace(',', ''))

    def parse(self, text: str) -> dict:
        "Parses a WhatsApp message and extracts relevant information."
        t = " ".join(text.split())
        out = {}
        if m := self.P_MAQ.search(t):
            out["maquina"] = m.group(1).lower()
        if m := self.P_FORMATO.search(t):
            out["formato"] = m.group(1)
        if m := self.P_TURNO.search(t):
            out["turno"] = m.group(1).lower()
        if m := self.P_PERSONAS.search(t):
            out["personas"] = int(m.group(1))
        
        # Detección de observaciones
        obs = self._detectar_observaciones(t)
        if obs:
            out["obs"] = "; ".join(obs)
        
        # Detección de cantidades
        if cantidades := [self.norm_int(x) for x in self.P_CANT_CTX.findall(t)]:
            out["cantidad"] = max(cantidades)
        
        return out if any(out) else {}

    def _detectar_observaciones(self, text: str) -> list:
        obs = []
        text_lower = text.lower()

        if m := self.P_PROBLEMA.search(text_lower):
            obs.append(f"Problemas con {m.group(1).strip()}")
        if any(x in text_lower for x in ["montamos bobina", "monté bobina", "montar bobina"]):
            obs.append("Montamos bobina")
        if "cambiar de formato" in text_lower or "cambio de formato" in text_lower:
            if m := self.P_FORMATO.search(text_lower):
                obs.append(f"Cambio de formato a {m.group(1)}")
            else:
                obs.append("Cambio de formato")
        return obs
