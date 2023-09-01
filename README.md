# Сервис отправки сообщений

Настоящий сервис позволяет отправлять уведомления в личные сообщения или группы мессенджеров (пока работает только с телеграмом). При этом нельзя отправить более 3-х одинаковых сообщений в один и тот же чат в течение суток (даже если эти сообщения оправляются с разных ip-адресов).

Реализовано 2 ручки\
**POST /notify_with_text** - отправляет текстовое уведомление в чат/группу мессенджера\
**POST /notify_with_files** - вместе с текстом отправляет файлы в чат/группу мессенджера


### Запуск
После установки библиотек из requirements.txt в venv в корне проекта набрать команду:
```bash
python main.py
```
Перейти сюда: http://localhost:8000/docs
И подключить вебхук http://localhost:8000/docs/setwebhook, предварительно задав WEBHOOK_HOST в config/config.py

<hr>

### Пользование


#### 1. Через веб интерфейс openapi
API cервиса расположен по адресу: http://localhost:8000/docs



##### /notify_with_text

Тело запроса имеет слюдующие поля:
 - "service" - название сервиса (string). Возможные значения: ["telegram"]
 - "text": сообщение (string)
 - "destination": id чата/группы (int)
 - "title": название сообщения (string) - опционально
 - "author": автор сообщения (string) - опционально

##### /notify_with_files
Тут тело представлено в виде формы. Каждое поле вбивается отдельно.
Также вместе с сообщением можно отправлять файлы. Если не планируете их отправлять, то надо снять галочку с поля **Send empty value**


#### 2. Через Postman

##### POST http://localhost:8000/docs/notify_with_text

Тело запроса имеет те же поля:
 - "service" - название сервиса (string). Возможные значения: ["telegram"]
 - "text": сообщение (string)
 - "destination": id чата/группы (int)
 - "title": название сообщения (string) - опционально
 - "author": автор сообщения (string) - опционально

Удобнее тело добавлять в виде json объекта

##### POST http://localhost:8000/docs/notify_with_files

Добавляем header Content-Type == multipart/form-data
Тело заполняем в формате form-data

![alt text](images/postman_example.JPG "Title")


<hr>


Тестовые данные для **/notify_with_text** лежат в [example.json](example.json),
где '-829479897' - id группы в телеграме. 
