"""
PyTest test file for queue_configuration.* modules.
"""
import glob
import importlib
from os.path import dirname, basename, isfile, join

import queue_configuration


def test_queue_configs():
    """
    Test queue_configuration.* files.
    """
    modules = glob.glob(join(dirname(queue_configuration.__file__), "*.py"))
    names = [
        basename(f)[:-3] for f in modules if isfile(f) and not f.endswith("__init__.py")
    ]

    # Import all files in queue_configuration module and check whether expected variables exist
    for name in names:
        config = importlib.import_module("queue_configuration." + name)

        assert config.TYPE in ["rabbitmq", "xqueue"]

        if config.TYPE == "rabbitmq":
            assert config.HOST
            assert config.PORT
            assert config.USER
            assert config.PASS
            assert config.QUEUE
        # elif config.TYPE == "xqueue":
        else:
            assert config.HOST
            assert config.USER
            assert config.PASS
            assert config.QUEUE
            assert config.POLLING_INTERVAL
