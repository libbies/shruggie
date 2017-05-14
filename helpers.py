#!/usr/bin/env python3
import logging

from config import *

logs = dict()
def logger(name):
    if logs.get(name):
        return logs[name]
    logs[name] = logging.getLogger(name)
    # FIXME: SHRUGGIE_LOG_LVL doesn't quite work right...
    #   the log() function writes to the debug log file despite this setting
    logs[name].setLevel(logging.INFO if name else SHRUGGIE_LOG_LVL)
    if not len(logs[name].handlers):
        handler = logging.FileHandler('{}/{}.log'.format(SHRUGGIE_LOG_DIR,
            name if name else 'debug')
        )
        handler.setFormatter(logging.Formatter('[%(asctime)s] %(message)s'))
        logs[name].addHandler(handler)
    return logs[name]

def debug(message):
    logger(None).debug(message)

def log(name, message):
    logger(name).info(message)
