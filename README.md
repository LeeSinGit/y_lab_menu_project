# y_lab_menu_project
Проект на FastAPI с использованием PostgreSQL в качестве БД

### Как запустить проект:
****
#### ШАГ 0 - Клонировать проект к себе на PC;
```
git clone git@github.com:LeeSinGit/y_lab_menu_project.git
```
#### ШАГ 1 - СОЗДАТЬ в pgAdmin 4 базу данных под названием 'menu_db' (databases->create);
```
menu_db
```
#### ШАГ 2 - Зайти в корневую директорию проекта;
#### ШАГ 3 - Создать вирутальное окружение;
```
py -m venv venv
```
#### ШАГ 4 - Подключить виртуальное окружение;
```
source venv/Scripts/activate
```
#### ШАГ 5 - Установить зависимости;
```
pip install -r requirements.txt
```
#### ШАГ 6 - Перейти в директорию api/;
```
cd api/
```
#### ШАГ 7 - Активировать скрипт создания таблиц в базе данных;
```
py create_db.py
```
##### OR
```
python create_db.py
```
#### ШАГ 8 - Включить сервер uvicorn;
```
python -m uvicorn main:app --reload
```
##### OR
```
uvicorn main:app --reload
```
#### ШАГ 9 - Прогнать сценарий в POSTMAN.
****
### *Над проектом работал Лисин Семён :heart:*
### *Код написан на языке Python :v:*
