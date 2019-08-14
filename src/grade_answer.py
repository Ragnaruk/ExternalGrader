from src.run_command import run_command

from subprocess import CompletedProcess
from pika import channel, spec
import json
import logging
import os.path
from distutils.dir_util import copy_tree
import shutil
import pika


def grade_answer(ch: channel.Channel,
                 basic_deliver: spec.Basic.Deliver,
                 properties: spec.BasicProperties,
                 body: bytes) -> None:
    """
    Callback function which receives consumed messages from RabbitMQ broker.
    :param ch: channel object.
    :param basic_deliver: object which has exchange, routing key, delivery tag and a redelivered flag of the message.
    :param properties: message properties.
    :param body: message body.
    """

    current_directory: str = os.path.dirname(os.path.abspath(__file__))
    solution_directory: str = os.path.join(os.path.split(current_directory)[0],
                                           "solutions")
    working_directory: str = os.path.join(os.path.split(current_directory)[0],
                                          "working_directory")

    try:
        logging.getLogger("ExternalGrader").info("Received message: {0}".format(body))

        decoded_body: str = body.decode("utf8").replace("\'", "\"")
        message: dict = json.loads(decoded_body)

        command: str = message["command"]
        expected_command: str = ""

        grade: int = 0

        solution_directory = os.path.join(solution_directory, str(message["solution_id"]))

        if not os.path.exists(working_directory):
            os.mkdir(working_directory)

        # Get expected name of the program to safeguard from execution of other programs
        with open(os.path.join(solution_directory, "example.sh"), "r") as file:
            expected_command = file.readline()

            logging.getLogger("ExternalGrader").info("Expected command: {0}".format(expected_command))
            logging.getLogger("ExternalGrader").info("Student command: {0}".format(command))

        # If commands are identical then there is no need to execute it
        if command == expected_command:
            grade = 100
        else:
            # Create a directory with files required for grading
            run_command("/bin/sh ./prepare.sh", "/bin/sh", solution_directory)

            # Copy requirements to working directory if they exist
            if os.path.exists(os.path.join(solution_directory, "requirements")):
                copy_tree(os.path.join(solution_directory, "requirements"), working_directory)

            # Get expected program name
            expected_program_name: str = expected_command.split(" ", 1)[0]
            
            result: CompletedProcess = run_command(command, expected_program_name, working_directory)
            logging.getLogger("ExternalGrader").info(result)
    
            if len(result.args) == 0:
                grade = 0
            else:
                grader: CompletedProcess = run_command("/bin/sh ./grade.sh", "/bin/sh", solution_directory)
                logging.getLogger("ExternalGrader").info(grader)

                try:
                    grade = int(grader.stdout.decode("utf8"))
                except Exception as e:
                    logging.getLogger("ExternalGrader").error(e)
                    logging.getLogger("ExternalGrader").error("Attempt to use stdout for a grade failed. "
                                                              "Using return code.")

                    grade = grader.returncode

                if not 0 <= grade <= 100:
                    raise ValueError("Invalid grade value: {0}".format(grade))

        message["grade"] = grade

        # Send a response and acknowledge message in queue
        ch.basic_publish(exchange="",
                         routing_key=properties.reply_to,
                         properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                         body=bytes(grade))

        ch.basic_ack(delivery_tag=basic_deliver.delivery_tag)
    except Exception as e:
        logging.getLogger("ExternalGrader").error(e)
    else:
        logging.getLogger("ExternalGrader").info("Grade: {0}".format(grade))
    finally:
        shutil.rmtree(working_directory)
