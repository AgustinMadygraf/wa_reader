"""
Path: src/Adapters/AppConfig.py
"""

class AppConfig:
    def __init__(self):
        self.CHAT_NAME = "Producción Mady"
        self.INGEST_URL = "http://127.0.0.1/ingesta"
        self.HEADLESS = False
        self.USER_DATA = "./wa_profile"
        self.POLL_SEC = 5
        self.TZ_LOCAL = tz.gettz("America/Argentina/Buenos_Aires")
