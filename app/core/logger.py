import logging.config

logging.basicConfig(filename="logs.log", level=logging.DEBUG, filemode="w")
logger = logging.getLogger(__name__)
