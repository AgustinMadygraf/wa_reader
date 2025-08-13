"""
Path: run.py
"""

import hashlib
import re
import time
from datetime import datetime
from urllib.parse import urlencode
import requests
from dateutil import tz
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

class AppConfig:
    def __init__(self):
        self.CHAT_NAME = "Producción Mady"
        self.INGEST_URL = "http://127.0.0.1/ingesta"
        self.HEADLESS = False
        self.USER_DATA = "./wa_profile"
        self.POLL_SEC = 5
        self.TZ_LOCAL = tz.gettz("America/Argentina/Buenos_Aires")


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

class IngestService:
    "Servicio de Ingesta"
    def __init__(self, endpoint: str):
        self.endpoint = endpoint
    
    def send(self, payload: dict) -> int | None:
        "Envía un payload al servicio de ingesta."
        clean_payload = {k: v for k, v in payload.items() if v not in (None, "", [])}
        try:
            response = requests.get(self.endpoint, params=clean_payload, timeout=5)
            return response.status_code
        except requests.RequestException:
            return None

class WhatsAppClient:
    "Cliente de WhatsApp"
    def __init__(self, config: AppConfig):
        self.config = config
        self.playwright = None
        self.context = None
        self.page = None
    
    def __enter__(self):
        self.playwright = sync_playwright().start()
        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.config.USER_DATA,
            headless=self.config.HEADLESS
        )
        self.page = self.context.new_page()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.context:
            self.context.close()
        if self.playwright:
            self.playwright.stop()
    
    def initialize(self):
        self.page.goto("https://web.whatsapp.com")
        self._wait_for_login()
    
    def _wait_for_login(self):
        try:
            self.page.wait_for_selector(
                "div[title='Buscar o empezar un chat'], div[title='Search or start new chat']",
                timeout=120000
            )
        except PWTimeout:
            raise RuntimeError("No se cargó WhatsApp Web a tiempo. ¿Escaneaste el QR?")
    
    def open_chat(self, chat_name: str):
        try:
            self.page.get_by_role("textbox", name=re.compile("Buscar|Search", re.I)).click()
        except PWTimeout:
            pass
        self.page.locator(f"//span[@title='{chat_name}']").first.click()
        print(f"[OK] Leyendo chat: {chat_name}")
    
    def get_messages(self) -> list[dict]:
        messages = []
        bubbles = self.page.locator("div[role='row'] div.copyable-text")
        count = bubbles.count()
        
        for i in range(max(0, count - 40), count):
            try:
                element = bubbles.nth(i)
                meta = element.get_attribute("data-pre-plain-text") or ""
                body = element.inner_text().strip()
                messages.append({"meta": meta, "body": body})
            except (PWTimeout, RuntimeError):
                continue
        return messages

class WhatsAppMonitor:
    "Monitor de WhatsApp"
    def __init__(self, config: AppConfig):
        self.config = config
        self.parser = MessageParser()
        self.ingest_service = IngestService(config.INGEST_URL)
        self.seen_messages = set()

    def process_message(self, message: dict) -> dict | None:
        """Procesa un mensaje y devuelve payload si es válido"""
        key = hashlib.sha1((message["meta"] + "\n" + message["body"]).encode("utf-8")).hexdigest()
        if key in self.seen_messages:
            return None

        self.seen_messages.add(key)
        parsed = self.parser.parse(message["body"])
        if not parsed:
            return None

        return {
            "fecha": datetime.now(self.config.TZ_LOCAL).strftime("%Y-%m-%d"),
            "maquina": parsed.get("maquina", ""),
            "formato": parsed.get("formato", ""),
            "cantidad": parsed.get("cantidad", 0),
            "turno": parsed.get("turno", ""),
            "personas": parsed.get("personas", ""),
            "obs": parsed.get("obs", "")
        }

    def run(self):
        "Ejecuta el monitor de WhatsApp."
        with WhatsAppClient(self.config) as wa_client:
            wa_client.initialize()
            wa_client.open_chat(self.config.CHAT_NAME)
            
            while True:
                messages = wa_client.get_messages()
                for msg in messages:
                    if payload := self.process_message(msg):
                        status = self.ingest_service.send(payload)
                        estado = status if status is not None else "ERROR_RED"
                        print(f"→ GET {self.config.INGEST_URL}?{urlencode(payload)}  [{estado}]")
                time.sleep(self.config.POLL_SEC)

if __name__ == "__main__":
    try:
        monitor = WhatsAppMonitor(AppConfig())
        monitor.run()
    except KeyboardInterrupt:
        print("\nAplicación detenida por el usuario")
    except Exception as e:
        print(f"Error crítico: {str(e)}")