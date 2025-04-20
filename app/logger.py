import logging

logger = logging.getLogger("news-api")
logger.setLevel(logging.DEBUG)

# Console Handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Formatter
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s")
console_handler.setFormatter(formatter)

# Avoid duplicate logs
if not logger.hasHandlers():
    logger.addHandler(console_handler)
