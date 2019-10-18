"""
Шаблон файла со скриптом проверки и тестами.
"""


def main(answer, *args):
    """
    Тестовая проверочная функция.
    :param answer: ответ студента.
    :return: кортеж из оценки студента и сообщения.


    Юнит-тесты для проверки правильности работы функции:

    Неверный формат ответа.
    >>> main("test")
    Traceback (most recent call last):
      ...
    AssertionError: Ответ — не число.

    Неверный ответ.
    >>> main(4)
    Traceback (most recent call last):
      ...
    AssertionError: Ответ не равен 5.

    Верный ответ.
    >>> main(5)
    (100, 'Верный ответ.')
    """
    try:
        try:
            answer = int(answer)
        except ValueError:
            raise AssertionError("Ответ — не число.")

        assert answer == 5, "Ответ не равен 5."

        return 100, "Верный ответ."
    except AssertionError as exception:
        raise exception
    except Exception as exception:
        import logging
        logging.getLogger("ExternalGrader").error(exception)

        raise AssertionError("Неизвестная ошибка. Обратитесь к составителю скрипта проверки.")


if __name__ == '__main__':
    import doctest

    doctest.testmod(verbose=True)
