import json
import logging
import importlib

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
            grade_script = importlib.import_module("grade_scripts."
                                                   + str(message["xqueue_body"]["grader_payload"])
                                                   + ".grade")
            if message["xqueue_files"]:
                score, msg = grade_script.main(message["xqueue_body"]["student_response"],
                                               message["xqueue_files"])
            else:
                score, msg = grade_script.main(message["xqueue_body"]["student_response"])

            response["xqueue_body"]["correct"] = True
            response["xqueue_body"]["score"] = score if score else 0
            response["xqueue_body"]["msg"] = msg if msg else ""
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
    except Exception as exception:
        logging.getLogger("ExternalGrader").error(exception)

    current_channel.basic_ack(delivery_tag=basic_deliver.delivery_tag)
