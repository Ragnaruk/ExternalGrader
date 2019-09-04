import logging
from time import sleep

import pika.exceptions

from external_grader.receive_messages import receive_messages
from external_grader.config import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_CONSUMPTION_QUEUE


def start_grader() -> None:
    """
    Initialize logger and start listening to messages from broker.
    """
    logging.basicConfig(
        filename="grader.log",
        level=logging.INFO,
        filemode="w",
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")

    while True:
        try:
            receive_messages(RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_CONSUMPTION_QUEUE)
        except pika.exceptions.AMQPConnectionError:
            logging.getLogger("ExternalGrader").error("Failed to connect to RabbitMQ broker.")
        except KeyboardInterrupt:
            logging.getLogger("ExternalGrader").info("Program has been stopped manually.")
        except Exception as exception:
            logging.getLogger("ExternalGrader").error(exception)

        sleep(10)


if __name__ == "__main__":
    start_grader()
