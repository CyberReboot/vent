import logging
import os

from vent.helpers.paths import PathDirs

def Logger(name, **kargs):
    """ Create and return logger """
    path_dirs = PathDirs(**kargs)
    logging.captureWarnings(True)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(os.path.join(path_dirs.meta_dir, "vent.log"))
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    if not len(logger.handlers):
        logger.addHandler(handler)
    return logger
