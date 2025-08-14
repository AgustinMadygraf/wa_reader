"""
Path: run.py
"""

import argparse
from src.common.logging_config import setup_logging
from src.application.whatsapp_monitor import WhatsAppMonitor
from src.application.historial_service import HistorialService
from src.adapters.app_config import AppConfig

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor y revisión de historial de WhatsApp")
    parser.add_argument("--monitor", action="store_true", help="Inicia el monitor en tiempo real")
    parser.add_argument("--historial", action="store_true", help="Revisa el historial de mensajes")
    parser.add_argument("--debug", action="store_true", help="Habilita logging DEBUG")
    args = parser.parse_args()

    setup_logging(debug=args.debug)

    config = AppConfig()
    try:
        if args.historial:
            HistorialService(config).revisar()
        else:
            monitor = WhatsAppMonitor(config)
            monitor.run()
    except KeyboardInterrupt:
        print("\nAplicación detenida por el usuario")
    except (ImportError, AttributeError, RuntimeError) as e:
        print(f"Error crítico: {str(e)}")
