__all__ = ['getLogger']

import os
import logging
import logging.config
from pathlib import Path

conf = Path(__file__).parent / 'logging.conf'

_initialized = False


def _postpone_config():
    """Postpone loading config once common.logging is initialized

    loading ColoredFormatter from logging.conf file throws error without this workaround"""
    global _initialized
    if _initialized:
        return

    logging.config.fileConfig(conf, disable_existing_loggers=False)
    _initialized = True


def getLogger(name=None):
    _postpone_config()
    return logging.getLogger(name)


if os.environ.get("ROS_ROOT") is not None:
    os.environ["ROS_PYTHON_LOG_CONFIG_FILE"] = str(conf.resolve())
    _initialized = True
