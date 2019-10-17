"""
PyTest test file for config_queue.* modules.
"""
import glob
import importlib
from os.path import dirname, basename, isfile, join

import config_queue


def test_queue_configs():
    """
    Test config_queue.* files.
    """
    modules = glob.glob(join(dirname(config_queue.__file__), "*.py"))
    names = [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]

    # Import all files in config_queue module and check whether expected variables exist
    for name in names:
        config = importlib.import_module("config_queue." + name)

        assert config.TYPE
        assert config.HOST
        assert config.PORT
        assert config.USER
        assert config.PASS
        assert config.QUEUE
