# External Grader
[![Build Status](https://travis-ci.org/Ragnaruk/external_grader.svg?branch=master)](https://travis-ci.org/Ragnaruk/external_grader)
[![codecov](https://codecov.io/gh/Ragnaruk/external_grader/branch/master/graph/badge.svg)](https://codecov.io/gh/Ragnaruk/external_grader)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](https://github.com/Ragnaruk/external_grader/blob/master/LICENSE)
[![Codecov Graph](https://codecov.io/gh/Ragnaruk/external_grader/branch/master/graphs/icicle.svg)](https://codecov.io/gh/Ragnaruk/external_grader/branch/master/graphs/icicle.svg)

## Описание
Внешний грейдер для проверки ответов на задачи, использующий [XQueue JSON Objects](https://edx.readthedocs.io/projects/edx-partner-course-staff/en/latest/exercises_tools/external_graders.html#xqueue-json-objects) для коммуникации.

Эта имплементация использует формат опрашивающего (polling) грейдера. То есть грейдер ждет появления ответа в заданной очереди, после чего берет его, проверяет и возвращает обратно.

## Оглавление
* [Описание](#Описание)
* [Оглавление](#Оглавление)
* [Установка](#Установка)
    * [Docker](#Docker)
* [Эксплуатация](#Эксплуатация)
    * [Формат получаемых сообщений](#Формат-получаемых-сообщений)
* [Добавление скриптов проверки](#Добавление-скриптов-проверки)
    * [grade.py](#gradepy)
    * [settings.json](#settingsjson)
* [Ссылки](#Ссылки)

## Установка
### Docker
```bash
# Клонировать репозиторий на локальную машину
git clone https://github.com/Ragnaruk/external_grader.git

# Перейти в папку репозитория
cd external_grader

# Добавить конфигурацию используемой очереди в /external_grader/config_queue/
# Отредактировать файл /external_grader/config/config.py
docker_images

# Запустить файл установки с командой compose
make compose
```

## Эксплуатация
### Формат получаемых сообщений
Пример полученного сообщения:
```json
{
  "xqueue_header": {
    "submission_id": 72,
    "submission_key": "ffcd933556c926a307c45e0af5131995"
  },
  "xqueue_files": {
    "helloworld.c": "http://download.location.com/helloworld.c"
  },
  "xqueue_body": {
    "student_info": {
      "anonymous_student_id": "106ecd878f4148a5cabb6bbb0979b730",
      "submission_time": "20160324104521",
      "random_seed": 334
    },
    "student_response": "def double(x):\n return 2*x\n",
    "grader_payload": "problem_2"
   }
}
```

В качестве ответа студента используется поле `student_response` в словаре `xqueue_body`.

Если поле пустое, то файл `student_response.txt` в словаре `xqueue_files`.

## Добавление скриптов проверки
В директории `/grader_scripts/` создается папка с id скрипта. Этот id будет приходит в поле `grader_payload`.

В папке скрипта должны быть файлы grade.py и settings.json.

### grade.py
Файл, где находится основная логика скрипта проверки.

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
  "docker_image": "ragnaruk/python:latest",
  "container_limits": {
    "cputime": 1,
    "realtime": 3,
    "memory": 64,
    "processes": -1
  }
}
```

Поля:
* `files` — список файлов, необходимых для проверки.
    * `name` — название, которое будет иметь загруженный файл.
    * `link` — ссылка на файл.
    * `path` — относительный путь до файла.
* `docker_image` — название Docker-образа, который будет взят за основу контейнера.
* `container_limits` — лимиты контейнера.
    * `cputime` — время процессора в секундах. 
    * `realtime` — время выполнения в секундах.
    * `memory` — количество оперативной памяти в мегабайтах.
    * `processes` — количество возможных процессов. -1 для бесконечного.

## Ссылки
* [edX External Grader](https://edx.readthedocs.io/projects/edx-partner-course-staff/en/latest/exercises_tools/external_graders.html) — описание внешнего грейдера.
* [queue_watcher](https://github.com/edx/xqueue-watcher) — альтернативная имплементация внешнего грейдера.
* [epicbox](https://github.com/StepicOrg/epicbox) — модуль для безопасного запуска кода.
