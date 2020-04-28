"""
PyTest test file for grader_scripts.computer_graphics_3_5.grade module.
"""
import pytest

from external_grader import process_answer


def test_grade_correct():
    """
    Test grader_scripts.computer_graphics_3_5.grade script.
    """
    answer: dict = {
        "xqueue_body": {
            "student_response": """ffmpeg -i in.mp4 -c:v h264 -b:v 5000k -minrate 5M -bufsize 1000k -maxrate 5000000 -s 1280x720 -r 25 -profile:v high -level:v 42 -bf 2 -g 13 -b:a 128k  -c:a aac -strict -2 -ar 96k out.mp4""",
            "grader_payload": "computer_graphics_3_5",
        }
    }

    expected_response: dict = {
        "correct": True,
        "score": 1,
        "msg": "Верный ответ.\n",
    }

    assert process_answer.process_answer(answer) == expected_response
