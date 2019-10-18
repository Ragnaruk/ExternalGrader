"""
Config for default XQueue message broker.
"""
# Either "rabbitmq" or "xqueue"
TYPE: str = "xqueue"

# Location of message broker
HOST: str = ""

# Credentials for basic auth
USER: str = ""
PASS: str = ""

# Submissions queue name
QUEUE: str = ""

# Polling interval in seconds
POLLING_INTERVAL: int = 10