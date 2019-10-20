# Шаблон скрипта проверки.

## grade.py
Файл, где находится основаная логика скрипта проверки.

Должен иметь возможность запускаться по команде: python grade.py.

То есть иметь структуру:
```python
def main():
    print("Проверка")

if __name__ == '__main__':
    main()
```

Если для проверки кода нужны пакеты, отсутсвующие в стандарной библиотеке Python, их можно установить так:
```python
import subprocess
import sys

def install(package):
    subprocess.call([sys.executable, "-m", "pip", "install", package])
```

Ответ студента будет находится в файле `student_submission.txt`, который будет находится в той же директории, что и скрипт проверки.

## settings.json
Файл, где находятся зависимости, используемые скриптом проверки, и имя Docker образа.

Имеет формат:
```json
{
  "files": {
    "external": [
      {
        "name": "test-external.txt",
        "link": "http://captive.apple.com"
      }
    ],
    "local": [
      {
        "name": "test-local.txt",
        "path": "settings.json"
      }
    ]
  },
  "docker_image": "python:3.8-alpine"
}
```

Поля:
* `name` — название, которое будет иметь итоговый файл.
* `link` — ссылка на файл.
* `path` — относительный относительно директории проверочного скрипта путь до файла.
