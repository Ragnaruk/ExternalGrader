"""
PyTest test file for grader_scripts.3.grade module.
"""
import pytest

from external_grader import process_answer


def test_grade_incorrect_circle():
    """
    Test grader_scripts.computer_graphics_2_6.grade script.
    """
    answer: dict = {
        "xqueue_body": {
            "student_response": """<svg width="400" height="200">
<rect x="1" y="1" height="180" width="180" stroke="gray" stroke-dasharray="10 5" stroke-width="2" fill="tomato"/>
<circle cx="309" cy="90" r="90" stroke="gray" stroke-dasharray="10 5" stroke-width="2" fill="lightblue"/>
<polygon points="200,43 110,199 290,199" stroke="darkgray" stroke-width="4" fill="lightgreen"/>
</svg>""",
            "grader_payload": "computer_graphics_2_6",
        }
    }

    expected_response: dict = {
        "correct": False,
        "score": 0,
        "msg": "Проверьте параметры круга\n",
    }

    assert process_answer.process_answer(answer) == expected_response


def test_grade_incorrect_no_shape():
    """
    Test grader_scripts.computer_graphics_2_6.grade script.
    """
    answer: dict = {
        "xqueue_body": {
            "student_response": """<svg width="400" height="200">
<polygon points="1,1 180,1 180,180 1,180" stroke="gray" stroke-dasharray="10 5" stroke-width="2" fill="tomato"/>
<circle cx="309" cy="90" r="90" stroke="gray" stroke-dasharray="10 5" stroke-width="2" fill="lightblue"/>
<polygon points="200,43 110,199 290,199" stroke="darkgray" stroke-width="4" fill="lightgreen"/>
</svg>""",
            "grader_payload": "computer_graphics_2_6",
        }
    }

    expected_response: dict = {
        "correct": False,
        "score": 0,
        "msg": "Мы не нашли одну из фигур в вашей команде (иногда это сообщение появляется,"
        " если в теге svg есть лишние атрибуты)\n",
    }

    assert process_answer.process_answer(answer) == expected_response


def test_grade_incorrect_tags():
    """
    Test grader_scripts.computer_graphics_2_6.grade script.
    """
    answer: dict = {
        "xqueue_body": {
            "student_response": """<svg width="400" height="200">
<polygon points="1,1 180,1 180,180 1,180" stroke="gray" stroke-dasharray="10 5" stroke-width="2" fill="tomato"/>
<circle cx="309" cy="90" r="90" stroke="gray"; stroke-dasharray="10 5" stroke-width="2" fill="lightblue"/>
<polygon points="200,43 110,199 290,199" stroke="darkgray" stroke-width="4" fill="lightgreen"/>
</svg>""",
            "grader_payload": "computer_graphics_2_6",
        }
    }

    expected_response: dict = {
        "correct": False,
        "score": 0,
        "msg": "Проверьте ваш текст на наличие открывающих и закрывающих тегов <svg>,"
        " на наличие синтаксических ошибок в тегах и на то, что все теги закрыты\n",
    }

    assert process_answer.process_answer(answer) == expected_response


def test_grade_correct():
    """
    Test grader_scripts.computer_graphics_2_6.grade script.
    """
    answer: dict = {
        "xqueue_body": {
            "student_response": """<svg width="400" height="200">
<rect x="1" y="1" height="180" width="180" stroke="gray" stroke-dasharray="10 5" stroke-width="2" fill="tomato"/>
<circle cx="309" cy="91" r="90" stroke="gray" stroke-dasharray="10 5" stroke-width="2" fill="lightblue"/>
<polygon points="200,43 110,199 290,199" stroke="darkgray" stroke-width="4" fill="lightgreen"/>
</svg>""",
            "grader_payload": "computer_graphics_2_6",
        }
    }

    expected_response: dict = {
        "correct": True,
        "score": 10,
        "msg": "Верный ответ.\n",
    }

    assert process_answer.process_answer(answer) == expected_response
