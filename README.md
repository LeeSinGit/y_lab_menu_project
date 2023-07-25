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
#### ШАГ 3 - Подключить виртуальное окружение командой source venv/Scripts/activate;
```
source venv/Scripts/activate
```
#### ШАГ 4 - Установить зависимости командой pip install -r requirements.txt;
```
pip install -r requirements.txt
```
#### ШАГ 5 - Перейти в директорию api/ и активировать скрипт создания таблиц в базе данных командой py create_db.py;
```
cd api/                       py create_db.py или python create_db.py
```
#### ШАГ 6 - Включить сервер uvicorn командой python -m uvicorn main:app --reload или uvicorn main:app --reload;
```
python -m uvicorn main:app --reload или uvicorn main:app --reload
```
#### ШАГ 7 - Прогнать сценарий в POSTMAN, должны пройти все тесты - (Passed 161);
****


##### p.s. специально не прятал данные в .env и .gitignore, чтобы не возникло проблем при проверке.
