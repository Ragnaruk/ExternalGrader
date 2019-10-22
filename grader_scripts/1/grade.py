"""
Шаблон файла со скриптом проверки.
"""
import sys


def main():
    """
    Check whether student submission equals 5.

    :return: Grade of the student.
    """
    try:
        answer = read_student_submission()

        parsed_answer = int(answer)
    except ValueError:
        print("Ответ — не число.", file=sys.stderr)

        print(0)
    else:
        if parsed_answer == -1000:
            print("Неверный формат сообщений.", file=sys.stderr)

            print("Неверный формат сообщений.")
        elif parsed_answer != 5:
            print("Ответ не равен 5.", file=sys.stderr)

            print(50)
        else:
            print("Верный ответ.", file=sys.stderr)

            print(100)


def read_student_submission() -> str:
    """
    Read student submission from file.

    :return: Student submission.
    """
    with open("./student_response.txt") as file:
        return file.read()


if __name__ == '__main__':
    try:
        main()
    except Exception as exception:
        exc_info = sys.exc_info()

        print("Unhandled error during grading.", file=sys.stderr)
        print("%s", exception, file=sys.stderr)
        print("%s", exc_info, file=sys.stderr)
