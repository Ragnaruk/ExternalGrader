# Шаблон скрипта проверки.
В директории `/grader_scripts/` создается папка с id скрипта. Этот id будет приходит в поле `grader_payload`.

В папке скрипта должны быть файлы grade.py и settings.json.

### grade.py
Файл, где находится основная логика скрипта проверки.

Значение поля `score` берется из stdout, а поля `msg` — из stderr.
Поле `correct` равно `true`, если `score` = 100, иначе — `false`.

Ответ студента будет находится в файле: `student_submission.txt`.
Он и все файлы из settings.json будут находится в одной директории со скриптом проверки.

Должен иметь возможность запускаться по команде: `python3 grade.py`.
То есть иметь структуру похожую на:
```python
def main():
    print("Проверка")


if __name__ == '__main__':
    main()
```

Если для проверки кода нужны пакеты, отсутствующие в стандарной библиотеке Python, их нужно устанавливать динамически:
```python
import subprocess
import sys


def install(package):
    subprocess.call(
        [sys.executable, "-m", "pip", "install", package]
    )
```

### settings.json
Файл, где находятся настройки скрипта проверки.

Формат настроек:
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
  "container_limits": {
    "cputime": 1,
    "realtime": 3,
    "memory": 64,
    "processes": -1
  },
  "profile": {
    "docker_image": "ragnaruk/python:latest",
    "user": "student",
    "read_only": true,
    "network_disabled": true
  }
}
```

Поля:
* `files` — список файлов, необходимых для проверки.
    * `name` — название, которое будет иметь загруженный файл.
    * `link` — ссылка на файл.
    * `path` — относительный путь до файла.
* `container_limits` — лимиты контейнера.
    * `cputime` — время процессора в секундах. 
    * `realtime` — время выполнения в секундах.
    * `memory` — количество оперативной памяти в мегабайтах.
    * `processes` — количество возможных процессов. -1 для бесконечного.
* `epicbox_profile` — профиль для контейнера.
    * `docker_image` — название Docker-образа, который будет взят за основу контейнера.
    * `user` — имя пользователя, от которого будет запущен скрипт.
    * `read_only` — разрешение записи файлов внутри контейнера.
    * `network_disabled` — разрешение использование сети.
