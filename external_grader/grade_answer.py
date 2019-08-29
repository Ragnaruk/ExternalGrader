import json
import logging
import importlib
import subprocess

from pika import channel, spec, BasicProperties


def grade_answer(current_channel: channel.Channel,
                 basic_deliver: spec.Basic.Deliver,
                 properties: spec.BasicProperties,
                 body: bytes) -> None:
    """
    Callback function which receives and proceeds consumed messages from RabbitMQ broker.

    :param current_channel: channel object.
    :param basic_deliver: object which has exchange, routing key,
     delivery tag and a redelivered flag of the message.
    :param properties: message properties.
    :param body: message body.
    """

    try:
        logging.getLogger("ExternalGrader").info("Received message: %s", body)

        message: dict = json.loads(body.decode("utf8").replace("\'", "\""))

        response: dict = {
            "xqueue_header": message["xqueue_header"],
            "xqueue_body": {
                "correct": False,
                "score": 0,
                "msg": ""
            }
        }

        try:
            grader = importlib.import_module("grade_scripts."
                                             + str(message["xqueue_header"]["submission_id"])
                                             + ".grade")
            grader.main(subprocess, message["xqueue_body"]["student_response"])

            response["xqueue_body"]["correct"] = True
        except AssertionError as exception:
            logging.getLogger("ExternalGrader").info("Grading failed with message: %s", exception)
            response["xqueue_body"]["msg"] = str(exception)

        logging.getLogger("ExternalGrader").info("Response: %s", response)

        # Send a response and acknowledge message in queue
        current_channel.basic_publish(
            exchange="",
            routing_key=properties.reply_to,
            properties=BasicProperties(correlation_id=properties.correlation_id),
            body=str(response))

        current_channel.basic_ack(delivery_tag=basic_deliver.delivery_tag)
    except Exception as exception:
        logging.getLogger("ExternalGrader").error(exception)
