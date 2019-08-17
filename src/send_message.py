import pika
import logging


def send_message(host: str,
                 port: int,
                 queue_name: str,
                 callback_queue_name: str,
                 message: str) -> None:
    """
    Send a message to a RabbitMQ broker.

    :param host: string with the url of the broker.
    :param port: integer with the port of the broker.
    :param queue_name: string with a name of the queue.
    :param callback_queue_name: string with a name of the callback queue for RPC.
    :param message: string with a message to send. # TODO Change description of message object.
    """

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port))
    channel = connection.channel()

    # Set durable=True to save messages between RabbitMQ restarts
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_publish(exchange="",
                          routing_key=queue_name,
                          body=message,
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # Make message persistent
                              reply_to=callback_queue_name
                          ))

    logging.getLogger("ExternalGrader").info("Sent message \"{0}\" to channel \"{1}\"".format(message, queue_name))

    connection.close()
