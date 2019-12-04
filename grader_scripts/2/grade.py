# -*- coding: UTF-8 -*-
import sys
import re
import random
import subprocess as s
from pathlib import Path

PATH_CWD = str(Path().absolute()) + "/"


################ Функция, которая запускается снаружи ################
def main():
    test_commands_file(s)

    run_submission(s)

    test_cropped_video(s)
    test_plate(s)
    test_IM_command(s)
    test_plated_video(s)
    test_final_video(s)


def run_submission(s):
    s.run(
        "sh " + PATH_CWD + "student_response.txt",
        shell=True,
        cwd=PATH_CWD,
    )


################ Провеяем файл с командами ################
def test_commands_file(s):
    assert (
        s.call(
            "test -e " + PATH_CWD + "student_response.txt",
            shell=True,
            cwd=PATH_CWD,
        )
        == 0
    ), "Не найден командный файл."


################ Проверяем обрезанное видео ################
def get_starttime(s):
    try:
        ss = s.check_output(
            "cat "
            + PATH_CWD
            + "student_response.txt |grep -e '\\-ss \\{1,\\}[0-9:\\.]*' -o",
            shell=True,
        )
    except Exception:
        raise AssertionError("Мы не смогли найти в вашем командном файле время, начиная с которого вы отрезали видеофайл.")

    ss = ss.decode("UTF-8")

    assert (
        ss != "" and ss is not None
    ), "Мы не смогли найти в вашем командном файле время, начиная с которого вы отрезали видеофайл."

    # оставляем только время, убирая '-ss' и отрезая пробелы по краям
    ss = str(ss[3:].strip())

    colon = ss.rfind(":")

    if colon != -1:
        ss = ss[colon + 1:]

    starttime = float(ss)

    assert (
        starttime >= 30 and starttime <= 44
    ), "Вы задали начальное время обрезанного ролика вне того промежутка, где камера направлена в небо."

    return starttime


def check_duration(s, ss):
    try:
        t = s.check_output(
            "cat "
            + PATH_CWD
            + "student_response.txt | grep -E '\-(t|to) +{1,}[0-9:\.]*' -o",
            shell=True,
        )
    except Exception:
        raise AssertionError("Мы не смогли найти длительность отрезаемого видеофайла (или конечный момент) в вашем командном файле.")

    t = t.decode("UTF-8")

    assert (
        t != "" and t is not None
    ), "Мы не смогли найти длительность отрезаемого видеофайла (или конечный момент) в вашем командном файле."

    t = t.strip()
    if t[:3] == "-t ":
        assert re.compile("-t +((00:)?00:)?10(\.0+)?").match(
            t
        ), "Вы неверно задали длительность отрезаемого видеофрагмента."
    elif t[:3] == "-to":
        colon = t.rfind(":")
        if colon != -1:
            t = t[colon + 1 :]
        else:
            t = t[3:].strip()
        t = float(t)
        assert t - ss == 10, "Вы неверно задали длительность отрезаемого видеофрагмента."
    else:
        assert False, "Вы неверно задали длительность отрезаемого видеофрагмента."


def compare_frames_in_cropped_video(s):
    s.run(
        "ffmpeg -hide_banner -loglevel panic -i "
        + PATH_CWD
        + "cropped.mp4 -y "
        + PATH_CWD
        + "frame.png",
        shell=True,
    )
    s.run(
        "ffmpeg -hide_banner -loglevel panic -i "
        + PATH_CWD
        + "cropped.mp4 -y "
        + PATH_CWD
        + "frame_origin.png",
        shell=True,
    )
    result = s.run(
        "compare "
        + PATH_CWD
        + "frame.png "
        + PATH_CWD
        + "frame_origin.png -compose Src -highlight-color White -lowlight-color Black :| convert - -resize 1x1\! -format '%[pixel:p{0,0}]' info:",
        shell=True,
    )
    s.run(
        "rm " + PATH_CWD + "frame.png",
        shell=True,
        cwd=PATH_CWD,
    )
    s.run(
        "rm " + PATH_CWD + "frame_origin.png",
        shell=True,
        cwd=PATH_CWD,
    )
    assert (
        (result == "gray(0,0,0)") or (result == "black") or (result == "gray(0)")
    ), "Кажется, вы отрезали видеофрагмент не с той секунды, с какой указано в вашем командном файле."


def check_cropped_video(s, ss):
    ffmpeg_output = s.check_output(
        "ffmpeg -hide_banner -loglevel panic -i " + PATH_CWD + "cropped.mp4",
        shell=True,
        capture_output=True,
    )

    ffmpeg_output = ffmpeg_output.decode("UTF-8")

    # проверили длину отрезанного видео
    assert (
        ffmpeg_output.find("Duration: 00:00:10.00") != -1
    ), "Обрезанное видео имеет неверную длину."

    s.run(
        "ffmpeg -hide_banner -loglevel panic -i "
        + PATH_CWD
        + "input_video.mp4 -ss "
        + str(ss)
        + " -t 10 -c copy -y "
        + PATH_CWD
        + "cropped.mp4",
        shell=True,
    )  # создаем видео с границами из команды
    ffmpeg_origin = s.run(
        "ffmpeg -hide_banner -i " + PATH_CWD + "cropped.mp4", shell=True,
    ).stdout
    start = ffmpeg_output.find("Stream #0:0")
    end = ffmpeg_output.rfind(",", 0, ffmpeg_output.find("kb/s", start))

    start_origin = ffmpeg_origin.find("Stream #0:0")
    end_origin = ffmpeg_origin.rfind(",", 0, ffmpeg_output.find("kb/s", start_origin))
    assert (
        ffmpeg_output[start:end] == ffmpeg_origin[start_origin:end_origin]
    ), "Метаданные вашего обрезанного фрагмента не совпадают с ожидаемыми метаданными. Вы точно скопировали видеокодек?"
    compare_frames_in_cropped_video(s)


def test_cropped_video(s):
    assert (
        s.call(
            "test -e " + PATH_CWD + "cropped.mp4",
            shell=True,
            cwd=PATH_CWD,
        )
        == 0
    ), "Не найден файл с обрезанным видео."

    ss = get_starttime(s)

    check_duration(s, ss)
    check_cropped_video(s, ss)


################ Проверяем плашку ################
def test_plate(s):
    assert (
        s.call(
            "test -e " + PATH_CWD + "plate.svg",
            shell=True,
            cwd=PATH_CWD,
        )
        == 0
    ), "Не найден svg-файл с кодом плашки"
    svg = s.run(
        "cat " + PATH_CWD + "plate.svg", shell=True, cwd=PATH_CWD
    ).stdout
    assert svg != "", "Ваш svg-файл пуст"
    checklist = [
        [
            "<circle .*cx *= *['\"]?359(px)?['\"]?",
            "Вы перенесли круг на 50 пикселей вправо?",
        ],
        [
            "<rect .*x *= *['\"]?51(px)?['\"]?",
            "Вы перенесли квадрат на 50 пикселей вправо?",
        ],
        [
            "<polygon .*(160,199 +250,43 +290,199)|(160,199 +340,199 +250,43)|(250,43 +340,199 +160,199)|(250,43 +160,199 +340,199)|(160,199 +340,199 +250,43)|(160,199 +250,43 +340,199)",
            "Вы перенесли треугольник на 50 пикселей вправо?",
        ],
        [
            "<rect .*fill *= *['\"]?rgba\(222, *222, *222, *0.5\)['\"]?",
            "Вы сделали подложку из прямоугольника? А заливка верная?",
        ],
    ]
    for param in checklist:
        assert re.compile(param[0]).search(svg) != None, param[1]

    s.run(
        "convert -background none "
        + PATH_CWD
        + "plate1.svg -resize 50% -depth 8 "
        + PATH_CWD
        + "plate1.png",
        shell=True,
    )
    s.run(
        "convert -background none "
        + PATH_CWD
        + "plate2.svg -resize 50% -depth 8 "
        + PATH_CWD
        + "plate2.png",
        shell=True,
    )
    s.run(
        "convert -background none "
        + PATH_CWD
        + "plate1.svg -depth 8 -resize 50% "
        + PATH_CWD
        + "plate3.png",
        shell=True,
    )
    s.run(
        "convert -background none "
        + PATH_CWD
        + "plate2.svg -depth 8 -resize 50% "
        + PATH_CWD
        + "plate4.png",
        shell=True,
    )

    res1 = s.run(
        "compare "
        + PATH_CWD
        + "plate1.png "
        + PATH_CWD
        + "plate.png -compose Src -highlight-color White -lowlight-color Black :| convert - -resize 1x1\! -format '%[pixel:p{0,0}]' info:",
        shell=True,
    ).stdout
    res2 = s.run(
        "compare "
        + PATH_CWD
        + "plate2.png "
        + PATH_CWD
        + "plate.png -compose Src -highlight-color White -lowlight-color Black :| convert - -resize 1x1\! -format '%[pixel:p{0,0}]' info:",
        shell=True,
    ).stdout
    res3 = s.run(
        "compare "
        + PATH_CWD
        + "plate3.png "
        + PATH_CWD
        + "plate.png -compose Src -highlight-color White -lowlight-color Black :| convert - -resize 1x1\! -format '%[pixel:p{0,0}]' info:",
        shell=True,
    ).stdout
    res4 = s.run(
        "compare "
        + PATH_CWD
        + "plate4.png "
        + PATH_CWD
        + "plate.png -compose Src -highlight-color White -lowlight-color Black :| convert - -resize 1x1\! -format '%[pixel:p{0,0}]' info:",
        shell=True,
    ).stdout
    if (res1 == "gray(0,0,0)") or (res1 == "black") or (res1 == "gray(0)"):
        s.run(
            "cp "
            + PATH_CWD
            + "plate1.png "
            + PATH_CWD
            + "plate.png",
            shell=True,
        )  # if plate 1 match, replace plate with it
    elif (res2 == "gray(0,0,0)") or (res2 == "black") or (res2 == "gray(0)"):
        s.run(
            "cp "
            + PATH_CWD
            + "plate2.png "
            + PATH_CWD
            + "plate.png",
            shell=True,
        )  # if plate 2 match, replace plate with it
    elif (res3 == "gray(0,0,0)") or (res3 == "black") or (res3 == "gray(0)"):
        s.run(
            "cp "
            + PATH_CWD
            + "plate3.png "
            + PATH_CWD
            + "plate.png",
            shell=True,
            cwd=PATH_CWD,
        )
    elif (res4 == "gray(0,0,0)") or (res4 == "black") or (res4 == "gray(0)"):
        s.run(
            "cp "
            + PATH_CWD
            + "plate4.png "
            + PATH_CWD
            + "plate.png",
            shell=True,
            cwd=PATH_CWD,
        )
    else:
        assert False, (
            "Кажется, вы неправильно сформировали плашку для титров. Служебные цифры (могут помочь при наличии ошибки):"
            + str(res1)
            + str(res2)
        )  # no plate match


def test_IM_command(s):
    assert (
        s.run(
            "cat "
            + PATH_CWD
            + "student_response.txt |grep -i -E 'convert .*(-depth +8 |png8: ?)' -o",
            shell=True,
        )
        != ""
    ), "Вы точно указали глубину цвета при конвертации плашки?"


################ Проверяем видео с плашкой ################
def compare_frames_in_plated_video(s):
    for d in [
        random.random(),
        1.0,
        1 + 8 * random.random(),
        9.00,
        random.random() + 9,
    ]:  # проверяем плашку на (0,1), 1, (1,9), 9, (9, 10)
        t = "{0:.2f} ".format(d)
        s.run(
            "ffmpeg -hide_banner -loglevel panic -i "
            + PATH_CWD
            + "plated.mp4 -ss "
            + t
            + " -y "
            + PATH_CWD
            + "frame.png",
            shell=True,
        )
        s.run(
            "ffmpeg -hide_banner -loglevel panic -i "
            + PATH_CWD
            + "plated.mp4 -ss "
            + t
            + " -y "
            + PATH_CWD
            + "frame_origin.png",
            shell=True,
        )
        result = s.run(
            "compare "
            + PATH_CWD
            + "frame.png "
            + PATH_CWD
            + "frame_origin.png -compose Src -highlight-color White -lowlight-color Black :| convert - -resize 1x1\! -format '%[pixel:p{0,0}]' info:",
            shell=True,
        ).stdout
        s.run(
            "rm " + PATH_CWD + "frame.png",
            shell=True,
            cwd=PATH_CWD,
        )
        s.run(
            "rm " + PATH_CWD + "frame_origin.png",
            shell=True,
            cwd=PATH_CWD,
        )
        assert (
            (result == "gray(0,0,0)") or (result == "black") or (result == "gray(0)")
        ), "Судя по видео, плашка наложена не в том промежутке, в котором ожидается."


def check_plated_video(s):
    ffmpeg_output = s.run(
        "ffmpeg -hide_banner -i " + PATH_CWD + "plated.mp4",
        shell=True,
        cwd=PATH_CWD,
    ).stdout
    assert (
        ffmpeg_output.find("Duration: 00:00:10.00") != -1
    ), "Видео с плашкой имеет неверную длину"  # проверили длину отрезанного видео
    ffmpeg_origin = s.run(
        "ffmpeg -hide_banner -i " + PATH_CWD + "plated.mp4", shell=True,
    ).stdout
    start = ffmpeg_output.find("Stream #0:0")
    end = ffmpeg_output.rfind(",", 0, ffmpeg_output.find("kb/s", start))

    start_origin = ffmpeg_origin.find("Stream #0:0")
    end_origin = ffmpeg_origin.rfind(",", 0, ffmpeg_output.find("kb/s", start_origin))
    assert (
        ffmpeg_output[start:end] == ffmpeg_origin[start_origin:end_origin]
    ), "Метаданные вашего видео с плашкой не совпадают с ожидаемыми метаданными. Вы точно не указывали параметров перекодирования?"
    compare_frames_in_plated_video(s)


def test_plated_video(s):
    assert (
        s.call(
            "test -e " + PATH_CWD + "plated.mp4",
            shell=True,
            cwd=PATH_CWD,
        )
        == 0
    ), "Не найден видеофайл 'plated.mp4'"
    assert (
        s.run(
            "cat "
            + PATH_CWD
            + "student_response.txt |grep -E 'ffmpeg .+overlay *= *.*((x *= *)?0 *:(.*:)? ?(y *= *)?446|y *= *446 *:(.*:)? *x *= *0)' -o",
            shell=True,
        )
        != ""
    ), "Проверьте координаты в команде наложения плашки"
    s.run(
        "ffmpeg -hide_banner -loglevel panic -i "
        + PATH_CWD
        + "cropped.mp4 -i "
        + PATH_CWD
        + "plate.png -filter_complex overlay=0:446:enable='between(t\,1\,9)' -y "
        + PATH_CWD
        + "plated.mp4",
        shell=True,
    )  # создаем эталонное видео с наложенной плашкой
    check_plated_video(s)


################ Проверяем видео с текстом ################
def get_text_and_fontsize(s):
    cmd = s.run(
        "cat "
        + PATH_CWD
        + "student_response.txt |grep -E 'ffmpeg .+drawtext'",
        shell=True,
        cwd=PATH_CWD,
    ).stdout
    assert cmd != "", "Мы не нашли команду для наложения текста"
    match = re.compile("[^w]text *= *").search(cmd)
    assert match != None, "Ошибка в команде наложения текста"
    start = match.end()  # получили первый символ после "=" и пробелов
    match = re.compile("[^\\\\][\"':]").search(cmd, start + 1)
    assert match != None, "Ошибка в команде наложения текста"
    end = match.end()
    end -= (
        1 if cmd[end - 1] == ":" else 0
    )  # если последним было двоеточие, сдвигаемся на предыдущий символ
    s.run(
        "echo " + cmd[start:end] + ">" + PATH_CWD + "text.txt",
        shell=True,
    )
    fontsize = s.run(
        "cat "
        + PATH_CWD
        + "student_response.txt |grep -E 'fontsize *= *[0-9]{1,2}' -o",
        shell=True,
    ).stdout
    assert fontsize != "", "Ошибка в команде наложения текста"
    fontsize = fontsize[fontsize.find("=") + 1 :].strip()  # оставляем только цифры
    return fontsize


def compare_frames_in_result_video(s):
    for d in [
        2 * random.random(),
        2.0,
        2 + 7 * random.random(),
        9.00,
        random.random() + 9,
    ]:  # проверяем текст на (0,2), 2, (2,9), 9, (9, 10)
        t = "{0:.2f} ".format(d)
        s.run(
            "ffmpeg -hide_banner -loglevel panic -i "
            + PATH_CWD
            + "result.mp4 -ss "
            + t
            + " -y "
            + PATH_CWD
            + "frame.png",
            shell=True,
        )
        s.run(
            "ffmpeg -hide_banner -loglevel panic -i "
            + PATH_CWD
            + "result.mp4 -ss "
            + t
            + " -y "
            + PATH_CWD
            + "frame_origin.png",
            shell=True,
        )
        result = s.run(
            "compare "
            + PATH_CWD
            + "frame.png "
            + PATH_CWD
            + "frame_origin.png -compose Src -highlight-color White -lowlight-color Black :| convert - -resize 1x1\! -format '%[pixel:p{0,0}]' info:",
            shell=True,
        ).stdout
        s.run(
            "rm " + PATH_CWD + "frame.png",
            shell=True,
            cwd=PATH_CWD,
        )
        s.run(
            "rm " + PATH_CWD + "frame_origin.png",
            shell=True,
            cwd=PATH_CWD,
        )
        assert (
            (result == "gray(0,0,0)") or (result == "black") or (result == "gray(0)")
        ), "Судя по видео, текст наложен не в том промежутке, в котором ожидается. Или вы наложили не тот текст."


def check_result_video(s):
    ffmpeg_output = s.run(
        "ffmpeg -hide_banner -i " + PATH_CWD + "result.mp4",
        shell=True,
        cwd=PATH_CWD,
    ).stdout
    assert (
        ffmpeg_output.find("Duration: 00:00:10.00") != -1
    ), "Итоговое видео имеет неверную длину"  # проверили длину отрезанного видео
    ffmpeg_origin = s.run(
        "ffmpeg -hide_banner -i " + PATH_CWD + "result.mp4", shell=True,
    ).stdout
    start = ffmpeg_output.find("Stream #0:0")
    end = ffmpeg_output.rfind(",", 0, ffmpeg_output.find("kb/s", start))

    start_origin = ffmpeg_origin.find("Stream #0:0")
    end_origin = ffmpeg_origin.rfind(",", 0, ffmpeg_output.find("kb/s", start_origin))
    assert (
        ffmpeg_output[start:end] == ffmpeg_origin[start_origin:end_origin]
    ), "Метаданные вашего итогового видео не совпадают с ожидаемыми метаданными. Вы точно не указывали параметров перекодирования?"
    compare_frames_in_result_video(s)


def test_final_video(s):
    assert (
        s.call(
            "test -e " + PATH_CWD + "result.mp4",
            shell=True,
            cwd=PATH_CWD,
        )
        == 0
    ), "Мы не нашли итоговое видео"
    fontsize = get_text_and_fontsize(s)  # получаем текст для наложения и размер шрифта
    assert (
        s.call(
            "ffmpeg -hide_banner -loglevel panic -i "
            + PATH_CWD
            + "plated.mp4 -filter_complex drawtext=x=200:y=476:fontfile=Arial.ttf:fontsize="
            + fontsize
            + ":textfile="
            + PATH_CWD
            + "text.txt:enable='between(t\,2\,9)' -y "
            + PATH_CWD
            + "result.mp4",
            shell=True,
        )
        == 0
    ), "Пожалуйста, выберите текст для наложения без сложных комбинаций кавычек"
    check_result_video(s)


if __name__ == "__main__":
    try:
        main()

        print(1)
    except AssertionError as exception:
        print(exception, file=sys.stderr)
        print(0)
    except Exception as exception:
        exc_info = sys.exc_info()

        print("Unhandled error during grading.", file=sys.stderr)
        print(exception, file=sys.stderr)
        print(exc_info, file=sys.stderr)
        print(0)
