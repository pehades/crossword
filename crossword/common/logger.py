import logging
import sys

LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s: %(message)s'


def create_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    # getLogger returns the same logger for the same name, so add the handler only once
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(handler)
    return logger
