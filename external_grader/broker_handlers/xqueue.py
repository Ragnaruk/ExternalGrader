"""
Handler for XQueue message broker.
"""
import json
import requests
from requests.auth import HTTPBasicAuth
from time import sleep

from external_grader.logs import get_logger
from external_grader.process_answer import process_answer


def receive_messages(
    host: str, user: str, password: str, queue: str, polling_interval: int
) -> None:
    """
    Start consuming messages from XQueue broker.

    :param host: Host of XQueue broker.
    :param user: Username for basic auth.
    :param password: Password for basic auth.
    :param queue: Queue name.
    :param polling_interval: Interval between requests for submissions.
    """
    logger = get_logger("xqueue")

    session = requests.session()

    xqueue_login_url = host + "/xqueue/login/"

    logger.debug(
        "Logging in to: %s with credentials: %s:%s", xqueue_login_url, user, password
    )
    response = session.post(
        xqueue_login_url, auth=None, data={"username": user, "password": password}
    )

    if response.status_code != 200:
        logger.error("Login failed: %s %s", response.status_code, response.content)
    else:
        logger.debug("Login successful: %s", response.json())

        try:
            logger.info("Started consuming messages from XQueue.")

            while True:
                process_submission(session, host, user, password, queue)
                sleep(polling_interval)
        except KeyboardInterrupt as exception:
            logger.info("Stopped consuming messages from XQueue.")

            session.close()

            raise exception


def process_submission(
    session: requests.Session, host: str, user: str, password: str, queue: str
) -> None:
    """
    Get submission from XQueue, process it, and put results back.

    :param session: Session object.
    :param host: Host of XQueue broker.
    :param user: Username for basic auth.
    :param password: Password for basic auth.
    :param queue: Queue name.
    """
    logger = get_logger("xqueue")

    xqueue_get_submission_url = host + "/xqueue/get_submission/"
    xqueue_put_result_url = host + "/xqueue/put_result/"

    response: requests.Response = session.get(
        xqueue_get_submission_url,
        auth=HTTPBasicAuth(user, password),
        params={"queue_name": queue},
    )
    logger.debug("GET request response: %s", response.json())

    try:
        message: str = response.json()["content"]
        logger.debug("Message: %s", message)

        if message.startswith("Queue"):
            return

        message: dict = json.loads(message)
        logger.debug("Content: %s", message)

        # XQueue header is a unique dict, so it is removed from message to allow caching
        xqueue_header = message.pop("xqueue_header", None)

        reply: dict = {
            "xqueue_header": xqueue_header,
            "xqueue_body": json.dumps(process_answer(message)),
        }
        logger.debug("Reply message: %s", reply)

        response: requests.Response = session.post(
            xqueue_put_result_url,
            auth=HTTPBasicAuth(user, password),
            verify=False,
            data=reply,
        )
        logger.debug("POST request response: %s", response.json())
    except Exception as exception:
        raise exception
