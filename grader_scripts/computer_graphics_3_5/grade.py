import re
import sys


def solve():
    return 'ffmpeg -i in.mp4 -c:v h264 -b:v 5000k -minrate 5M -bufsize 1000k -maxrate 5000000 -s 1280x720 -r 25 -profile:v high -level:v 42 -bf 2 -g 13 -b:a 128k  -c:a aac -strict -2 -ar 96k out.mp4'


def cut_reply(matching, reply):
    coords = matching.span()
    return reply[0:coords[0]] + reply[coords[1]:]


def check(reply):
    if len(reply) == 0:
        return 0, "Ответ пуст"
    reply = reply.lower()

    end = re.search('out\.mp4"?$', reply)
    if not re.search("^ffmpeg ", reply) or not end:
        return 0, "Что-то не так в начале команды или имя выходного файла неверное"
    reply = reply[7:-len(end.group())]
    infile = re.search('-i +in\.[\w\d]{3,4}', reply)
    # входной файл
    if not infile:
        return 0, "Название входного файла"
    reply = cut_reply(infile, reply)

    # видео кодек
    matching = re.search('-c:v +(h264|libx264)', reply)
    if not matching:
        return 0, "Видео кодек"
    reply = cut_reply(matching, reply)

    # видео битрейт
    vbitrates = ['-b:v +(5000k|5m|5000000) ', '-minrate +(5000k|5m|5000000) ',
                 '-maxrate +(5000k|5m|5000000) ', '-bufsize +(\d{3,4}k|\dm|\d{5,7}) ']
    regexs = [re.compile(elem) for elem in vbitrates]

    for reg in regexs:
        matching = reg.search(reply)
        if matching == None:
            return 0, "Видео битрейт"
        reply = cut_reply(matching, reply)

    # Профиль
    matching = re.search('-profile:v +high ', reply)
    if not matching:
        return 0, "Профиль видео"
    reply = cut_reply(matching, reply)

    # Уровень
    matching = re.search('-level(:v)? +4\.?2 ', reply)
    if not matching:
        return 0, "Уровень видео"
    reply = cut_reply(matching, reply)

    # размер
    matching = re.search('-s +1280x720 ', reply)
    if not matching:
        return 0, "Размер"
    reply = cut_reply(matching, reply)

    # fps
    matching = re.search('-r +25 ', reply)
    if not matching:
        return 0, "Частота кадров"
    reply = cut_reply(matching, reply)

    # B-frames
    matching = re.search('-bf +2 ', reply)
    if not matching:
        return 0, "B-кадры"
    reply = cut_reply(matching, reply)

    # GOP
    matching = re.search('-g(op)? +(12|13|25/2|12[,\.]5) ', reply)
    if not matching:
        return 0, "Длина GOP"
    reply = cut_reply(matching, reply)

    # Аудио кодек
    matching = re.search('-c:a +(aac|libvo_aacenc|libfdk_aac|libfaac) ', reply)
    if not matching:
        return 0, "Аудио кодек"
    reply = cut_reply(matching, reply)

    if matching.group() == '-c:a aac ':  # нужны дополнительные ключи
        matching = re.search('-strict ', reply)
        if matching:
            reply = cut_reply(matching, reply)

        matching = re.search('(-2|experimental) +', reply)
        if matching:
            reply = cut_reply(matching, reply)

    # Аудио битрейт
    matching = re.search('-b:a +128(k|000) ', reply)
    if not matching:
        return 0, "Аудио битрейт"
    reply = cut_reply(matching, reply)

    # Субдискретизация
    matching = re.search('-(ar|r:a) +96(k|000) ', reply)
    if not matching:
        return 0, "Дискретизация аудио"
    reply = cut_reply(matching, reply)

    if not (len(reply) == 0) and (not re.match('^\s*(-f\s+mp4)?\s*$', reply)):
        return 0, "Что-то лишнее"

    return 1, ""  # OK


if __name__ == "__main__":
    with open("./student_response.txt") as file:
        reply = file.read()

        correct, comment = check(reply)

        if correct:
            print(1)
            print("Верный ответ.", file=sys.stderr)
        else:
            print(0)
            print(comment, file=sys.stderr)
