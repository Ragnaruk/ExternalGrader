"""
PyTest test file for grader_scripts.1.grade module.
"""
import pytest

from external_grader import process_answer
from external_grader.exceptions import InvalidGraderScriptException


def test_grade_incorrect_not_number():
    """
    Test grader_scripts.1.grade script.
    """
    answer: dict = {"xqueue_body": {"student_response": "hello", "grader_payload": "1"}}

    expected_response: dict = {
        "correct": False,
        "score": 0,
        "msg": "Ответ — не число.\n",
    }

    assert process_answer.process_answer(answer) == expected_response


def test_grade_incorrect_different_number():
    """
    Test grader_scripts.1.grade script.
    """
    answer: dict = {"xqueue_body": {"student_response": "4", "grader_payload": "1"}}

    expected_response: dict = {
        "correct": False,
        "score": 0,
        "msg": "Ответ не равен 5.\n",
    }

    assert process_answer.process_answer(answer) == expected_response


def test_grade_incorrect_invalid_output():
    """
    Test grader_scripts.1.grade script.
    """
    answer: dict = {"xqueue_body": {"student_response": "-1000", "grader_payload": "1"}}

    with pytest.raises(InvalidGraderScriptException):
        assert process_answer.process_answer(answer)


def test_grade_correct():
    """
    Test grader_scripts.1.grade script.
    """
    answer: dict = {"xqueue_body": {"student_response": "5", "grader_payload": "1"}}

    expected_response: dict = {"correct": True, "score": 1, "msg": "Верный ответ.\n"}

    assert process_answer.process_answer(answer) == expected_response
