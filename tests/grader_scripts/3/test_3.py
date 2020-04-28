"""
PyTest test file for grader_scripts.3.grade module.
"""
import pytest

from external_grader import process_answer


@pytest.mark.skip(reason="No access to a camera.")
def test_grade_incorrect():
    """
    Test grader_scripts.3.grade script.
    """
    answer: dict = {
        "xqueue_body": {
            "student_response": """from onvif import ONVIFCamera
cam = ONVIFCamera("172.18.191.143", "80", "admin", "Supervisor")
media_service = cam.create_media_service()
profiles = media_service.GetProfiles()
media_profile = profiles[0]
ptz = cam.create_ptz_service()
status = ptz.GetStatus({"ProfileToken": media_profile.token})
status.Position.PanTilt.x = 0.6
status.Position.PanTilt.y = 0.6
status.Position.Zoom.x = 0.0
request_absolute_move = ptz.create_type("AbsoluteMove")
request_absolute_move.ProfileToken = media_profile.token
request_absolute_move.Position = status.Position
ptz.AbsoluteMove(request_absolute_move)
""",
            "grader_payload": "3",
        }
    }

    expected_response: dict = {
        "correct": False,
        "score": 0,
        "msg": "Неверная позиция камеры. Ожидалось: 0.7 : 0.7 : 0.0. Текущая: 0.6 : 0.6 : 0.0.\n",
    }

    assert process_answer.process_answer(answer) == expected_response


@pytest.mark.skip(reason="No access to a camera.")
def test_grade_correct():
    """
    Test grader_scripts.3.grade script.
    """
    answer: dict = {
        "xqueue_body": {
            "student_response": """from onvif import ONVIFCamera
cam = ONVIFCamera("172.18.191.143", "80", "admin", "Supervisor")
media_service = cam.create_media_service()
profiles = media_service.GetProfiles()
media_profile = profiles[0]
ptz = cam.create_ptz_service()
status = ptz.GetStatus({"ProfileToken": media_profile.token})
status.Position.PanTilt.x = 0.7
status.Position.PanTilt.y = 0.7
status.Position.Zoom.x = 0.0
request_absolute_move = ptz.create_type("AbsoluteMove")
request_absolute_move.ProfileToken = media_profile.token
request_absolute_move.Position = status.Position
ptz.AbsoluteMove(request_absolute_move)
""",
            "grader_payload": "3",
        }
    }

    expected_response: dict = {
        "correct": True,
        "score": 1,
        "msg": "Верный ответ.\n",
    }

    assert process_answer.process_answer(answer) == expected_response
