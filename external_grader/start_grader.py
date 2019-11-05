from time import sleep
from typing import Any
from os import getenv

import pika.exceptions
import epicbox.exceptions
import requests.exceptions
import importlib
import socket

from external_grader.config import CONNECTION_RETRY_TIME, QUEUE_CONFIG_NAME
from external_grader.logs import get_logger
from external_grader.broker_handlers.rabbitmq import (
    receive_messages as rabbitmq_receive,
)
from external_grader.broker_handlers.xqueue import receive_messages as xqueue_receive


def start_grader() -> None:
    """
    Start main grader loop.
    """
    logger = get_logger("start_grader")

    try:
        queue_config_name = getenv("QUEUE_CONFIG_NAME", QUEUE_CONFIG_NAME)

        try:
            queue_config = importlib.import_module(
                "queue_configuration." + queue_config_name
            )
        except ModuleNotFoundError:
            logger.error("Queue config with name: %s not found.", queue_config_name)
        else:
            while True:
                listen_to_broker(queue_config)
                sleep(CONNECTION_RETRY_TIME)
    except AttributeError as exception:
        logger.error(exception, exc_info=True)
    except epicbox.exceptions.DockerError as exception:
        logger.error("Docker error: \n%s.", exception)
    except socket.gaierror:
        logger.error("Unknown host name in queue configuration file.")
    except KeyboardInterrupt:
        logger.info("Program has been stopped manually.")
    except Exception as exception:
        logger.error("Unhandled exception: \n%s.", exception, exc_info=True)


def listen_to_broker(queue_config: Any):
    """
    Listen to chosen message broker.

    :param queue_config: Module containing queue config.
    """
    logger = get_logger("start_grader")

    if queue_config.TYPE == "rabbitmq":
        try:
            rabbitmq_receive(
                queue_config.HOST,
                queue_config.PORT,
                queue_config.USER,
                queue_config.PASS,
                queue_config.QUEUE,
            )
        except pika.exceptions.AMQPConnectionError as exception:
            logger.error("Failed to connect to RabbitMQ broker. %s", exception)
    elif queue_config.TYPE == "xqueue":
        try:
            xqueue_receive(
                queue_config.HOST,
                queue_config.USER,
                queue_config.PASS,
                queue_config.QUEUE,
                queue_config.POLLING_INTERVAL,
            )
        except requests.exceptions.ConnectionError as exception:
            logger.error("Failed to connect to XQueue broker. %s", exception)
    else:
        logger.error("Unknown message broker type: %s", queue_config.TYPE)


if __name__ == "__main__":
    start_grader()
