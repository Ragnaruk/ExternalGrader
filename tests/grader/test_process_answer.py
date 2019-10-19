"""
PyTest test file for grader.process_answer module.
"""
import pytest

from external_grader.grader import process_answer


def test_process_answer_correct():
    """
    Test grader.process_answer.process_answer function.
    """
    answer: dict = {
        "xqueue_body": {
            "student_response": "5",
            "grader_payload": "1"
        }
    }

    expected_response: dict = {
        "score": '100',
        "msg": "Верный ответ.\n"
    }

    assert process_answer.process_answer(answer) == expected_response


def test_process_answer_incorrect():
    """
    Test grader.process_answer.process_answer function.
    """
    answer: dict = {
        "xqueue_body": {
            "student_response": "4",
            "grader_payload": "1"
        }
    }

    expected_response: dict = {
        "score": '50',
        "msg": "Ответ не равен 5.\n"
    }

    assert process_answer.process_answer(answer) == expected_response


# def test_process_answer_module_not_found():
#     """
#     Test grader.process_answer.process_answer function.
#     """
#     answer: dict = {
#         "xqueue_body": {
#             "student_response": "response",
#             "grader_payload": "qwerty123456"
#         }
#     }
#
#     with pytest.raises(ModuleNotFoundError):
#         process_answer.process_answer(answer)


# def test_process_answer():
#     answer: dict = {
#         "xqueue_body": {
#             "student_response": "5",
#             "grader_payload": "1"
#         }
#     }
#
#     print(process_answer.process_answer(answer))
