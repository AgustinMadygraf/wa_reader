"""
Path: src/Infrastructure/WhatsAppClient.py
"""


import re
import logging
from src_old.shared.app_config import AppConfig
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
        try:
            if self.context:
                self.context.close()
        except Exception as e:
            self.logger.warning("Error cerrando contexto: %s", e)
        try:
            if self.playwright:
                self.playwright.stop()
        except Exception as e:
            self.logger.warning("Error cerrando Playwright: %s", e)

    def initialize(self, login_timeout: int = 120, retry_count: int = 2):
        "Inicializa el cliente de WhatsApp. login_timeout en segundos."
        self.logger.info("Navegando a WhatsApp Web...")

        for attempt in range(1, retry_count + 1):
            try:
                self.page.goto("https://web.whatsapp.com")
                self.logger.debug("Esperando login de usuario (intento %d de %d)...",
                                 attempt, retry_count)
                self._wait_for_login(timeout=login_timeout)
                self.logger.info("Login exitoso en WhatsApp Web.")
                return
            except KeyboardInterrupt:
                self.logger.warning("Interrupción por el usuario durante el login.")
                self._cleanup("interrupción")
                raise
            except RuntimeError as e:
                if attempt < retry_count:
                    self.logger.warning(
                        "Intento %d fallido. Reintentando en 5 segundos...", attempt
                    )
                    self.page.wait_for_timeout(5000)  # Esperar 5 segundos
                    self.page.reload()  # Recargar la página
                else:
                    self.logger.error(
                        "Timeout de login superado después de %d intentos: %s", 
                        retry_count, e
                    )
                    self._cleanup("timeout")
                    raise

    def _cleanup(self, reason: str):
        "Limpia los recursos del cliente."
        if self.context:
            self.context.close()
            self.logger.debug("Contexto cerrado por %s.", reason)
        if self.playwright:
            self.playwright.stop()
            self.logger.debug("Playwright detenido por %s.", reason)

    def _wait_for_login(self, timeout: int = 120):
        "Espera a que el usuario inicie sesión. timeout en segundos."
        # Múltiples selectores para mayor compatibilidad con cambios en la interfaz
        selectors = [
            "div[title='Buscar o empezar un chat'], div[title='Search or start new chat']",
            "[data-testid='chat-list-search']",  # Selector alternativo para el buscador
            "[data-icon='search']",  # Icono de búsqueda
            ".two, .three",  # Selectores para los paneles de WhatsApp Web
            "._1Flk2, ._13NKt"  # Clases comunes del campo de búsqueda
        ]
        self.logger.info("Por favor espere mientras se carga la interfaz de WhatsApp Web...")
        for selector in selectors:
            try:
                self.logger.debug("Intentando selector: %s", selector)
                self.page.wait_for_selector(selector, timeout=10000)  # 10 segundos por selector
                self.logger.info("Login exitoso en WhatsApp Web (selector: %s).", selector)
                return
            except Error:
                self.logger.debug("Selector no encontrado: %s", selector)
                continue
        self.logger.error(
            "No se pudo detectar la interfaz de WhatsApp Web después de %d segundos.",
            timeout
        )
        try:
            screenshot_path = "wa_login_error.png"
            self.page.screenshot(path=screenshot_path)
            self.logger.error("Screenshot guardada en: %s", screenshot_path)
        except Error as e:
            self.logger.error("No se pudo guardar screenshot: %s", e)

        # Verificar si hay QR o ya está en la interfaz
        try:
            if self.page.locator("canvas[aria-label='Scan me!']").count() > 0:
                self.logger.error(
                    "Se detectó un código QR. Por favor escanee el código con su teléfono.")
            elif self.page.locator("[data-testid='chat-list']").count() > 0:
                self.logger.warning(
                    "Se detectó la lista de chats pero no el buscador. Intentando continuar...")
                return
        except Error:
            pass

        self.logger.error("¿WhatsApp Web está cargado correctamente? Verifique la pantalla.")
        raise RuntimeError("No se pudo detectar la interfaz de WhatsApp Web")

    def open_chat(self, chat_name: str):
        "Abre un chat en WhatsApp, buscando en la lista principal y en archivados si es necesario."
        self.logger.info("Buscando y abriendo chat: %s", chat_name)
        try:
            # Buscar el textbox y limpiar antes de escribir
            textbox = self.page.get_by_role("textbox", name=re.compile("Buscar|Search", re.I))
            textbox.click()
            textbox.fill("")  # Limpiar campo
            textbox.type(chat_name, delay=50)
            self.page.wait_for_timeout(1000)  # Esperar resultados
        except Error:
            self.logger.warning("No se pudo interactuar con el textbox de búsqueda, intentando continuar...")

        # Buscar el chat por nombre exacto
        chat_locator = self.page.locator(f"//span[@title='{chat_name}']")
        if chat_locator.count() > 0:
            chat_locator.first.click()
            self.logger.info("Leyendo chat: %s", chat_name)
            return

        self.logger.info("Chat '%s' no encontrado en la lista principal.", chat_name)
        # Buscar en archivados si corresponde
        if getattr(self.config, "chat_archived", False):
            self.logger.info("Buscando en archivados...")
            archived_locator = self.page.locator(
                "//span[contains(text(), 'Archivados') or contains(text(), 'Archived')]")
            if archived_locator.count() > 0:
                archived_locator.first.click()
                self.logger.info("Sección de archivados abierta.")
                self.page.wait_for_timeout(1000)
                # Repetir búsqueda en archivados
                try:
                    textbox = self.page.get_by_role("textbox", name=re.compile("Buscar|Search", re.I))
                    textbox.click()
                    textbox.fill("")
                    textbox.type(chat_name, delay=50)
                    self.page.wait_for_timeout(1000)
                except Error:
                    self.logger.warning("No se pudo usar el textbox en archivados.")
                archived_chat_locator = self.page.locator(f"//span[@title='{chat_name}']")
                if archived_chat_locator.count() > 0:
                    archived_chat_locator.first.click()
                    self.logger.info("Leyendo chat archivado: %s", chat_name)
                    return
                else:
                    self.logger.error("El chat '%s' no se encuentra en archivados.", chat_name)
            else:
                self.logger.error("No se encontró la sección de archivados en WhatsApp Web.")
        else:
            self.logger.info("No se buscará en archivados porque chat_archived=False.")

        # Si llega aquí, no se encontró el chat
        self.logger.error("No se pudo encontrar el chat '%s'. Deteniendo ejecución.", chat_name)
        raise RuntimeError(f"No se pudo encontrar el chat '{chat_name}' en WhatsApp Web.")

    def get_messages(self) -> list[dict]:
        "Obtiene los mensajes del chat."
        self.logger.info("Extrayendo mensajes del chat...")
        messages = []
        bubbles = self.page.locator("div[role='row'] div.copyable-text")
        count = bubbles.count()
        self.logger.debug("Cantidad de burbujas encontradas: %d", count)

        for i in range(count):
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
