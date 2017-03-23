import logging
import logging.handlers
import os
import signal
import sys

from pythonjsonlogger import jsonlogger


CONSOLE_FORMATTER = logging.Formatter('[%(asctime)s] %(levelname)s --- %(message)s ' +
                                      '(%(filename)s:%(lineno)d - %(funcName)s())',
                                      datefmt='%Y-%m-%d %H:%M:%S')

JSON_FORMATTER = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s ' +
                                          '%(filename)s %(module)s %(funcName)s %(lineno)d ',
                                          datefmt='%Y-%m-%d %H:%M:%S')


LOG_HANDLER_CONSOLE = logging.StreamHandler(stream=sys.stdout)
LOG_HANDLER_CONSOLE.setLevel(logging.INFO)
LOG_HANDLER_CONSOLE.setFormatter(CONSOLE_FORMATTER)

LOG_HANDLER_FILE = logging.FileHandler("indus_script_ocr.log", mode="a")
LOG_HANDLER_FILE.setLevel(logging.DEBUG)
LOG_HANDLER_FILE.setFormatter(JSON_FORMATTER)


def create_logger(caller_name):

    logger = logging.getLogger(caller_name)
    logger.propagate = False
    logger.setLevel(int(os.environ["LOG_LEVEL"]))
    logger.addHandler(LOG_HANDLER_CONSOLE)
    logger.addHandler(LOG_HANDLER_FILE)

    return logger


def signal_handler(signal, frame):
    logger = create_logger(__name__)
    logger.info("App terminated!")
    logging.shutdown()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
