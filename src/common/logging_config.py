"""
Path: src/common/logging_config.py
"""

import logging

def setup_logging(debug: bool = False):
    "Configura el logging global del proyecto."
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        #format="%(levelname)s %(filename)s:%(lineno)d [%(name)s] %(asctime)s: %(message)s",
        format="%(levelname)s %(filename)s:%(lineno)d %(message)s",
        datefmt="%H:%M:%S"
    )
