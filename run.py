"""
Path: run.py
"""

import argparse
from datetime import datetime

from src.shared.logging_config import setup_logging
from src.shared.app_config import AppConfig

from src.entities.message_parser import MessageParser
from src.entities.strategies import ObservacionTareaStrategy
from src.entities.meta_parser import MetaParser
from src.uses_cases.message_processor import MessageProcessor
from src.application.historial_service import HistorialService
from src.application.whatsapp_monitor import WhatsAppMonitor
from src.interface_adapters.gateways.ingest_service import IngestService
from src.interface_adapters.gateways.whatsapp_client import WhatsAppClient
from src.interface_adapters.presenters.historial_presenter import HistorialPresenter

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor y revisión de historial de WhatsApp")
    parser.add_argument("--monitor", action="store_true", help="Inicia el monitor en tiempo real")
    parser.add_argument("--historial", action="store_true", help="Revisa el historial de mensajes")
    parser.add_argument("--debug", action="store_true", help="Habilita logging DEBUG")
    parser.add_argument("--output-mode", choices=["cli", "api"],
                        default="cli", help="Modo de salida")
    import sys
    args = parser.parse_args()
    # Si no se pasa ningún argumento, usar --historial por defecto
    if len(sys.argv) == 1:
        args.historial = True

    setup_logging(debug=args.debug)

    config = AppConfig()
    config.output_mode = args.output_mode

    # Instanciar la estrategia personalizada para análisis de mensajes
    base_parser = MessageParser()
    estrategia = ObservacionTareaStrategy(base_parser)

    def get_fecha():
        "Obtiene la fecha actual formateada"
        return datetime.now(config.tz_local).strftime("%Y-%m-%d")

    try:
        if args.historial:
            # Cargar roles de autor desde archivo
            import json
            try:
                with open(config.author_roles_path, encoding="utf-8") as f:
                    author_roles = json.load(f)
            except (OSError, json.JSONDecodeError):
                author_roles = {}

            meta_parser = MetaParser(author_roles)
            presenter = HistorialPresenter(meta_parser)
            ingest_service = IngestService(config.ingest_url)
            wa_client = WhatsAppClient(
                user_data_dir=config.user_data,
                headless=config.headless,
                chat_archived=getattr(config, 'chat_archived', False)
            )
            processor = MessageProcessor(get_fecha, parser_strategy=estrategia)
            HistorialService(
                config,
                wa_client=wa_client,
                ingest_service=ingest_service,
                presenter=presenter,
                meta_parser=meta_parser,
                processor=processor
            ).revisar()
        else:
            ingest_service = IngestService(config.ingest_url)
            wa_client = WhatsAppClient(
                user_data_dir=config.user_data,
                headless=config.headless,
                chat_archived=getattr(config, 'chat_archived', False)
            )
            # Cargar roles de autor desde archivo
            import json
            try:
                with open(config.author_roles_path, encoding="utf-8") as f:
                    author_roles = json.load(f)
            except (OSError, json.JSONDecodeError):
                author_roles = {}

            meta_parser = MetaParser(author_roles)
            monitor = WhatsAppMonitor(
                config,
                ingest_service=ingest_service,
                wa_client=wa_client,
                processor=MessageProcessor(get_fecha, parser_strategy=estrategia)
            )
            monitor.meta_parser = meta_parser  # <--- Asignar MetaParser aquí
            monitor.run()
    except KeyboardInterrupt:
        print("\nAplicación detenida por el usuario")
    except (ImportError, AttributeError, RuntimeError) as e:
        print(f"Error crítico: {str(e)}")
