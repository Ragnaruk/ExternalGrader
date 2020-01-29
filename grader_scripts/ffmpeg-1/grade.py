import re
import sys


def get_answer():
    """
    Read student answer from the file.

    :return: Student answer.
    """
    with open("./student_response.txt") as file:
        return file.read().splitlines()


def run_job(answer: str, job: dict, grade: float, feedback: str):
    """
    Match answer to regex inside job dictionary.
    Add weight to grade if successful, else add comment to feedback.

    :param answer: Answer.
    :param job: Dictionary with regex, weight, and comment.
    :param grade: Current grade for the answer.
    :param feedback: Current feedback for the answer.
    :return: Modified answer, grade, and feedback.
    """
    match = re.search(job["regex"], answer)

    if match:
        grade += job["weight"]
        answer = answer.replace(match[0], "", 1)
    else:
        feedback += job["comment"] + "\n"

    return answer, grade, feedback


def run_extra(answer: str, grade: float, max_grade: float, feedback: str, regex: str):
    """
    Run an extra job if all others are correct.

    :param answer: Answer.
    :param grade: Current grade for the answer.
    :param max_grade: Max grade for the answer.
    :param feedback: Current feedback for the answer.
    :param regex: Regex to match against.
    :return: Modified grade and feedback.
    """
    if round(grade, 1) == max_grade:
        match = re.search(regex, answer)

        if match:
            grade += 0.1
            feedback += "Верно.\n"
        else:
            feedback += "Что-то лишнее.\n"

    return grade, feedback


def task_1(answer: str):
    """
    Grade task 1.

    :param answer: Answer.
    """
    grade = 0
    feedback = ""

    jobs = [
        {"regex": r"^\s*ffmpeg(\.exe)?\s+", "comment": "Вызов ffmpeg.", "weight": 0.1,},
        {"regex": r"-i\s+input\.mp4\s+", "comment": "Входной файл.", "weight": 0.1},
        {"regex": r"output\.mp4\s*$", "comment": "Выходной файл.", "weight": 0.1},
        {
            "regex": r"-ss\s+((0?0:(0?0:)?)?0)?2\s+",
            "comment": "Начало фрагмента.",
            "weight": 0.3,
        },
        {
            "regex": r"-(t\s+(0?0:(0?0:)?)?10|to\s+(0?0:(0?0:)?)?12)\s+",
            "comment": "Длина (окончание) фрагмента.",
            "weight": 0.3,
        },
    ]

    for job in jobs:
        answer, grade, feedback = run_job(answer, job, grade, feedback)

    grade, feedback = run_extra(answer, grade, 0.9, feedback, r"^\s*$")

    global total_grade
    total_grade += round(grade, 1)

    global total_feedback
    total_feedback += "Задание 1: {0}/{1}\n{2}".format(round(grade, 1), 1.0, feedback)


def task_2_1(answer_1: str, answer_2: str):
    """
    Grade task 2_1.

    :param answer_1: Bitrate.
    :param answer_2: Answer.
    """
    grade = 0
    feedback = ""

    job = {
        "regex": r"^\s*2360(k|000)\s*$",
        "comment": "Изначальный битрейт.",
        "weight": 0.3,
    }

    _, grade, feedback = run_job(answer_1, job, grade, feedback)

    jobs = [
        {"regex": r"^\s*ffmpeg(\.exe)?\s+", "comment": "Вызов ffmpeg.", "weight": 0.1,},
        {"regex": r"-i\s+input\.mp4\s+", "comment": "Входной файл.", "weight": 0.1},
        {"regex": r"output\.mp4\s*$", "comment": "Выходной файл.", "weight": 0.1},
        {"regex": r"-b\s+1180(k|000)\s+", "comment": "Битрейт.", "weight": 0.3},
    ]

    for job in jobs:
        answer_2, grade, feedback = run_job(answer_2, job, grade, feedback)

    grade, feedback = run_extra(answer_2, grade, 0.9, feedback, r"^\s*$")

    global total_grade
    total_grade += round(grade, 1)

    global total_feedback
    total_feedback += "\nЗадание 2. Часть 1: {0}/{1}\n{2}".format(
        round(grade, 1), 1.0, feedback
    )


def task_2_2(answer_1: str, answer_2: str):
    """
    Grade task 2_2.

    :param answer_1: Bitrate.
    :param answer_2: Answer.
    """
    grade = 0
    feedback = ""

    job = {
        "regex": r"^\s*129(k|000)\s*$",
        "comment": "Изначальный битрейт.",
        "weight": 0.3,
    }

    _, grade, feedback = run_job(answer_1, job, grade, feedback)

    jobs = [
        {"regex": r"^\s*ffmpeg(\.exe)?\s+", "comment": "Вызов ffmpeg.", "weight": 0.1,},
        {"regex": r"-i\s+input\.mp4\s+", "comment": "Входной файл.", "weight": 0.1},
        {"regex": r"output\.mp4\s*$", "comment": "Выходной файл.", "weight": 0.1},
        {
            "regex": r"-b:a\s+6((4([\.,]5)?|5)k|4(5|0)00)\s+",
            "comment": "Битрейт.",
            "weight": 0.3,
        },
    ]

    for job in jobs:
        answer_2, grade, feedback = run_job(answer_2, job, grade, feedback)

    grade, feedback = run_extra(answer_2, grade, 0.9, feedback, r"^\s*$")

    global total_grade
    total_grade += round(grade, 1)

    global total_feedback
    total_feedback += "\nЗадание 2. Часть 2: {0}/{1}\n{2}".format(
        round(grade, 1), 1.0, feedback
    )


def task_3(answer: str):
    """
    Grade task 3.

    :param answer: Answer.
    """
    grade = 0
    feedback = ""

    jobs = [
        {"regex": r"^\s*ffmpeg(\.exe)?\s+", "comment": "Вызов ffmpeg.", "weight": 0.1,},
        {"regex": r"-i\s+input\.mp4\s+", "comment": "Входной файл.", "weight": 0.1},
        {"regex": r"output\.mp4\s*$", "comment": "Выходной файл.", "weight": 0.1},
        {
            "regex": r"-c:a\s+(mp3|libmp3lame)\s+",
            "comment": "Аудиокодек.",
            "weight": 0.3,
        },
        {"regex": r"-c:v\s+copy\s+", "comment": "Видеокодек.", "weight": 0.3},
    ]

    for job in jobs:
        answer, grade, feedback = run_job(answer, job, grade, feedback)

    grade, feedback = run_extra(answer, grade, 0.9, feedback, r"^\s*$")

    global total_grade
    total_grade += round(grade, 1)

    global total_feedback
    total_feedback += "\nЗадание 3: {0}/{1}\n{2}".format(round(grade, 1), 1.0, feedback)


def task_4(answer: str):
    """
    Grade task 4.

    :param answer: Answer.
    """
    grade = 0
    feedback = ""

    jobs = [
        {"regex": r"^\s*ffmpeg(\.exe)?\s+", "comment": "Вызов ffmpeg.", "weight": 0.1,},
        {"regex": r"-i\s+input\.mp4\s+", "comment": "Входной файл.", "weight": 0.1},
        {"regex": r"output\.gif\s*$", "comment": "Выходной файл.", "weight": 0.1},
        {"regex": r"-s\s+640x480\s+", "comment": "Размер.", "weight": 0.3},
    ]

    # Something
    ss = 0
    match = re.search(r"-ss\s+((\d{1,3}:[0-6])?\d:[0-6])?\d(\.\d{1,2})?", answer)

    if match:
        colon = match[0].rindex(":")

        if not colon:
            colon = match[0].index(" ")

        ss = int(match[0][colon + 1 : -1])

        answer = answer.replace(match[0], "", 1)

    # Something
    match = re.search(r"-t\s+(0?0:(0?0:)?)?10(\.00?)?", answer)

    if not match:
        match = re.search(r"-to\s+((\d{1,3}:[0-6])?\d:[0-6])?\d", answer)
        if not match:
            feedback += "Длительность.\n"
        else:
            colon = match[0].rindex(":")

            if not colon:
                colon = match[0].index(" ")

            t = int(match[0][colon + 1 : -1])

            if t - ss == 10 or t - ss == -50:
                grade += 0.3

                answer = answer.replace(match[0], "", 1)
            else:
                feedback += "Длительность.\n"
    else:
        grade += 0.3

        answer = answer.replace(match[0], "", 1)

    # Main
    for job in jobs:
        answer, grade, feedback = run_job(answer, job, grade, feedback)

    grade, feedback = run_extra(answer, grade, 0.9, feedback, r"^\s*(-f\s+gif)?\s*$")

    global total_grade
    total_grade += round(grade, 1)

    global total_feedback
    total_feedback += "\nЗадание 4: {0}/{1}\n{2}".format(round(grade, 1), 1.0, feedback)


def task_5_1(answer: str):
    """
    Grade task 5_1.

    :param answer: Answer.
    """
    grade = 0
    feedback = ""

    jobs = [
        {"regex": r"^\s*ffmpeg(\.exe)?\s+", "comment": "Вызов ffmpeg.", "weight": 0.1,},
        {"regex": r"-i\s+input\.mp4\s+", "comment": "Входной файл.", "weight": 0.1},
        {"regex": r"output%d\.png\s*$", "comment": "Выходные файлы.", "weight": 0.3},
        {
            "regex": r"-to?\s+(0?0:(0?0:)?)?0?1(\.00?)?",
            "comment": "Длительность.",
            "weight": 0.1,
        },
    ]

    for job in jobs:
        answer, grade, feedback = run_job(answer, job, grade, feedback)

    match = re.search(r"-f\s+image2", answer)

    if match:
        answer = answer.replace(match[0], "", 1)

    grade, feedback = run_extra(answer, grade, 0.6, feedback, r"^\s*(-an)?\s*$")

    global total_grade
    total_grade += round(grade, 1)

    global total_feedback
    total_feedback += "\nЗадание 5. Часть 1: {0}/{1}\n{2}".format(
        round(grade, 1), 0.7, feedback
    )


def task_5_2(answer: str):
    """
    Grade task 5_2.

    :param answer: Answer.
    """
    grade = 0
    feedback = ""

    jobs = [
        {"regex": r"^\s*ffmpeg(\.exe)?\s+", "comment": "Вызов ffmpeg.", "weight": 0.1},
        {"regex": r"-i\s+input%d\.png\s+", "comment": "Входные файлы.", "weight": 0.3},
        {"regex": r"output\.mp4\s*$", "comment": "Выходной файл.", "weight": 0.1},
        {"regex": r"-r\s+25", "comment": "Частота кадров.", "weight": 0.2},
        {
            "regex": r"-c:v\s+(libx264(rgb)?|h264)",
            "comment": "Видеокодек.",
            "weight": 0.3,
        },
        {"regex": r"-b(:v)?\s+1024(k|000)", "comment": "Битрейт.", "weight": 0.2},
    ]

    for job in jobs:
        answer, grade, feedback = run_job(answer, job, grade, feedback)

    match = re.search(r"-f\s+image2", answer)

    if match:
        answer = answer.replace(match[0], "", 1)

    grade, feedback = run_extra(answer, grade, 1.2, feedback, r"^\s*(-an)?\s*$")

    global total_grade
    total_grade += round(grade, 1)

    global total_feedback
    total_feedback += "\nЗадание 5. Часть 2: {0}/{1}\n{2}".format(
        round(grade, 1), 1.3, feedback
    )


def task_6(answer: str):
    """
    Grade task 6.

    :param answer: Answer.
    """
    grade = 0
    feedback = ""

    jobs = [
        {"regex": r"^\s*ffmpeg(\.exe)?\s+", "comment": "Вызов ffmpeg.", "weight": 0.1},
        {"regex": r"-i\s+input\.mp4\s+", "comment": "Входной файл.", "weight": 0.1},
        {"regex": r"output\.avi\s*$", "comment": "Выходной файл.", "weight": 0.4},
        {"regex": r"-s\s+640x360\s+", "comment": "Размер.", "weight": 0.3},
        {"regex": r"-c:v\s+mpeg2?video\s+", "comment": "Видеокодек.", "weight": 0.4},
        {"regex": r"-c:a\s+(mp3|libmp3lame)", "comment": "Аудиокодек.", "weight": 0.4},
        {
            "regex": r"-ss\s+(00:)?3[78]:[0-6]\d(\.\d{1,2})?\s+",
            "comment": "Время начала.",
            "weight": 0.4,
        },
        {
            "regex": r"-t(\s+(00:)?(10|0?[89])|o\s+(00:)?4[67]):[0-6]\d(\.\d{1,2})?\s+",
            "comment": "Время окончания (длительность).",
            "weight": 0.4,
        },
        {
            "regex": r"-b(\s+1879|:v\s+1684)(000|k)\s+",
            "comment": "Битрейт.",
            "weight": 0.4,
        },
    ]

    for job in jobs:
        answer, grade, feedback = run_job(answer, job, grade, feedback)

    grade, feedback = run_extra(answer, grade, 2.9, feedback, r"^\s*$")

    global total_grade
    total_grade += round(grade, 1)

    global total_feedback
    total_feedback += "\nЗадание 6: {0}/{1}\n{2}".format(round(grade, 1), 3.0, feedback)


if __name__ == "__main__":
    total_grade = 0
    total_feedback = ""

    student_answer = get_answer()

    try:
        task_1(student_answer[0])
        task_2_1(student_answer[1], student_answer[2])
        task_2_2(student_answer[3], student_answer[4])
        task_3(student_answer[5])
        task_4(student_answer[6])
        task_5_1(student_answer[7])
        task_5_2(student_answer[8])
        task_6(student_answer[9])
    except IndexError:
        pass

    print(round(total_grade, 1))
    print(total_feedback, file=sys.stderr)
