#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import logging

logger = None
PATTERN = '%(asctime)s::%(levelname)s:: %(message)s'
TIME_PATTERN = '-%Y%m%d-%H%M%S'
LOG_FILE = None

def now():
    return time.strftime(TIME_PATTERN)

def init_logger(path):
    global logger, LOG_FILE
    if logger:
        return logger
    LOG_FILE = path
    logger = logging.getLogger(__name__)
    sh = logging.StreamHandler()
    fh = logging.FileHandler(LOG_FILE)
    formatter = logging.Formatter(PATTERN)
    sh.setFormatter(formatter)
    fh.setFormatter(formatter)
    logger.addHandler(sh)
    logger.addHandler(fh)
    logger.setLevel(logging.DEBUG)
    logger.info('logfile: {}'.format(LOG_FILE))
    return logger
