import pika

from external_grader.grade_answer import grade_answer


def receive_messages(host: str,
                     port: int,
                     queue_name: str) -> None:
    """
    Start consuming messages from RabbitMQ broker.

    :param host: string with the url of the broker.
    :param port: integer with the port of the broker.
    :param queue_name: string with a name of the queue.
    """

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port))
    channel = connection.channel()

    # Set durable=True to save messages between RabbitMQ restarts
    channel.queue_declare(queue=queue_name, durable=True)

    # Make RabbitMQ avoid giving more than 1 message at a time to a worker
    channel.basic_qos(prefetch_count=1)

    # Start receiving messages
    channel.basic_consume(queue=queue_name, on_message_callback=grade_answer)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
        connection.close()


if __name__ == '__main__':
    receive_messages("localhost", 32769, "student_grades")
