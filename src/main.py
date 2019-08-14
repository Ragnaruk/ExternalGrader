from src.receive_messages import receive_messages
from src.send_message import send_message

import logging
import pika.exceptions


def main() -> None:
    logging.basicConfig(
        filename="grader.log",
        level=logging.INFO,
        filemode="w",
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")

    try:
        send_message("localhost", 32769, "student_answers", "student_grades",
                     "{'command': 'touch hello_world.txt', 'solution_id': 1, 'student_id': 1}")
        receive_messages("localhost", 32769, "student_answers")
    except pika.exceptions.AMQPConnectionError as e:
        logging.getLogger("ExternalGrader").error("Failed to connect to RabbitMQ broker.")
    except Exception as e:
        logging.getLogger("ExternalGrader").error(e)


if __name__ == "__main__":
    main()
