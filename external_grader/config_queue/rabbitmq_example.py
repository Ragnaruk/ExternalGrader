"""
Config for default local RabbitMQ message broker.
"""
# Either "rabbitmq" or "xqueue"
TYPE: str = "rabbitmq"

# Location of message broker
HOST: str = "rabbitmq"
PORT: int = 5672

# Credentials for basic auth
USER: str = "user"
PASS: str = "jn0oSx3i2SkV5TlQAFVy"

# Submissions queue name
QUEUE: str = "student_answers"
