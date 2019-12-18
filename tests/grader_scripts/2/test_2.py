"""
PyTest test file for grader_scripts.2.grade module.
"""
import pytest

from external_grader import process_answer


def test_grade_incorrect_no_output_video():
    """
    Test grader_scripts.2.grade script.
    """
    answer: dict = {
        "xqueue_body": {
            "student_response": "ffmpeg -hide_banner -loglevel panic",
            "grader_payload": "2",
        }
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


@pytest.mark.skip(reason="No way to get desired response.")
def test_grade_incorrect_metadata():
    """
    Test grader_scripts.2.grade script.
    """
    answer: dict = {
        "xqueue_body": {
            "student_response": "ffmpeg -hide_banner -loglevel panic -ss 35 -i input_video.mp4 -t 10 cropped.mp4",
            "grader_payload": "2",
        }
    }

    expected_response: dict = {
        "correct": False,
        "score": 0,
        "msg": (
            "Метаданные вашего обрезанного фрагмента не совпадают с ожидаемыми метаданными."
            " Вы точно скопировали видеокодек?\n"
            "Ожидаемые: Stream #0:0(und): Video: h264 (High) (avc1 / 0x31637661), yuv420p, 720x576 [SAR 16:15 DAR 4:3]\n"
            "Полученные: Stream #0:0(und): Video: h264 (High) (avc1 / 0x31637661), yuv420p, 720x576 [SAR 16:15 DAR 4:3]\n"
        ),
    }

    assert process_answer.process_answer(answer) == expected_response


def test_grade_plate_no_svg():
    """
    Test grader_scripts.2.grade script.
    """
    answer: dict = {
        "xqueue_body": {
            "student_response": "ffmpeg -hide_banner -loglevel panic -ss 35 -i input_video.mp4 -t 10 cropped.mp4",
            "grader_payload": "2",
        }
    }

    expected_response: dict = {
        "correct": False,
        "score": 0,
        "msg": ("Не найден svg-файл с кодом плашки.\n"),
    }

    assert process_answer.process_answer(answer) == expected_response


def test_grade_plate_empty_svg():
    """
    Test grader_scripts.2.grade script.
    """
    answer: dict = {
        "xqueue_body": {
            "student_response": (
                "ffmpeg -hide_banner -loglevel panic -ss 35 -i input_video.mp4 -t 10 cropped.mp4;\n"
                'echo "" > plate.svg'
            ),
            "grader_payload": "2",
        }
    }

    expected_response: dict = {
        "correct": False,
        "score": 0,
        "msg": ("Ваш svg-файл пуст.\n"),
    }

    assert process_answer.process_answer(answer) == expected_response


def test_grade_plate_incorrect_circle():
    """
    Test grader_scripts.2.grade script.
    """
    svg = '<svg width="1440" height="200"> \
    <rect x="1" y="1" height="200" width="1440" fill="rgba(222,222,222,0.5)"/> \
    <rect x="51" y="1" height="180" width="180" stroke="gray" stroke-dasharray="10 5" stroke-width="2" fill="tomato" opacity="0.75"/> \
    <circle cx="358" cy="91" r="90" stroke="gray" stroke-dasharray="10 5" stroke-width="2" fill="lightblue" opacity="0.75"/> \
    <polygon points="250,43 160,199 340,199" stroke="darkgray" stroke-width="4" fill="lightgreen" opacity="0.75"/> \
    </svg>'

    answer: dict = {
        "xqueue_body": {
            "student_response": (
                "ffmpeg -hide_banner -loglevel panic -ss 35 -i input_video.mp4 -t 10 cropped.mp4;\n"
                "echo '{0}' > plate.svg".format(svg)
            ),
            "grader_payload": "2",
        }
    }

    expected_response: dict = {
        "correct": False,
        "score": 0,
        "msg": ("Вы перенесли круг на 50 пикселей вправо?\n"),
    }

    assert process_answer.process_answer(answer) == expected_response


def test_grade_plate_incorrect_square():
    """
    Test grader_scripts.2.grade script.
    """
    svg = '<svg width="1440" height="200"> \
    <rect x="1" y="1" height="200" width="1440" fill="rgba(222,222,222,0.5)"/> \
    <rect x="50" y="1" height="180" width="180" stroke="gray" stroke-dasharray="10 5" stroke-width="2" fill="tomato" opacity="0.75"/> \
    <circle cx="359" cy="91" r="90" stroke="gray" stroke-dasharray="10 5" stroke-width="2" fill="lightblue" opacity="0.75"/> \
    <polygon points="250,43 160,199 340,199" stroke="darkgray" stroke-width="4" fill="lightgreen" opacity="0.75"/> \
    </svg>'

    answer: dict = {
        "xqueue_body": {
            "student_response": (
                "ffmpeg -hide_banner -loglevel panic -ss 35 -i input_video.mp4 -t 10 cropped.mp4;\n"
                "echo '{0}' > plate.svg".format(svg)
            ),
            "grader_payload": "2",
        }
    }

    expected_response: dict = {
        "correct": False,
        "score": 0,
        "msg": ("Вы перенесли квадрат на 50 пикселей вправо?\n"),
    }

    assert process_answer.process_answer(answer) == expected_response


def test_grade_plate_incorrect_triangle():
    """
    Test grader_scripts.2.grade script.
    """
    svg = '<svg width="1440" height="200"> \
    <rect x="1" y="1" height="200" width="1440" fill="rgba(222,222,222,0.5)"/> \
    <rect x="51" y="1" height="180" width="180" stroke="gray" stroke-dasharray="10 5" stroke-width="2" fill="tomato" opacity="0.75"/> \
    <circle cx="359" cy="91" r="90" stroke="gray" stroke-dasharray="10 5" stroke-width="2" fill="lightblue" opacity="0.75"/> \
    <polygon points="249,43 160,199 340,199" stroke="darkgray" stroke-width="4" fill="lightgreen" opacity="0.75"/> \
    </svg>'

    answer: dict = {
        "xqueue_body": {
            "student_response": (
                "ffmpeg -hide_banner -loglevel panic -ss 35 -i input_video.mp4 -t 10 cropped.mp4;\n"
                "echo '{0}' > plate.svg".format(svg)
            ),
            "grader_payload": "2",
        }
    }

    expected_response: dict = {
        "correct": False,
        "score": 0,
        "msg": ("Вы перенесли треугольник на 50 пикселей вправо?\n"),
    }

    assert process_answer.process_answer(answer) == expected_response


def test_grade_plate_incorrect_background():
    """
    Test grader_scripts.2.grade script.
    """
    svg = '<svg width="1440" height="200"> \
    <rect x="1" y="1" height="200" width="1440"/> \
    <rect x="51" y="1" height="180" width="180" stroke="gray" stroke-dasharray="10 5" stroke-width="2" fill="tomato" opacity="0.75"/> \
    <circle cx="359" cy="91" r="90" stroke="gray" stroke-dasharray="10 5" stroke-width="2" fill="lightblue" opacity="0.75"/> \
    <polygon points="250,43 160,199 340,199" stroke="darkgray" stroke-width="4" fill="lightgreen" opacity="0.75"/> \
    </svg>'

    answer: dict = {
        "xqueue_body": {
            "student_response": (
                "ffmpeg -hide_banner -loglevel panic -ss 35 -i input_video.mp4 -t 10 cropped.mp4;\n"
                "echo '{0}' > plate.svg".format(svg)
            ),
            "grader_payload": "2",
        }
    }

    expected_response: dict = {
        "correct": False,
        "score": 0,
        "msg": ("Вы сделали подложку из прямоугольника? А заливка верная?\n"),
    }

    assert process_answer.process_answer(answer) == expected_response


@pytest.mark.skip(reason="In work.")
def test_grade_plate_incorrect_background():
    """
    Test grader_scripts.2.grade script.
    """
    svg = '<svg width="1440" height="200"> \
    <rect x="1" y="1" height="200" width="1440" fill="rgba(222,222,222,0.5)"/> \
    <rect x="51" y="1" height="180" width="180" stroke="gray" stroke-dasharray="10 5" stroke-width="2" fill="tomato" opacity="0.75"/> \
    <circle cx="359" cy="91" r="90" stroke="gray" stroke-dasharray="10 5" stroke-width="2" fill="lightblue" opacity="0.75"/> \
    <polygon points="250,43 160,199 340,199" stroke="darkgray" stroke-width="4" fill="lightgreen" opacity="0.75"/> \
    </svg>'

    answer: dict = {
        "xqueue_body": {
            "student_response": (
                "ffmpeg -hide_banner -loglevel panic -ss 35 -i input_video.mp4 -t 10 cropped.mp4;\n"
                "echo '{0}' > plate.svg".format(svg) + ";\n"
                "convert plate.svg -resize 50% plate.png"
            ),
            "grader_payload": "2",
        }
    }

    expected_response: dict = {
        "correct": False,
        "score": 0,
        "msg": ("Вы сделали подложку из прямоугольника? А заливка верная?\n"),
    }

    assert process_answer.process_answer(answer) == expected_response
