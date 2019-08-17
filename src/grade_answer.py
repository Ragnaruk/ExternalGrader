from subprocess import CompletedProcess
import json
import logging
import os.path
from distutils.dir_util import copy_tree
import shutil

from pika import channel, spec, BasicProperties

from src.run_command import run_command


def grade_answer(current_channel: channel.Channel,
                 basic_deliver: spec.Basic.Deliver,
                 properties: spec.BasicProperties,
                 body: bytes) -> None:
    """
    Callback function which receives consumed messages from RabbitMQ broker.

    :param current_channel: channel object.
    :param basic_deliver: object which has exchange, routing key,
     delivery tag and a redelivered flag of the message.
    :param properties: message properties.
    :param body: message body.
    """

    current_directory: str = os.path.split(
        os.path.dirname(os.path.abspath(__file__)))[0]
    solution_directory: str = os.path.join(current_directory, "solutions")
    working_directory: str = os.path.join(current_directory,
                                          "working_directory")

    try:
        logging.getLogger("ExternalGrader").info("Received message: %s", body)

        decoded_body: str = body.decode("utf8").replace("\'", "\"")
        message: dict = json.loads(decoded_body)

        message["grade"]: int = 0

        solution_directory: str = os.path.join(
            solution_directory,
            str(message["solution_id"]))

        if not os.path.exists(working_directory):
            os.mkdir(working_directory)

        # Get expected name of the program to safeguard
        # from execution of other programs
        with open(os.path.join(solution_directory, "example.sh")) as file:
            expected_command = file.readline()

            logging.getLogger("ExternalGrader").info(
                "Expected command: %s", expected_command)
            logging.getLogger("ExternalGrader").info(
                "Student command: %s", message["command"])

        # If commands are identical then there is no need to execute it
        if message["command"] == expected_command:
            message["grade"] = 100
        else:
            # Create a directory with files required for grading
            run_command("/bin/sh ./prepare.sh", "/bin/sh", solution_directory)

            # Copy requirements to working directory if they exist
            if os.path.exists(os.path.join(solution_directory, "requirements")):
                copy_tree(
                    os.path.join(solution_directory, "requirements"),
                    working_directory)

            # Get expected program name
            expected_program_name: str = expected_command.split(" ", 1)[0]

            result: CompletedProcess = run_command(message["command"],
                                                   expected_program_name,
                                                   working_directory)
            logging.getLogger("ExternalGrader").info(result)

            if not result.args:
                message["grade"] = 0
            else:
                grader: CompletedProcess = run_command("/bin/sh ./grade.sh",
                                                       "/bin/sh",
                                                       solution_directory)
                logging.getLogger("ExternalGrader").info(grader)

                try:
                    message["grade"] = int(grader.stdout.decode("utf8"))
                except ValueError as exception:
                    logging.getLogger("ExternalGrader").error(exception)
                    logging.getLogger("ExternalGrader").error(
                        "Attempt to use stdout for a grade failed. "
                        "Using return code.")

                    message["grade"] = grader.returncode

                if not 0 <= message["grade"] <= 100:
                    raise ValueError(
                        "Invalid grade value: {0}".format(message["grade"]))

        # Send a response and acknowledge message in queue
        current_channel.basic_publish(
            exchange="",
            routing_key=properties.reply_to,
            properties=BasicProperties(correlation_id=properties.correlation_id),
            body=bytes(message["grade"]))

        current_channel.basic_ack(delivery_tag=basic_deliver.delivery_tag)
    except Exception as exception:
        logging.getLogger("ExternalGrader").error(exception)
    else:
        logging.getLogger("ExternalGrader").info("Grade: %s", message["grade"])
    finally:
        shutil.rmtree(working_directory)
