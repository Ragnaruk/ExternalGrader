import logging

import pika.exceptions

from src.receive_messages import receive_messages
from src.send_message import send_message


def main() -> None:
    """
    Initialize logger and start listening to messages from broker.
    """
    logging.basicConfig(
        filename="grader.log",
        level=logging.INFO,
        filemode="w",
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")

    try:
        send_message("localhost", 32769, "student_answers", "student_grades",
                     "{'command': 'touch hello_world.txt', 'solution_id': 1, 'student_id': 1}")

        receive_messages("localhost", 32769, "student_answers")
    except pika.exceptions.AMQPConnectionError:
        logging.getLogger("ExternalGrader").error("Failed to connect to RabbitMQ broker.")
        receive_messages("localhost", 32769, "student_answers")
    except KeyboardInterrupt:
        logging.getLogger("ExternalGrader").info("Program has been stopped manually.")
    except Exception as exception:
        logging.getLogger("ExternalGrader").error(exception)


if __name__ == "__main__":
    main()
