# -*- coding: UTF-8 -*-
import re
import random
import subprocess

from external_grader.config import HOME_PATH, VERIFICATION_FILES_PATH


################ Функция, которая запускается снаружи ################
def main(student_submission):
    s = subprocess

    prepare_grader(s, student_submission)

    test_commands_file(s)
    test_cropped_video(s)
    test_plate(s)
    test_IM_command(s)
    test_plated_video(s)
    test_final_video(s)


################ Создаем необходимые для проверки файлы ################
def prepare_grader(s, student_submission):
    s.run("wget https://stepic.org/media/attachments/lesson/22602/plate.svg -O /root/plate1.svg")
    s.run("wget https://stepic.org/media/attachments/lesson/22602/plate2.svg -O /root/plate2.svg")
    s.run("wget https://stepic.org/media/attachments/lesson/22602/input_video.mp4 -O /root/input_video.mp4")
    s.run("wget https://stepic.org/media/attachments/lesson/22602/arial.ttf -O /root/Arial.ttf")

    s.run("cp /root/Arial.ttf /home/box/Arial.ttf")
    s.run("cp /root/input_video.mp4 /home/box/input_video.mp4")
    s.run("echo '' > /home/box/commands.sh")
    s.run("chmod 0647 /home/box/commands.sh")

    with open(HOME_PATH + "commands.sh", "w") as f:
        print(student_submission, file=f)


################ Провеяем файл с командами ################
def test_commands_file(s):
    assert s.run(
        'test -e ' + HOME_PATH + 'commands.sh').succeeded, "Не найден командный файл 'commands.sh'"


################ Проверяем обрезанное видео ################
def get_starttime(s):
    ss = s.run("cat /home/box/commands.sh |grep -e '\-ss \{1,\}[0-9:\.]*' -o")
    assert (
                ss != '' and ss != None), "Мы не смогли найти в вашем командном файле время, начиная с которого вы отрезали видеофайл"
    ss = ss[
         3:].strip()  # оставляем только время, убирая '-ss' и отрезая пробелы по краям
    colon = ss.rfind(':')
    if colon != -1:
        ss = ss[colon + 1:]
    starttime = float(ss)
    assert (
                starttime >= 30 and starttime <= 44), "Вы задали начальное время обрезанного ролика вне того промежутка, где камера направлена в небо"
    return starttime


def check_duration(s, ss):
    t = s.run("cat /home/box/commands.sh |grep -E '\-(t|to) +{1,}[0-9:\.]*' -o")
    assert t != '' and t != None, "Мы не смогли найти длительность отрезаемого видеофайла (или конечный момент) в вашем командном файле"
    t = t.strip()
    if t[:3] == '-t ':
        assert re.compile('-t +((00:)?00:)?10(\.0+)?').match(
            t), 'Вы неверно задали длительность отрезаемого видеофрагмента'
    elif t[:3] == '-to':
        colon = t.rfind(':')
        if colon != -1:
            t = t[colon + 1:]
        else:
            t = t[3:].strip()
        t = float(t)
        assert t - ss == 10, "Вы неверно задали длительность отрезаемого видеофрагмента"
    else:
        assert False, "Вы неверно задали длительность отрезаемого видеофрагмента"


def compare_frames_in_cropped_video(s):
    s.run(
        'ffmpeg -i ' + HOME_PATH + 'cropped.mp4 -y ' + VERIFICATION_FILES_PATH + 'frame.png')
    s.run(
        'ffmpeg -i ' + VERIFICATION_FILES_PATH + 'cropped.mp4 -y ' + VERIFICATION_FILES_PATH + 'frame_origin.png')
    result = s.run(
        "compare " + VERIFICATION_FILES_PATH + "frame.png " + VERIFICATION_FILES_PATH + "frame_origin.png -compose Src -highlight-color White -lowlight-color Black :| convert - -resize 1x1\! -format '%[pixel:p{0,0}]' info:")
    s.run('rm ' + VERIFICATION_FILES_PATH + 'frame.png')
    s.run('rm ' + VERIFICATION_FILES_PATH + 'frame_origin.png')
    assert (result == 'gray(0,0,0)') or (result == 'black') or (
                result == 'gray(0)'), "Кажется, вы отрезали видеофрагмент не с той секунды, с какой указано в вашем командном файле."


def check_cropped_video(s, ss):
    ffmpeg_output = s.run('ffmpeg -i ' + HOME_PATH + 'cropped.mp4')
    assert ffmpeg_output.find(
        'Duration: 00:00:10.00') != -1, "Обрезанное видео имеет неверную длину"  # проверили длину отрезанного видео
    s.run('ffmpeg -i ' + HOME_PATH + 'input_video.mp4 -ss ' + str(
        ss) + ' -t 10 -c copy -y ' + VERIFICATION_FILES_PATH + 'cropped.mp4')  # создаем видео с границами из команды
    ffmpeg_origin = s.run('ffmpeg -i ' + VERIFICATION_FILES_PATH + 'cropped.mp4')
    start = ffmpeg_output.find('Stream #0:0')
    end = ffmpeg_output.rfind(',', 0, ffmpeg_output.find('kb/s', start))

    start_origin = ffmpeg_origin.find('Stream #0:0')
    end_origin = ffmpeg_origin.rfind(',', 0,
                                     ffmpeg_output.find('kb/s', start_origin))
    assert ffmpeg_output[start:end] == ffmpeg_origin[
                                       start_origin:end_origin], "Метаданные вашего обрезанного фрагмента не совпадают с ожидаемыми метаданными. Вы точно скопировали видеокодек?"
    compare_frames_in_cropped_video(s)


def test_cropped_video(s):
    assert s.run(
        'test -e ' + HOME_PATH + 'cropped.mp4').succeeded, "Не найден файл с обрезанным видео"
    ss = get_starttime(s)
    check_duration(s, ss)
    check_cropped_video(s, ss)


################ Проверяем плашку ################
def test_plate(s):
    assert s.run(
        'test -e ' + HOME_PATH + 'plate.svg').succeeded, "Не найден svg-файл с кодом плашки"
    svg = s.run('cat ' + HOME_PATH + 'plate.svg')
    assert svg != '', "Ваш svg-файл пуст"
    checklist = [['<circle .*cx *= *[\'"]?359(px)?[\'"]?',
                  "Вы перенесли круг на 50 пикселей вправо?"],
                 ['<rect .*x *= *[\'"]?51(px)?[\'"]?',
                  'Вы перенесли квадрат на 50 пикселей вправо?'], [
                     '<polygon .*(160,199 +250,43 +290,199)|(160,199 +340,199 +250,43)|(250,43 +340,199 +160,199)|(250,43 +160,199 +340,199)|(160,199 +340,199 +250,43)|(160,199 +250,43 +340,199)',
                     'Вы перенесли треугольник на 50 пикселей вправо?'],
                 ['<rect .*fill *= *[\'"]?rgba\(222, *222, *222, *0.5\)[\'"]?',
                  "Вы сделали подложку из прямоугольника? А заливка верная?"]]
    for param in checklist:
        assert re.compile(param[0]).search(svg) != None, param[1]

    s.run(
        "convert -background none " + VERIFICATION_FILES_PATH + "plate1.svg -resize 50% -depth 8 " + VERIFICATION_FILES_PATH + "plate1.png")
    s.run(
        "convert -background none " + VERIFICATION_FILES_PATH + "plate2.svg -resize 50% -depth 8 " + VERIFICATION_FILES_PATH + "plate2.png")
    s.run(
        "convert -background none " + VERIFICATION_FILES_PATH + "plate1.svg -depth 8 -resize 50% " + VERIFICATION_FILES_PATH + "plate3.png")
    s.run(
        "convert -background none " + VERIFICATION_FILES_PATH + "plate2.svg -depth 8 -resize 50% " + VERIFICATION_FILES_PATH + "plate4.png")

    res1 = s.run(
        "compare /root/plate1.png /home/box/plate.png -compose Src -highlight-color White -lowlight-color Black :| convert - -resize 1x1\! -format '%[pixel:p{0,0}]' info:")
    res2 = s.run(
        "compare /root/plate2.png /home/box/plate.png -compose Src -highlight-color White -lowlight-color Black :| convert - -resize 1x1\! -format '%[pixel:p{0,0}]' info:")
    res3 = s.run(
        "compare /root/plate3.png /home/box/plate.png -compose Src -highlight-color White -lowlight-color Black :| convert - -resize 1x1\! -format '%[pixel:p{0,0}]' info:")
    res4 = s.run(
        "compare /root/plate4.png /home/box/plate.png -compose Src -highlight-color White -lowlight-color Black :| convert - -resize 1x1\! -format '%[pixel:p{0,0}]' info:")
    if (res1 == 'gray(0,0,0)') or (res1 == 'black') or (res1 == 'gray(0)'):
        s.run(
            "cp /root/plate1.png /root/plate.png")  # if plate 1 match, replace plate with it
    elif (res2 == 'gray(0,0,0)') or (res2 == 'black') or (res2 == 'gray(0)'):
        s.run(
            "cp /root/plate2.png /root/plate.png")  # if plate 2 match, replace plate with it
    elif (res3 == 'gray(0,0,0)') or (res3 == 'black') or (res3 == 'gray(0)'):
        s.run("cp /root/plate3.png /root/plate.png")
    elif (res4 == 'gray(0,0,0)') or (res4 == 'black') or (res4 == 'gray(0)'):
        s.run("cp /root/plate4.png /root/plate.png")
    else:
        assert False, "Кажется, вы неправильно сформировали плашку для титров. Служебные цифры (могут помочь при наличии ошибки):" + str(
            res1) + str(res2)  # no plate match


def test_IM_command(s):
    assert s.run(
        "cat /home/box/commands.sh |grep -i -E 'convert .*(-depth +8 |png8: ?)' -o") != '', "Вы точно указали глубину цвета при конвертации плашки?"


################ Проверяем видео с плашкой ################
def compare_frames_in_plated_video(s):
    for d in [random.random(), 1.0, 1 + 8 * random.random(), 9.00,
              random.random() + 9]:  # проверяем плашку на (0,1), 1, (1,9), 9, (9, 10)
        t = "{0:.2f} ".format(d)
        s.run(
            'ffmpeg -i ' + HOME_PATH + 'plated.mp4 -ss ' + t + ' -y ' + VERIFICATION_FILES_PATH + 'frame.png')
        s.run(
            'ffmpeg -i ' + VERIFICATION_FILES_PATH + 'plated.mp4 -ss ' + t + ' -y ' + VERIFICATION_FILES_PATH + 'frame_origin.png')
        result = s.run(
            "compare " + VERIFICATION_FILES_PATH + "frame.png " + VERIFICATION_FILES_PATH + "frame_origin.png -compose Src -highlight-color White -lowlight-color Black :| convert - -resize 1x1\! -format '%[pixel:p{0,0}]' info:")
        s.run('rm ' + VERIFICATION_FILES_PATH + 'frame.png')
        s.run('rm ' + VERIFICATION_FILES_PATH + 'frame_origin.png')
        assert (result == 'gray(0,0,0)') or (result == 'black') or (
                    result == 'gray(0)'), 'Судя по видео, плашка наложена не в том промежутке, в котором ожидается'


def check_plated_video(s):
    ffmpeg_output = s.run('ffmpeg -i ' + HOME_PATH + 'plated.mp4')
    assert ffmpeg_output.find(
        'Duration: 00:00:10.00') != -1, "Видео с плашкой имеет неверную длину"  # проверили длину отрезанного видео
    ffmpeg_origin = s.run('ffmpeg -i ' + VERIFICATION_FILES_PATH + 'plated.mp4')
    start = ffmpeg_output.find('Stream #0:0')
    end = ffmpeg_output.rfind(',', 0, ffmpeg_output.find('kb/s', start))

    start_origin = ffmpeg_origin.find('Stream #0:0')
    end_origin = ffmpeg_origin.rfind(',', 0,
                                     ffmpeg_output.find('kb/s', start_origin))
    assert ffmpeg_output[start:end] == ffmpeg_origin[
                                       start_origin:end_origin], "Метаданные вашего видео с плашкой не совпадают с ожидаемыми метаданными. Вы точно не указывали параметров перекодирования?"
    compare_frames_in_plated_video(s)


def test_plated_video(s):
    assert s.run(
        'test -e ' + HOME_PATH + 'plated.mp4').succeeded, "Не найден видеофайл 'plated.mp4'"
    assert s.run(
        "cat /home/box/commands.sh |grep -E 'ffmpeg .+overlay *= *.*((x *= *)?0 *:(.*:)? ?(y *= *)?446|y *= *446 *:(.*:)? *x *= *0)' -o") != '', "Проверьте координаты в команде наложения плашки"
    s.run(
        'ffmpeg -i ' + VERIFICATION_FILES_PATH + 'cropped.mp4 -i ' + VERIFICATION_FILES_PATH + "plate.png -filter_complex overlay=0:446:enable='between(t\,1\,9)' -y " + VERIFICATION_FILES_PATH + 'plated.mp4')  # создаем эталонное видео с наложенной плашкой
    check_plated_video(s)


################ Проверяем видео с текстом ################
def get_text_and_fontsize(s):
    cmd = s.run("cat /home/box/commands.sh |grep -E 'ffmpeg .+drawtext'")
    assert cmd != '', "Мы не нашли команду для наложения текста"
    match = re.compile('[^w]text *= *').search(cmd)
    assert match != None, "Ошибка в команде наложения текста"
    start = match.end()  # получили первый символ после "=" и пробелов
    match = re.compile('[^\\\\]["\':]').search(cmd, start + 1)
    assert match != None, "Ошибка в команде наложения текста"
    end = match.end()
    end -= 1 if cmd[
                    end - 1] == ':' else 0  # если последним было двоеточие, сдвигаемся на предыдущий символ
    s.run('echo ' + cmd[start:end] + '>' + VERIFICATION_FILES_PATH + 'text.txt')
    fontsize = s.run(
        "cat /home/box/commands.sh |grep -E 'fontsize *= *[0-9]{1,2}' -o")
    assert fontsize != '', "Ошибка в команде наложения текста"
    fontsize = fontsize[
               fontsize.find('=') + 1:].strip()  # оставляем только цифры
    return fontsize


def compare_frames_in_result_video(s):
    for d in [2 * random.random(), 2.0, 2 + 7 * random.random(), 9.00,
              random.random() + 9]:  # проверяем текст на (0,2), 2, (2,9), 9, (9, 10)
        t = "{0:.2f} ".format(d)
        s.run(
            'ffmpeg -i ' + HOME_PATH + 'result.mp4 -ss ' + t + ' -y ' + VERIFICATION_FILES_PATH + 'frame.png')
        s.run(
            'ffmpeg -i ' + VERIFICATION_FILES_PATH + 'result.mp4 -ss ' + t + ' -y ' + VERIFICATION_FILES_PATH + 'frame_origin.png')
        result = s.run(
            "compare " + VERIFICATION_FILES_PATH + "frame.png " + VERIFICATION_FILES_PATH + "frame_origin.png -compose Src -highlight-color White -lowlight-color Black :| convert - -resize 1x1\! -format '%[pixel:p{0,0}]' info:")
        s.run('rm ' + VERIFICATION_FILES_PATH + 'frame.png')
        s.run('rm ' + VERIFICATION_FILES_PATH + 'frame_origin.png')
        assert (result == 'gray(0,0,0)') or (result == 'black') or (
                    result == 'gray(0)'), 'Судя по видео, текст наложен не в том промежутке, в котором ожидается. Или вы наложили не тот текст.'


def check_result_video(s):
    ffmpeg_output = s.run('ffmpeg -i ' + HOME_PATH + 'result.mp4')
    assert ffmpeg_output.find(
        'Duration: 00:00:10.00') != -1, "Итоговое видео имеет неверную длину"  # проверили длину отрезанного видео
    ffmpeg_origin = s.run('ffmpeg -i ' + VERIFICATION_FILES_PATH + 'result.mp4')
    start = ffmpeg_output.find('Stream #0:0')
    end = ffmpeg_output.rfind(',', 0, ffmpeg_output.find('kb/s', start))

    start_origin = ffmpeg_origin.find('Stream #0:0')
    end_origin = ffmpeg_origin.rfind(',', 0,
                                     ffmpeg_output.find('kb/s', start_origin))
    assert ffmpeg_output[start:end] == ffmpeg_origin[
                                       start_origin:end_origin], "Метаданные вашего итогового видео не совпадают с ожидаемыми метаданными. Вы точно не указывали параметров перекодирования?"
    compare_frames_in_result_video(s)


def test_final_video(s):
    assert s.run(
        'test -e ' + HOME_PATH + 'result.mp4').succeeded, "Мы не нашли итоговое видео"
    fontsize = get_text_and_fontsize(
        s)  # получаем текст для наложения и размер шрифта
    assert s.run(
        'ffmpeg -i ' + VERIFICATION_FILES_PATH + 'plated.mp4 -filter_complex drawtext=x=200:y=476:fontfile=Arial.ttf:fontsize=' + fontsize + ':textfile=' + VERIFICATION_FILES_PATH + 'text.txt:enable=\'between(t\,2\,9)\' -y ' + VERIFICATION_FILES_PATH + 'result.mp4').succeeded, "Пожалуйста, выберите текст для наложения без сложных комбинаций кавычек"
    check_result_video(s)
