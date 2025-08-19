"""
Path: src/adapters/app_config.py
"""

from dateutil import tz

class AppConfig:
    "Configuración de la aplicación"
    def __init__(self):
        self.chat_name = "Operadores de bolsa"
        self.ingest_url = "http://127.0.0.1/ingesta"
        self.headless = False
        self.user_data = "./wa_profile"
        self.poll_sec = 5
        self.tz_local = tz.gettz("America/Argentina/Buenos_Aires")
        self.chat_archived = False
        self.output_mode = "cli"
        self.author_roles_path = "./src/shared/author_roles.json"
