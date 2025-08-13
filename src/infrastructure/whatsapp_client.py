"""
Path: src/Infrastructure/WhatsAppClient.py
"""


import re
import logging
from src.adapters.app_config import AppConfig
from playwright.sync_api import sync_playwright  # noqa: E402
from playwright.sync_api import Error  # noqa: E402


class WhatsAppClient:
    "Cliente de WhatsApp"
    def __init__(self, config: AppConfig):
        self.config = config
        self.playwright = None
        self.context = None
        self.page = None
        self.logger = logging.getLogger("wa_reader.whatsapp_client")

    def __enter__(self):
        self.logger.info("Iniciando Playwright y contexto de navegador...")
        self.playwright = sync_playwright().start()
        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.config.user_data,
            headless=self.config.headless
        )
        self.page = self.context.new_page()
        self.logger.debug(
            "Contexto lanzado con user_data_dir=%s, headless=%s",
            self.config.user_data,
            self.config.headless
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.info("Cerrando contexto y Playwright...")
        if self.context:
            self.context.close()
            self.logger.debug("Contexto cerrado.")
        if self.playwright:
            self.playwright.stop()
            self.logger.debug("Playwright detenido.")

    def initialize(self):
        "Inicializa el cliente de WhatsApp."
        self.logger.info("Navegando a WhatsApp Web...")
        self.page.goto("https://web.whatsapp.com")
        self.logger.debug("Esperando login de usuario...")
        try:
            self._wait_for_login()
        except KeyboardInterrupt:
            self.logger.warning("Interrupción por el usuario durante el login. Cerrando recursos...")
            if self.context:
                self.context.close()
                self.logger.debug("Contexto cerrado por interrupción.")
            if self.playwright:
                self.playwright.stop()
                self.logger.debug("Playwright detenido por interrupción.")
            raise

    def _wait_for_login(self):
        "Espera a que el usuario inicie sesión."
        selector = "div[title='Buscar o empezar un chat'], div[title='Search or start new chat']"
        self.logger.debug("Esperando selector de login: %s", selector)
        try:
            # wait_for_selector espera a que el elemento esté presente en el DOM y sea visible.
            # Es útil para sincronizar la automatización con el estado de la página.
            self.page.wait_for_selector(
                selector,
                timeout=120000
            )
            self.logger.info("Login exitoso en WhatsApp Web.")
        except Error as exc:
            self.logger.error("No se cargó WhatsApp Web a tiempo. ¿Escaneaste el QR?")
            self.logger.debug("Error en wait_for_selector: %s", exc)
            raise RuntimeError("No se cargó WhatsApp Web a tiempo. ¿Escaneaste el QR?") from exc

    def open_chat(self, chat_name: str):
        "Abre un chat en WhatsApp."
        self.logger.info("Buscando y abriendo chat: %s", chat_name)
        try:
            self.page.get_by_role("textbox", name=re.compile("Buscar|Search", re.I)).click()
        except Error:
            self.logger.warning(
                "No se pudo hacer click en el textbox de búsqueda, "
                "intentando continuar..."
            )
        self.page.locator(f"//span[@title='{chat_name}']").first.click()
        self.logger.info("Leyendo chat: %s", chat_name)

    def get_messages(self) -> list[dict]:
        "Obtiene los mensajes del chat."
        self.logger.info("Extrayendo mensajes del chat...")
        messages = []
        bubbles = self.page.locator("div[role='row'] div.copyable-text")
        count = bubbles.count()
        self.logger.debug("Cantidad de burbujas encontradas: %d", count)

        for i in range(max(0, count - 40), count):
            try:
                element = bubbles.nth(i)
                meta = element.get_attribute("data-pre-plain-text") or ""
                body = element.inner_text().strip()
                messages.append({"meta": meta, "body": body})
                self.logger.debug("Mensaje extraído: meta=%s, body=%s", meta, body[:30])
            except (Error, RuntimeError) as e:
                self.logger.warning("Error extrayendo mensaje en posición %d: %s", i, e)
                continue
        self.logger.info("Total mensajes extraídos: %d", len(messages))
        return messages
