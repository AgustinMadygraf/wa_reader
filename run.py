"""
Path: run.py
"""

from src.application.whatsapp_monitor import WhatsAppMonitor
from src.adapters.app_config import AppConfig

if __name__ == "__main__":
    try:
        monitor = WhatsAppMonitor(AppConfig())
        monitor.run()
    except KeyboardInterrupt:
        print("\nAplicación detenida por el usuario")
    except (ImportError, AttributeError, RuntimeError) as e:
        print(f"Error crítico: {str(e)}")
