# External Grader
[![Build Status](https://travis-ci.org/Ragnaruk/external_grader.svg?branch=master)](https://travis-ci.org/Ragnaruk/ExternalGrader)
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

## Установка
### Docker
```bash
# Клонировать репозиторий на локальную машину
git clone https://github.com/Ragnaruk/external_grader.git

# Перейти в папку репозитория
cd external_grader

# Добавить конфигурацию используемой очереди в /external_grader/config_queue/
# Отредактировать файл docker-compose.yml

# Запустить файл установки с командой compose
make compose
```