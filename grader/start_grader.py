from time import sleep

import pika.exceptions

from config.config import CONNECTION_RETRY_TIME
from grader.logs import get_logger
from grader.message_brokers.rabbitmq import receive_messages
from utils.decorators import log_exceptions


@log_exceptions
def start_grader() -> None:
    """
    Initialize logger and start listening to messages from broker.
    """
    while True:
        listen_to_broker()
        sleep(CONNECTION_RETRY_TIME)


@log_exceptions
def listen_to_broker():
    """
    Listen to chosen message broker.
    """
    logger = get_logger("start_grader")

    try:
        receive_messages()
    except pika.exceptions.AMQPConnectionError:
        logger.error("Failed to connect to RabbitMQ broker.")
    except pika.exceptions:
        logger.error("Failed to connect to RabbitMQ broker.")
    except KeyboardInterrupt:
        logger.info("Program has been stopped manually.")


if __name__ == "__main__":
    start_grader()
