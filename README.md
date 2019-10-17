# External Grader
[![Build Status](https://travis-ci.org/Ragnaruk/external_grader.svg?branch=master)](https://travis-ci.org/Ragnaruk/ExternalGrader)

Внешний грейдер для LMS, работающий по формату Edx.

## Установка

### Docker
```bash
## Установка брокера сообщений RabbitMQ
docker pull rabbitmq:3-management
docker run -idt -p 5672:5672 -p 15672:15672 --name rabbitmq --hostname my-rabbit rabbitmq:3-management

## Установка грейдера
git clone https://github.com/Ragnaruk/ExternalGrader.git

grader
docker build -t external_grader .
docker run -idt --name external_grader --network="host" external_grader
```

### Без Docker
```bash
## Установка грейдера
git clone https://github.com/Ragnaruk/ExternalGrader.git
pip install -r ./requirements.txt

# Перед этим шагом можно изменить файл конфигураций /external_grader/config.py
python ./external_grader/
```

## Формат сообщений
Грейдер получает и отправляет сообщения в формате EDX.

Пример получаемого сообщения:
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
    "grader_payload": "1"
   }
}
```

Пример отправляемого сообщения:
```json
{
  "xqueue_header": {
    "submission_id": 72,
    "submission_key": "ffcd933556c926a307c45e0af5131995"
  },
  "xqueue_body": {
    "correct": true,
    "score": 1,
    "msg": grader
  }
}
```

Поле `xqueue_header` является неизменяемым и служит для идентификации одной цепочки сообщений.

Поле `grader_payload` несет id скрипта проверки.

В ответе грейдера гарантирована правильность содержания только поля `correct`. Поля `score` и `msg` могут быть заполнены по желанию составителя скрипта проверки.

## Добавление проверочного скрипта
Грейдер может расширятся пользовательскими проверочными скриптами.

В директории `grade_scripts` создается новая директория с id скрипта, а в ней создается проверочный файл.

Шаблон для проверочного скрипта находится в директории `/grade_scripts/1/`.

### Требования:
* Скрипт должен иметь название `grade.py`.
* Скрипт должен содержать функцию `main`, которая принимает ответ студента и список файлов.
* Функция `main` может возвращать оценку и сообщение, которые записываются в поля `score` и `msg`.
* Если функция падает с ошибкой AssertionError, то грейдер возвращает сообщение, где поле `correct` имеет значение `false`. Сообщение об ошибке может быть записано в поле `msg`.
* Если функция выполняется без ошибок, то грейдер возвращает сообщение, где поле `correct` имеет значение `true`. Оценка может быть записана в поле `score`, а комментарий к ответу — в поле `msg`.