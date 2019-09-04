import pika

from external_grader.config import RABBITMQ_PORT, RABBITMQ_HOST, RABBITMQ_CALLBACK_QUEUE


def receive_message(host: str,
                     port: int,
                     queue_name: str) -> None:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port))
    channel = connection.channel()

    method_frame, header_frame, body = channel.basic_get(queue_name)

    if method_frame:
        print(method_frame, header_frame, body)
        channel.basic_ack(method_frame.delivery_tag)
    else:
        print('No message returned')


if __name__ == '__main__':
    receive_message(RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_CALLBACK_QUEUE)
