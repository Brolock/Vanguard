import logging
import sys

FORMAT = logging.Formatter("%(asctime)s %(levelname)s: %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p")

def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMAT)
    console_handler.setLevel(logging.DEBUG)
    return console_handler

def get_file_handler(logfile: str):
    file_handler = logging.FileHandler(logfile)
    file_handler.setFormatter(FORMAT)
    file_handler.setLevel(logging.INFO)
    return file_handler

def get_logger(logfile: str, logger_name: str = "scrapper_logger"):
    logger = logging.getLogger("scrapper_logger")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler(logfile))

    logger.propagate = False
    return logger
