"""
Handler for RabbitMQ message broker.
"""
import json

from pika import channel, spec, credentials, \
    BlockingConnection, ConnectionParameters, BasicProperties

from config.config import MESSAGE_BROKER
from grader.logs import get_logger
from grader.process_answer import process_answer


# @log_exceptions
def receive_messages() -> None:
    """
    Start consuming messages from RabbitMQ broker.
    """
    logger = get_logger("rabbitmq")

    connection = BlockingConnection(
        ConnectionParameters(
            host=MESSAGE_BROKER.HOST,
            port=MESSAGE_BROKER.PORT,
            credentials=credentials.PlainCredentials(
                MESSAGE_BROKER.USER,
                MESSAGE_BROKER.PASS
            )
        )
    )
    ch = connection.channel()

    # Set durable=True to save messages between RabbitMQ restarts
    ch.queue_declare(queue=MESSAGE_BROKER.QUEUE, durable=True)

    # Make RabbitMQ avoid giving more than 1 message at a time to a worker
    ch.basic_qos(prefetch_count=1)

    # Start receiving messages
    ch.basic_consume(queue=MESSAGE_BROKER.QUEUE, on_message_callback=callback_function)

    try:
        logger.info("Started consuming messages from RabbitMQ.")

        ch.start_consuming()
    except KeyboardInterrupt:
        logger.info("Stopped consuming messages from RabbitMQ.")

        ch.stop_consuming()
        connection.close()


# @log_exceptions
def callback_function(current_channel: channel.Channel,
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
    logger = get_logger("rabbitmq")

    try:
        message: dict = json.loads(body.decode("utf8").replace("\'", "\""))
        logger.debug("Received message: {0}".format(message))

        response: dict = {
            "xqueue_header": message["xqueue_header"],
            "xqueue_body": process_answer(message)
        }
        logger.debug("Response message: {0}".format(response))

        # Send a response
        current_channel.basic_publish(
            exchange="",
            routing_key=properties.reply_to,
            properties=BasicProperties(correlation_id=properties.correlation_id),
            body=json.dumps(response))
    except Exception as exception:
        logger.error(exception, exc_info=True)

    # Acknowledge message in queue
    current_channel.basic_ack(delivery_tag=basic_deliver.delivery_tag)
