import pika

from external_grader.config import RABBITMQ_PORT, RABBITMQ_HOST, RABBITMQ_CONSUMPTION_QUEUE, \
    RABBITMQ_CALLBACK_QUEUE


def send_message(host: str,
                 port: int,
                 queue_name: str,
                 callback_queue_name: str,
                 message: str) -> None:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port))
    channel = connection.channel()

    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_publish(exchange="",
                          routing_key=queue_name,
                          body=message,
                          properties=pika.BasicProperties(
                              delivery_mode=2,
                              reply_to=callback_queue_name
                          ))
    connection.close()


if __name__ == '__main__':
    send_message(RABBITMQ_HOST, RABBITMQ_PORT,
                 RABBITMQ_CONSUMPTION_QUEUE, RABBITMQ_CALLBACK_QUEUE,
                 """{
                     "xqueue_header": {
                         "submission_id": 1,
                         "submission_key": "1"
                     },
                     "xqueue_body": {
                         "student_response": "5",
                         "grader_payload": "1"
                     }
                 }""")
