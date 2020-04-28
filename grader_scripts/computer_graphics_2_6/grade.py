import re
import xml.etree.ElementTree as ET
import sys


def solve():
    return '<svg width="400" height="200">\n<rect stroke-dasharray="10 5" stroke-width="2" stroke="grey" fill="tomato" height="180" width="180" y="1" x="1"/>\n<circle stroke-dasharray="10,5" stroke-width="2" stroke="grey" fill="lightblue" r="90" cy="91" cx="309"/>\n<polygon stroke-width="4" stroke="darkgrey" fill="lightgreen" points="110,199 200,43 290,199" />\n</svg>'


def get_xml_tree(reply):
    try:
        root = ET.fromstring(reply)
    except:
        return (
            False,
            "Проверьте ваш текст на наличие открывающих и закрывающих тегов <svg>, на наличие синтаксических ошибок в тегах и на то, что все теги закрыты",
        )
    return root


def check_all_elements_exist(root):
    if len(root) != 3:
        return False, "В вашей команде больше или меньше тегов, чем мы ожидаем"

    tags = [elem.tag for elem in root]

    for tag in ["rect", "circle", "polygon"]:
        if (tag in tags) == False:
            return (
                False,
                "Мы не нашли одну из фигур в вашей команде (иногда это сообщение появляется, если в теге svg есть лишние атрибуты)",
            )

    if tags.index("polygon") != 2:
        return False, "Вы расположили треугольник под одной из фигур"

    return [
        root.find("rect"),
        root.find("circle"),
        root.find("polygon"),
    ]  # return figures: square, circle, triangle


def check_field_size(root):
    if len(root.attrib) != 2:
        return False, "Проверьте тег svg"
    parameters = {"width": "400 ?(px)?", "height": "200 ?(px)?"}

    for key in parameters:
        value = re.compile(parameters[key])
        if ((key in root.attrib) and (value.match(root.attrib[key]) != None)) == False:
            return False, "Вы неверно задали размер листа"


def check_square(rect):
    if len(rect.attrib) != 8:
        return (
            False,
            "Количество параметров для квадрата отличается от ожидаемого (Вы забыли какой-то параметр или указали лишний)",
        )
    parameters = {
        "fill": "tomato",
        "stroke-dasharray": "10,? ?5",
        "stroke-width": "2 ?(px)?",
        "stroke": "gr[ae]y",
        "height": "180 ?(px)?",
        "width": "180 ?(px)?",
        "y": "1 ?(px)?",
        "x": "1 ?(px)?",
    }

    for key in parameters:
        value = re.compile(parameters[key])
        if ((key in rect.attrib) and (value.match(rect.attrib[key]) != None)) == False:
            return False, "Проверьте параметры квадрата"


def check_circle(circle):
    if len(circle.attrib) != 7:
        return (
            False,
            "Количество параметров для круга отличается от ожидаемого (Вы забыли какой-то параметр или указали лишний)",
        )
    parameters = {
        "stroke-dasharray": "10,? ?5",
        "stroke-width": "2 ?(px)?",
        "stroke": "gr[ae]y",
        "fill": "lightblue",
        "r": "90 ?(px)?",
        "cy": "91 ?(px)?",
        "cx": "309 ?(px)?",
    }

    for key in parameters:
        value = re.compile(parameters[key])
        if (
            (key in circle.attrib) and (value.match(circle.attrib[key]) != None)
        ) == False:
            return False, "Проверьте параметры круга"


def check_triangle(pol):
    if len(pol.attrib) != 4:
        return (
            False,
            "Количество параметров для треугольника отличается от ожидаемого (Вы забыли какой-то параметр или указали лишний)",
        )
    parameters = {
        "stroke-width": "4 ?(px)?",
        "stroke": "darkgr[ae]y",
        "fill": "lightgreen",
        "points": "(110,199 200,43 290,199)|(110,199 290,199 200,43)|(200,43 290,199 110,199)|(200,43 110,199 290,199)|(290,199 110,199 200,43)|(290,199 200,43 110,199)",
    }

    for key in parameters:
        value = re.compile(parameters[key])
        if ((key in pol.attrib) and (value.match(pol.attrib[key]) != None)) == False:
            return False, "Проверьте параметры треугольника"


def check(reply):
    reply = reply.lower()
    reply = " ".join(reply.split())  # replace multiple spaces with one
    root = get_xml_tree(reply)
    if len(root) == 2 and root[0] == False:
        return root

    elements = check_all_elements_exist(root)
    if len(elements) != 3:
        return elements

    foos = [
        check_field_size(root),
        check_square(elements[0]),
        check_circle(elements[1]),
        check_triangle(elements[2]),
    ]

    for foo in foos:
        ret = foo
        if ret:
            return ret

    return True, ""


if __name__ == "__main__":
    with open("./student_response.txt") as file:
        reply = file.read()

        correct, comment = check(reply)

        if correct:
            print(10)
            print("Верный ответ.", file=sys.stderr)
        else:
            print(0)
            print(comment, file=sys.stderr)
