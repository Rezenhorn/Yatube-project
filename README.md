# Проект Yatube
[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/downloads/release/python-379/) [![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/) [![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/index.html) [![Bootstrap](https://img.shields.io/badge/bootstrap-%23563D7C.svg?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)

## Описание:

Социальная сеть для публикации личных дневников. Она даёт пользователям возможность создать учетную запись, публиковать записи, подписываться на любимых авторов и оставлять комментарии.

## Запуск проекта в dev-режиме
### Клонировать репозиторий и перейти в него:
```
git clone https://github.com/Rezenhorn/Yatube-project
```
### Cоздать и активировать виртуальное окружение:
```
python -m venv venv
```
```
source venv/scripts/activate
```
### Установить зависимости из файла requirements.txt:
```
python -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```
### Выполнить миграции. В папке с файлом manage.py выполните команду:
```
python manage.py migrate
```
### Запустить сервер. В папке с файлом manage.py выполните команду:
```
python manage.py runserver
```