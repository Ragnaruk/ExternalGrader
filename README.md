# External Grader
[![Build Status](https://travis-ci.com/Ragnaruk/external_grader.svg?branch=master)](https://travis-ci.com/Ragnaruk/external_grader)
[![codecov](https://codecov.io/gh/Ragnaruk/external_grader/branch/master/graph/badge.svg)](https://codecov.io/gh/Ragnaruk/external_grader)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](https://github.com/Ragnaruk/external_grader/blob/master/LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Codecov Graph](https://codecov.io/gh/Ragnaruk/external_grader/branch/master/graphs/icicle.svg)](https://codecov.io/gh/Ragnaruk/external_grader/branch/master/graphs/icicle.svg)

## Описание
Внешний грейдер для проверки ответов на задачи, использующий [XQueue JSON Objects](https://edx.readthedocs.io/projects/edx-partner-course-staff/en/latest/exercises_tools/external_graders.html#xqueue-json-objects) для коммуникации.

Эта имплементация использует формат опрашивающего (polling) грейдера. То есть грейдер ждет появления ответа в заданной очереди, после чего берет его, проверяет и возвращает обратно оценку и комментарии.

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
* [Тестирование](#Тестирование)
* [Ссылки](#Ссылки)

## Установка
### Docker
```bash
# Клонировать репозиторий на локальную машину
git clone https://github.com/Ragnaruk/external_grader.git

# Перейти в папку репозитория
cd external_grader

# Добавить конфигурацию используемой очереди в /external_grader/queue_configuration/
# Примеры конфигураций очередей лежат в этой же директории

# Отредактировать файл /external_grader/config.py по желанию

# Отредактировать файл /docker-compose.yml
# Не забыть указать название файла с конфигурацией очереди в переменной окружения QUEUE_CONFIG_NAME
# Не забыть удалить ненужные сервисы из файла

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

Значение `grader_payload` может быть словарем, но тогда он должен содержать поле `script_id`.


## Добавление скриптов проверки
В директории `/grader_scripts/` создается папка с id скрипта. Этот id будет приходит в поле `grader_payload`.

В папке скрипта должны быть файлы `grade.py` и `settings.json`.

### grade.py
Файл, где находится основная логика скрипта проверки.

Ответ студента будет находится в файле с названием `student_submission.txt`.
Он и все файлы зависимостей из `settings.json` будут находится в одной директории со скриптом проверки.

Должен иметь возможность запускаться по команде: `python grade.py`, то есть иметь структуру похожую на:
```python
def main():
    print("Проверка")


if __name__ == '__main__':
    main()
```

Значение поля `score` берется из `stdout`, а поля `msg` — из `stderr` контейнера.

Поле `correct` равно `true`, если `score` отлично от 0, иначе — `false`.

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
* `profile` — профиль для контейнера.
    * `docker_image` — название Docker-образа, который будет взят за основу контейнера.
    * `user` — имя пользователя, от которого будет запущен скрипт.
    * `read_only` — разрешение записи файлов внутри контейнера.
    * `network_disabled` — разрешение использование сети.

## Тестирование
В директории `/tests/` находятся юнит-тесты, сделанные с помощью библиотеки PyTest.

Тесты автоматически выполняются при каждом коммите в этот репозиторий.
Статус тестов и покрытие кода ими есть в шапке этого файла.

Для ручного запуска тестов необходимо:
```bash
# Установка зависимостей для тестирования
make requirements-test

# Обычное тестирование
make test

# Тестирование с указанием процента покрытия кода тестами
make test-cov
```


## Ссылки
* [edX External Grader](https://edx.readthedocs.io/projects/edx-partner-course-staff/en/latest/exercises_tools/external_graders.html) — описание внешнего грейдера.
* [queue_watcher](https://github.com/edx/xqueue-watcher) — альтернативная имплементация внешнего грейдера.
* [epicbox](https://github.com/StepicOrg/epicbox) — модуль для безопасного запуска кода.
