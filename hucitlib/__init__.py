#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Matteo Romanello, matteo.romanello@gmail.com

import logging
from hucitlib.__version__ import str_version
from hucitlib.surfext import *
from hucitlib.kb import KnowledgeBase


def init_logger(log_file_path: str, verbose: bool=False) -> logging.RootLogger:
    logger = logging.getLogger()
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    handler = logging.FileHandler(filename=log_file_path, mode='w')
    formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
