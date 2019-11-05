"""
Config for default XQueue message broker.
"""
# Either "rabbitmq" or "xqueue"
TYPE: str = "xqueue"

# Location of message broker
HOST: str = "host"

# Credentials for basic auth
USER: str = "user"
PASS: str = "pass"

# Submissions queue name
QUEUE: str = "queue"

# Polling interval in seconds
POLLING_INTERVAL: int = 10
