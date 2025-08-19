"""
Path: src/common/logging_config.py
"""

import logging

def setup_logging(debug: bool = False):
    "Configura el logging global del proyecto."
    level = logging.DEBUG if debug else logging.INFO
    if debug:
        # Incluye minutos y segundos entre levelname y filename
        fmt = "%(levelname)s %(asctime)s %(filename)s:%(lineno)d %(message)s"
        datefmt = "%M:%S"
    else:
        fmt = "%(levelname)s %(asctime)s %(filename)s:%(lineno)d %(message)s"
        datefmt = "%H:%M:%S"
    logging.basicConfig(
        level=level,
        format=fmt,
        datefmt=datefmt
    )
