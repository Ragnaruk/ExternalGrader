from time import sleep

import pika.exceptions

from external_grader.config.config import CONNECTION_RETRY_TIME, MESSAGE_BROKER
from external_grader.grader.logs import get_logger
from external_grader.grader.message_brokers.rabbitmq import receive_messages
from external_grader.utils.decorators import log_exceptions


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
        if MESSAGE_BROKER.TYPE == "rabbitmq":
            try:
                receive_messages(
                    MESSAGE_BROKER.HOST,
                    MESSAGE_BROKER.PORT,
                    MESSAGE_BROKER.USER,
                    MESSAGE_BROKER.PASS,
                    MESSAGE_BROKER.QUEUE,
                )
            except pika.exceptions.AMQPConnectionError:
                logger.error("Failed to connect to RabbitMQ broker.")
            except KeyboardInterrupt:
                logger.info("Program has been stopped manually.")
            except Exception as exception:
                logger.error("Unhandled exception: %s.", exception, exc_info=True)
    except AttributeError as exception:
        logger.error(exception, exc_info=True)


if __name__ == "__main__":
    start_grader()
