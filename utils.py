import os
import logging


def ensure_dir_exists(dirname):
    if not os.path.isdir(dirname):
        logging.debug(f'Creating {dirname} directory')
        os.makedirs(dirname)

