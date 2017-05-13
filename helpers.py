#!/usr/bin/env python3
import logging

from config import *

logs = dict()
def logger(name):
    if logs.get(name):
        return logs[name]
    logs[name] = logging.getLogger(name)
    logs[name].setLevel(logging.DEBUG)
    if not len(logs[name].handlers):
        handler = logging.FileHandler('{}/{}.log'.format(SHRUGGIE_LOG_DIR, name))
        handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
        logs[name].addHandler(handler)
    return logs[name]

def debug(message):
    logger('debug').debug(message)
