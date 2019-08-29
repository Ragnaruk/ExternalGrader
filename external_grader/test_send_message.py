import pika
import logging

from external_grader.config import RABBITMQ_PORT, RABBITMQ_HOST, RABBITMQ_CALLBACK_QUEUE,\
    RABBITMQ_CONSUMPTION_QUEUE

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
    :param message: string with a message to send.
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

    logging.getLogger("ExternalGrader").info(
        "Sent message \"{0}\" to channel \"{1}\"".format(message, queue_name))

    connection.close()


if __name__ == '__main__':
    send_message(RABBITMQ_HOST, RABBITMQ_PORT,
                 RABBITMQ_CONSUMPTION_QUEUE, RABBITMQ_CALLBACK_QUEUE,
                 """{
                     "xqueue_header": {
                     "submission_id": 1,
                     "submission_key": "ffcd933556c926a307c45e0af5131995"
                 },
                 "xqueue_files": {
                    "helloworld.c": "http://download.location.com/helloworld.c"
                 },
                 "xqueue_body": {
                     "student_info": {
                         "anonymous_student_id": "106ecd878f4148a5cabb6bbb0979b730",
                         "submission_time": "20160324104521",
                         "random_seed": 334
                     },
                     "student_response": "def double(x):\\n return 2*x\\n",
                     "grader_payload": "problem_2"
                 }
                 }""")
