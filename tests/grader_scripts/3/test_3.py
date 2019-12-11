"""
PyTest test file for grader_scripts.3.grade module.
"""
from external_grader import process_answer


# def test_grade_incorrect():
#     """
#     Test grader_scripts.3.grade script.
#     """
#     answer: dict = {
#         "xqueue_body": {
#             "student_response": (
#                 "from onvif import ONVIFCamera\n"
#                 "cam = ONVIFCamera(\"172.18.191.143\", \"80\", \"admin\", \"Supervisor\")\n"
#                 "media_service = cam.create_media_service()\n"
#                 "profiles = media_service.GetProfiles()\n"
#                 "media_profile = profiles[0]\n"
#                 "ptz = cam.create_ptz_service()\n"
#                 "status = ptz.GetStatus({\"ProfileToken\": media_profile.token})\n"
#                 "status.Position.PanTilt.x = 0.6\n"
#                 "status.Position.PanTilt.y = 0.6\n"
#                 "status.Position.Zoom.x = 0.0\n"
#                 "request_absolute_move = ptz.create_type(\"AbsoluteMove\")\n"
#                 "request_absolute_move.ProfileToken = media_profile.token\n"
#                 "request_absolute_move.Position = status.Position\n"
#                 "ptz.AbsoluteMove(request_absolute_move)\n"
#             ),
#             "grader_payload": "3"
#         }
#     }
#
#     expected_response: dict = {
#         "correct": False,
#         "score": 0,
#         "msg": "Неверная позиция камеры.\nОжидалось: 0.7 : 0.7 : 0.0\nТекущая: 0.6 : 0.6 : 0.0\n",
#     }
#
#     assert process_answer.process_answer(answer) == expected_response


# def test_grade_correct():
#     """
#     Test grader_scripts.3.grade script.
#     """
#     answer: dict = {
#         "xqueue_body": {
#             "student_response": (
#                 "from onvif import ONVIFCamera\n"
#                 "cam = ONVIFCamera(\"172.18.191.143\", \"80\", \"admin\", \"Supervisor\")\n"
#                 "media_service = cam.create_media_service()\n"
#                 "profiles = media_service.GetProfiles()\n"
#                 "media_profile = profiles[0]\n"
#                 "ptz = cam.create_ptz_service()\n"
#                 "status = ptz.GetStatus({\"ProfileToken\": media_profile.token})\n"
#                 "status.Position.PanTilt.x = 0.7\n"
#                 "status.Position.PanTilt.y = 0.7\n"
#                 "status.Position.Zoom.x = 0.0\n"
#                 "request_absolute_move = ptz.create_type(\"AbsoluteMove\")\n"
#                 "request_absolute_move.ProfileToken = media_profile.token\n"
#                 "request_absolute_move.Position = status.Position\n"
#                 "ptz.AbsoluteMove(request_absolute_move)\n"
#             ),
#             "grader_payload": "3"
#         }
#     }
#
#     expected_response: dict = {
#         "correct": True,
#         "score": 1,
#         "msg": "Верный ответ.\n",
#     }
#
#     assert process_answer.process_answer(answer) == expected_response
