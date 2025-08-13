"""
Path: run.py
"""

import argparse
from src.application.whatsapp_monitor import WhatsAppMonitor
from src.adapters.app_config import AppConfig

def revisar_historial():
    "Revisa el historial de mensajes de WhatsApp"
    print("[TODO] Revisar historial no implementado aún.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor y revisión de historial de WhatsApp")
    parser.add_argument("--monitor", action="store_true", help="Inicia el monitor en tiempo real")
    parser.add_argument("--historial", action="store_true", help="Revisa el historial de mensajes")
    args = parser.parse_args()

    config = AppConfig()
    try:
        if args.historial:
            revisar_historial()
        else:
            monitor = WhatsAppMonitor(config)
            monitor.run()
    except KeyboardInterrupt:
        print("\nAplicación detenida por el usuario")
    except (ImportError, AttributeError, RuntimeError) as e:
        print(f"Error crítico: {str(e)}")
