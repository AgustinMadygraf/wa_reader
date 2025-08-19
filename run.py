"""
Path: run.py
"""

import argparse
from src_old.shared.logging_config import setup_logging

from src_old.application.whatsapp_monitor import WhatsAppMonitor
from src_old.infrastructure.ingest_service import IngestService
from src_old.infrastructure.whatsapp_client import WhatsAppClient
from src_old.application.historial_service import HistorialService
from src_old.shared.app_config import AppConfig
from src_old.domain.message_parser import MessageParser
from src_old.domain.strategies import ObservacionTareaStrategy
from src_old.domain.message_processor import MessageProcessor

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor y revisión de historial de WhatsApp")
    parser.add_argument("--monitor", action="store_true", help="Inicia el monitor en tiempo real")
    parser.add_argument("--historial", action="store_true", help="Revisa el historial de mensajes")
    parser.add_argument("--debug", action="store_true", help="Habilita logging DEBUG")
    parser.add_argument("--output-mode", choices=["cli", "api"],
                        default="cli", help="Modo de salida")
    args = parser.parse_args()

    setup_logging(debug=args.debug)

    config = AppConfig()
    config.output_mode = args.output_mode

    # Instanciar la estrategia personalizada para análisis de mensajes
    base_parser = MessageParser()
    estrategia = ObservacionTareaStrategy(base_parser)

    try:
        if args.historial:
            HistorialService(
                config,
                processor=MessageProcessor(
                    config,
                    parser_strategy=estrategia
                )
            ).revisar()
        else:
            ingest_service = IngestService(config.ingest_url)
            wa_client = WhatsAppClient(config)
            monitor = WhatsAppMonitor(
                config,
                ingest_service=ingest_service,
                wa_client=wa_client,
                processor=MessageProcessor(config, parser_strategy=estrategia)
            )
            monitor.run()
    except KeyboardInterrupt:
        print("\nAplicación detenida por el usuario")
    except (ImportError, AttributeError, RuntimeError) as e:
        print(f"Error crítico: {str(e)}")
