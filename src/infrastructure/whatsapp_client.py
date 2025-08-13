"""
Path: src/Infrastructure/WhatsAppClient.py
"""


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
