"""
Handler for RabbitMQ message broker.
"""
import json

from pika import (
    channel,
    spec,
    credentials,
    BlockingConnection,
    ConnectionParameters,
    BasicProperties,
)
from logging import Logger

from external_grader.logs import get_logger
from external_grader.process_answer import process_answer
from external_grader.exceptions import (
    InvalidSubmissionException,
    InvalidGraderScriptException,
)


def receive_messages(
    host: str, port: int, user: str, password: str, queue: str
) -> None:
    """
    Start consuming messages from RabbitMQ broker.

    :param host: Host of XQueue broker.
    :param port: Port of XQueue broker.
    :param user: Username for basic auth.
    :param password: Password for basic auth.
    :param queue: Queue name.
    """
    logger: Logger = get_logger("rabbitmq")

    connection: BlockingConnection = BlockingConnection(
        ConnectionParameters(
            host=host,
            port=port,
            credentials=credentials.PlainCredentials(user, password),
        )
    )
    ch: channel = connection.channel()

    # Set durable=True to save messages between RabbitMQ restarts
    ch.queue_declare(queue=queue, durable=True)

    # Make RabbitMQ avoid giving more than 1 message at a time to a worker
    ch.basic_qos(prefetch_count=1)

    # Start receiving messages
    ch.basic_consume(queue=queue, on_message_callback=callback_function)

    try:
        logger.info("Started consuming messages from RabbitMQ.")

        ch.start_consuming()
    except KeyboardInterrupt as exception:
        logger.info("Stopped consuming messages from RabbitMQ.")

        ch.stop_consuming()
        connection.close()

        raise exception


def callback_function(
    current_channel: channel.Channel,
    basic_deliver: spec.Basic.Deliver,
    properties: spec.BasicProperties,
    body: bytes,
) -> None:
    """
    Callback function which receives and proceeds consumed messages from RabbitMQ broker.

    :param current_channel: Channel object.
    :param basic_deliver: Object which has exchange, routing key,
     delivery tag and a redelivered flag of the message.
    :param properties: Message properties.
    :param body: Message body.
    """
    logger: Logger = get_logger("rabbitmq")

    try:
        message: dict = json.loads(body.decode("utf8"))

        logger.debug("Received message: %s", message)
    except json.decoder.JSONDecodeError as exception:
        send_reply(
            logger,
            current_channel,
            basic_deliver,
            properties,
            {},
            False,
            0,
            "Ошибка при декодировании сообщения.",
        )

        logger.info("Failed to decode message: {}.".format(body.decode("utf8")))

        return

    # XQueue header is a unique dict, so it is removed from message to allow caching
    xqueue_header = message.pop("xqueue_header", None)

    try:
        xqueue_body: dict = process_answer(message)

        send_reply(
            logger,
            current_channel,
            basic_deliver,
            properties,
            xqueue_header,
            xqueue_body=xqueue_body,
        )
    except InvalidSubmissionException:
        send_reply(
            logger,
            current_channel,
            basic_deliver,
            properties,
            xqueue_header,
            False,
            0,
            "Неверный формат сообщения или ID скрипта проверки.",
        )
    except InvalidGraderScriptException:
        send_reply(
            logger,
            current_channel,
            basic_deliver,
            properties,
            xqueue_header,
            False,
            0,
            "Неверный скрипт проверки.",
        )
    except Exception as exception:
        send_reply(
            logger,
            current_channel,
            basic_deliver,
            properties,
            xqueue_header,
            False,
            0,
            "Ошибка при проверке ответа.",
        )

        raise exception

    logger.debug("Finished handling message.")


def send_reply(
    logger: Logger,
    current_channel: channel.Channel,
    basic_deliver: spec.Basic.Deliver,
    properties: spec.BasicProperties,
    xqueue_header: dict,
    correct: bool = False,
    score: int = 0,
    msg: str = "",
    xqueue_body: dict = None,
):
    """
    Send a reply message and acknowledge received one.

    :param logger: Logger object.
    :param current_channel: Channel object.
    :param basic_deliver: Object which has exchange, routing key,
     delivery tag and a redelivered flag of the message.
    :param properties: Message properties.
    :param xqueue_header: Unique message header.
    :param correct: xqueue_body parameter.
    :param score: xqueue_body parameter.
    :param msg: xqueue_body parameter.
    :param xqueue_body: alternative way to pass values.
    """
    if not xqueue_body:
        xqueue_body = {
            "correct": correct,
            "score": score,
            "msg": msg,
        }

    reply: dict = {"xqueue_header": xqueue_header, "xqueue_body": xqueue_body}
    logger.debug("Reply message: %s", reply)

    current_channel.basic_publish(
        exchange="",
        routing_key=properties.reply_to,
        properties=BasicProperties(correlation_id=properties.correlation_id),
        body=json.dumps(reply),
    )

    # Acknowledge message in queue
    current_channel.basic_ack(delivery_tag=basic_deliver.delivery_tag)
