"""
PyTest test file for grader_scripts.2.grade module.
"""
import pytest

from external_grader import process_answer
from external_grader.exceptions import InvalidGraderScriptException


def test_grade_incorrect_no_output_video():
    """
    Test grader_scripts.2.grade script.
    """
    answer: dict = {
        "xqueue_body": {"student_response": "ffmpeg", "grader_payload": "2"}
    }

    expected_response: dict = {
        "correct": False,
        "score": 0,
        "msg": "Не найден файл с обрезанным видео.",
    }

    assert process_answer.process_answer(answer) == expected_response


def test_grade_incorrect_time_from_value_none():
    """
    Test grader_scripts.2.grade script.
    """
    answer: dict = {
        "xqueue_body": {
            "student_response": "ffmpeg -i input_video.mp4 -t 10 cropped.mp4",
            "grader_payload": "2",
        }
    }

    expected_response: dict = {
        "correct": False,
        "score": 0,
        "msg": "Мы не смогли найти в вашем командном файле время, начиная с которого вы отрезали видеофайл.",
    }

    assert process_answer.process_answer(answer) == expected_response


def test_grade_incorrect_time_from_value_wrong():
    """
    Test grader_scripts.2.grade script.
    """
    answer: dict = {
        "xqueue_body": {
            "student_response": "ffmpeg -ss 25 -i input_video.mp4 -t 10 cropped.mp4",
            "grader_payload": "2",
        }
    }

    expected_response: dict = {
        "correct": False,
        "score": 0,
        "msg": "Вы задали начальное время обрезанного ролика вне того промежутка, где камера направлена в небо.",
    }

    assert process_answer.process_answer(answer) == expected_response


def test_grade_incorrect_time_to_value_none():
    """
    Test grader_scripts.2.grade script.
    """
    answer: dict = {
        "xqueue_body": {
            "student_response": "ffmpeg -ss 35 -i input_video.mp4 cropped.mp4",
            "grader_payload": "2",
        }
    }

    expected_response: dict = {
        "correct": False,
        "score": 0,
        "msg": "Мы не смогли найти длительность отрезаемого видеофайла (или конечный момент) в вашем командном файле.",
    }

    assert process_answer.process_answer(answer) == expected_response


def test_grade_incorrect_time_to_value_wrong():
    """
    Test grader_scripts.2.grade script.
    """
    answer: dict = {
        "xqueue_body": {
            "student_response": "ffmpeg -ss 35 -i input_video.mp4 -t 5 cropped.mp4",
            "grader_payload": "2",
        }
    }

    expected_response: dict = {
        "correct": False,
        "score": 0,
        "msg": "Вы неверно задали длительность отрезаемого видеофрагмента.",
    }

    assert process_answer.process_answer(answer) == expected_response
