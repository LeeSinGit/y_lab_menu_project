# y_lab_menu_project
Проект на FastAPI с использованием PostgreSQL в качестве БД

### Как запустить проект:
****
#### ШАГ 0 - Клонировать проект к себе на PC;
```
git clone git@github.com:LeeSinGit/y_lab_menu_project.git
```
#### ШАГ 1 - Зайти в корневую директорию проекта;
```
cd y_lab_menu_project/
```
#### ШАГ 2 - Применить команду;
```
docker-compose -f docker-compose.test.yml up --build
```
****
#### Будут пройдены все тесты pytest;
##### Инструкция по работе с БД, если встанет такая необходимость.
По умолчанию база данных пуста и готова к прохождению тестов.
Удобнее всего зайти в терминал базы данных через Docker Desctop.
Нажать на db_postgres -> Terminal
Затем прописать там команду:
```
psql -U postgres -d menu_db
```
Посмотреть все таблицы:
```
\dt
```
Очистить данные из таблицы Menu:
```
DELETE FROM "Menu";
```
Очистить данные из таблицы Submenu:
```
DELETE FROM "Submenu";
```
Очистить данные из таблицы Dish:
```
DELETE FROM "Dish";
```
****
### *Над проектом работал Лисин Семён :heart:*
### *Код написан на языке Python :v:*
