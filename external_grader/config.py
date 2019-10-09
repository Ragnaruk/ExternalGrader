from pathlib import Path

HOME_PATH = Path("/home/")
VERIFICATION_FILES_PATH = Path("/root/")
LOG_FILE_PATH = Path(__file__).parent.parent / "grader.log"

RABBITMQ_HOST = "localhost"
RABBITMQ_PORT = 5672
RABBITMQ_CONSUMPTION_QUEUE = "student_answers"
RABBITMQ_CALLBACK_QUEUE = "student_grades"
