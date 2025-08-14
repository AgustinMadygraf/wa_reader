"""
Path: run.py
"""


import argparse
import logging
from src.common.logging_config import setup_logging
from src.application.whatsapp_monitor import WhatsAppMonitor
from src.adapters.app_config import AppConfig
from src.infrastructure.whatsapp_client import WhatsAppClient
from src.domain.message_processor import MessageProcessor
from src.infrastructure.ingest_service import IngestService
from tabulate import tabulate

def revisar_historial():
    "Revisa el historial de mensajes de WhatsApp y muestra por CLI o envía por API"
    logger = logging.getLogger("wa_reader.historial")
    local_config = AppConfig()
    ingest_service = IngestService(local_config.ingest_url)
    processor = MessageProcessor(local_config)
    try:
        with WhatsAppClient(local_config) as wa_client:
            logger.info("Inicializando cliente de WhatsApp...")
            wa_client.initialize()
            logger.info("Abriendo chat: %s", local_config.chat_name)
            wa_client.open_chat(local_config.chat_name)
            logger.info("Extrayendo historial de mensajes...")
            messages = wa_client.get_messages()
            logger.debug("Total mensajes obtenidos: %d", len(messages))
            procesados = 0
            tabla = []
            for msg in reversed(messages):
                logger.debug("Procesando mensaje: %s %s", msg['meta'], msg['body'][:50])
                try:
                    payload = processor.process(msg)
                except (ValueError, KeyError, TypeError) as e:
                    logger.error("Error procesando mensaje: %s", e)
                    continue
                if payload:
                    if local_config.output_mode == "cli":
                        tabla.append([
                            payload.get("fecha", ""),
                            payload.get("maquina", ""),
                            payload.get("formato", ""),
                            payload.get("cantidad", ""),
                            payload.get("turno", ""),
                            payload.get("personas", ""),
                            payload.get("obs", "")
                        ])
                    else:
                        try:
                            status = ingest_service.send(payload)
                            estado = status if status is not None else "ERROR_RED"
                            if status == 200:
                                logger.info("Enviado correctamente: %s", payload)
                            else:
                                logger.warning("Respuesta inesperada [%s] para: %s", estado, payload)
                        except (ConnectionError, TimeoutError, ValueError) as e:
                            logger.error("Error enviando payload: %s", e)
                    procesados += 1
            if local_config.output_mode == "cli":
                fecha = tabla[0][0] if tabla and tabla[0][0] else "(sin datos)"
                print(f"\nHistorial del chat: {local_config.chat_name} - Fecha: {fecha}\n")
                print(tabulate(
                    tabla,
                    headers=["Fecha", "Máquina", "Formato", "Cantidad", "Turno", "Personas", "Obs"],
                    tablefmt="github",
                    showindex=False
                ))
            logger.info(
                "Historial procesado: %d de %d mensajes revisados.",
                procesados,
                len(messages)
            )
    except (ImportError, AttributeError, RuntimeError) as e:
        logger.error("Error crítico en revisión de historial: %s", e)

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
            revisar_historial()
        else:
            monitor = WhatsAppMonitor(config)
            monitor.run()
    except KeyboardInterrupt:
        print("\nAplicación detenida por el usuario")
    except (ImportError, AttributeError, RuntimeError) as e:
        print(f"Error crítico: {str(e)}")
