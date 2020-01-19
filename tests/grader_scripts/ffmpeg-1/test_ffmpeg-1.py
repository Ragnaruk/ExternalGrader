"""
PyTest test file for grader_scripts.ffmpeg-1.grade module.
"""
from external_grader import process_answer


def test_grade_correct():
    """
    Test grader_scripts.1.grade script.
    """
    answer: dict = {
        "xqueue_body": {
            "student_response": """ffmpeg -i input.mp4 -ss 00:00:02 -t 00:00:10 output.mp4
            2360k
            ffmpeg -i input.mp4 -b 1180k output.mp4
            129k
            ffmpeg -i input.mp4 -b:a 64500 output.mp4
            ffmpeg -i input.mp4 -c:v copy -c:a mp3 output.mp4
            ffmpeg -i input.mp4 -s 640x480 -t 00:00:10 output.gif
            ffmpeg -i input.mp4 -f image2 -t 00:00:01 output%d.png
            ffmpeg -i input%d.png -c:v h264 -b 1024k -r 25 output.mp4
            ffmpeg -i input.mp4 -ss 00:37:50 -to 00:47:10 -s 640x360 -c:v mpeg2video -c:a mp3 -b:v 1684k output.avi""",
            "grader_payload": "ffmpeg-1",
        }
    }

    expected_response: dict = {
        "correct": True,
        "score": 10.0,
        "msg": """Задание 1: 1.0/1.0
Верно.

Задание 2. Часть 1: 1.0/1.0
Верно.

Задание 2. Часть 2: 1.0/1.0
Верно.

Задание 3: 1.0/1.0
Верно.

Задание 4: 1.0/1.0
Верно.

Задание 5. Часть 1: 0.7/0.7
Верно.

Задание 5. Часть 2: 1.3/1.3
Верно.

Задание 6: 3.0/3.0
Верно.

""",
    }

    assert process_answer.process_answer(answer) == expected_response
