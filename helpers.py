#!/usr/bin/env python3
import logging

logs = dict()
def logger(name):
    if logs.get(name):
        return logs[name]
    logs[name] = logging.getLogger(name)
    logs[name].setLevel(logging.DEBUG)
    if not len(logs[name].handlers):
        handler = logging.FileHandler('/home/_shruggie/logs/{}.log'.format(name))
        handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
        logs[name].addHandler(handler)
    return logs[name]

def debug(message):
    logger('debug').info(message)
