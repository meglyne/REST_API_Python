# app/custom_logger.py

import logging
import logging.config
from logging.handlers import TimedRotatingFileHandler

def init_logger(logpath='/var/log/messaging_api', logname='messaging_api', env=['development', 'production']):
    logging_level = None
    if env == 'development':
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO
    format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger()
    logger.setLevel(logging_level)

    filepath = '{directory}/{filename}'.format(directory=logpath, filename=logname)

    # setting up logger for file change everyday
    rotation_logging_handler = TimedRotatingFileHandler(filename='{}.log'.format(filepath), when='midnight', interval=1)
    rotation_logging_handler.suffix = "%Y-%m-%d"
    rotation_logging_handler.setFormatter(format)

    logger.addHandler(rotation_logging_handler)
    return logger
