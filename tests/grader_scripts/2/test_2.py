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
        "xqueue_body": {"student_response": "ffmpeg -hide_banner -loglevel panic", "grader_payload": "2"}
    }

    expected_response: dict = {
        "correct": False,
        "score": 0,
        "msg": "Не найден файл с обрезанным видео.\n",
    }

    assert process_answer.process_answer(answer) == expected_response


def test_grade_incorrect_time_from_value_none():
    """
    Test grader_scripts.2.grade script.
    """
    answer: dict = {
        "xqueue_body": {
            "student_response": "ffmpeg -hide_banner -loglevel panic -i input_video.mp4 -t 10 cropped.mp4",
            "grader_payload": "2",
        }
    }

    expected_response: dict = {
        "correct": False,
        "score": 0,
        "msg": "Мы не смогли найти в вашем командном файле время, начиная с которого вы отрезали видеофайл.\n",
    }

    assert process_answer.process_answer(answer) == expected_response


def test_grade_incorrect_time_from_value_wrong():
    """
    Test grader_scripts.2.grade script.
    """
    answer: dict = {
        "xqueue_body": {
            "student_response": "ffmpeg -hide_banner -loglevel panic -ss 25 -i input_video.mp4 -t 10 cropped.mp4",
            "grader_payload": "2",
        }
    }

    expected_response: dict = {
        "correct": False,
        "score": 0,
        "msg": "Вы задали начальное время обрезанного ролика вне того промежутка, где камера направлена в небо.\n",
    }

    assert process_answer.process_answer(answer) == expected_response


def test_grade_incorrect_time_to_value_none():
    """
    Test grader_scripts.2.grade script.
    """
    answer: dict = {
        "xqueue_body": {
            "student_response": "ffmpeg -hide_banner -loglevel panic -ss 35 -i input_video.mp4 cropped.mp4",
            "grader_payload": "2",
        }
    }

    expected_response: dict = {
        "correct": False,
        "score": 0,
        "msg": "Мы не смогли найти длительность отрезаемого видеофайла (или конечный момент) в вашем командном файле.\n",
    }

    assert process_answer.process_answer(answer) == expected_response


def test_grade_incorrect_time_to_value_wrong():
    """
    Test grader_scripts.2.grade script.
    """
    answer: dict = {
        "xqueue_body": {
            "student_response": "ffmpeg -hide_banner -loglevel panic -ss 35 -i input_video.mp4 -t 5 cropped.mp4",
            "grader_payload": "2",
        }
    }

    expected_response: dict = {
        "correct": False,
        "score": 0,
        "msg": "Вы неверно задали длительность отрезаемого видеофрагмента.\n",
    }

    assert process_answer.process_answer(answer) == expected_response


def test_grade_incorrect_duration():
    """
    Test grader_scripts.2.grade script.
    """
    answer: dict = {
        "xqueue_body": {
            "student_response": "ffmpeg -hide_banner -loglevel panic -ss 35 -i input_video.mp4 -to 45 cropped.mp4",
            "grader_payload": "2",
        }
    }

    expected_response: dict = {
        "correct": False,
        "score": 0,
        "msg": "Обрезанное видео имеет неверную длину.\n",
    }

    assert process_answer.process_answer(answer) == expected_response


# def test_grade_incorrect_metadata():
#     """
#     Test grader_scripts.2.grade script.
#     """
#     answer: dict = {
#         "xqueue_body": {
#             "student_response": "ffmpeg -hide_banner -loglevel panic -ss 35 -i input_video.mp4 -t 10 cropped.mp4",
#             "grader_payload": "2",
#         }
#     }
#
#     expected_response: dict = {
#         "correct": False,
#         "score": 0,
#         "msg": (
#             "Метаданные вашего обрезанного фрагмента не совпадают с ожидаемыми метаданными."
#             " Вы точно скопировали видеокодек?\n"
#             "Ожидаемые: Stream #0:0(und): Video: h264 (High) (avc1 / 0x31637661), yuv420p, 720x576 [SAR 16:15 DAR 4:3]\n"
#             "Полученные: Stream #0:0(und): Video: h264 (High) (avc1 / 0x31637661), yuv420p, 720x576 [SAR 16:15 DAR 4:3]\n"
#         ),
#     }
#
#     assert process_answer.process_answer(answer) == expected_response


# def test_grade_incorrect_metadata():
#     """
#     Test grader_scripts.2.grade script.
#     """
#     answer: dict = {
#         "xqueue_body": {
#             "student_response": "ffmpeg -hide_banner -loglevel panic -ss 35 -i input_video.mp4 -t 10 cropped.mp4",
#             "grader_payload": "2",
#         }
#     }
#
#     expected_response: dict = {
#         "correct": False,
#         "score": 0,
#         "msg": "Метаданные вашего обрезанного фрагмента не совпадают с ожидаемыми метаданными. Вы точно скопировали видеокодек?",
#     }
#
#     assert process_answer.process_answer(answer) == expected_response
