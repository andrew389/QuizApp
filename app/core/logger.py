import logging.config

logging.basicConfig(filename="logs.txt", level=logging.DEBUG, filemode="w")
logger = logging.getLogger(__name__)
