# Disinfection Requests System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.0+-lightgrey.svg)

Веб приложение для учёта и обработки заявок на заключительную дезинфекцию. Проект реализован с целью ознакомления с фреймворком Flask. 

## 📌 Основные функции

- 📝 Создание заявок на дезинфекцию
- 🏷️ Учёт и обработка заявок
- 🔍 Фильтрация и поиск заявок
- 📊 Статистика и отчёты
- 👨‍⚕️ Мониторинг изменения статуса заявки (в работе, исполнен, отказ)

## 🛠 Технологии

- **Backend**: Python 3, Flask, SQLAlchemy
- **Frontend**: Bootstrap 5, Jinja2, Vanilla js
- **База данных**: PostgreSQL
- **Деплой**: Docker-ready

## 🚀 Быстрый старт

Установи `POSTGRESHOST=localhost`
Создай виртуальное окружение 
Установи зависимости
запусти flask

```bash
python -m venv env
pip install -r requirements.txt
flask run
```


## 🐳 Запуск через Docker

Собери и запусти контейнер

```bash
docker-compose up --build```
