
# Uni Timetable Tracker Bot for VK

*A.K.A. Redemption Bot*

Бот для ВК, который присылает напоминания о предстоящих парах.

### Contents

* Functionality
* Usage
* Trivia
* TODO

### Functionality

* Присылает напоминания в чат/лс за несколько минут (по умолчанию 5) до начала пары, содержащие название пары, место, имя преподавателя и т.п.
* После её окончания удаляет напоминание чтобы не захламлять чат.
* Вечером в указанное время (по умолчанию 21:00) присылает расписание на следующий день.

### Usage

1. Склонируйте репозиторий, установите зависимости poetry:

    ```
    git clone https://github.com/Lainina/uni_VK_timetable_tracker
   
    cd uni_VK_timetable_tracker

    pip install poetry

    poetry install
    ```
 
2. Создайте ключ управления сообществом в ВК, подключите Long Poll API, включите возможности для ботов:

    - Ваше сообщество - Управление - Настройки - Работа с API - Ключи доступа - Создать ключ доступа (Отметьте "управление сообществом", "сообщения сообщества")
    - Long Poll API - Включено
    - Типы событий (Отметьте "Входящее сообщение")
    - Сообщения - Сообщения сообщества (включены)
    - Настройки для бота - Возможности ботов (включены), отметьте "Разрешать добавлять сообщество в чаты"

3. Добавьте бота в чат 

    Главная сообщества - Добавить в чат

4. Откройте config_example.py и вставьте свои настройки:
    - VK_TOKEN - ключ доступа который вы создали
    - API_VERSION - версия API которая стоит у вас в Long Poll API (по умолчанию 5.131)
    - Различные CHAT_ID: CHAT_ID - основной ваш чат, TEST_CHAT_ID_1 - для дебага, можете ввести тот же
      (CHAT_ID строятся по типу: 2000000000 + (номер чата в порядке добавления в них бота), т.е. первый чат в который вы добавите сообщество будет иметь CHAT_ID 2000000001)  
    - Другие настройки по вкусу, переменные сами за себя говорят
    - После всех настроек поменяйте название файла на config.py

5. В src\database\timetable_example.json введите своё расписание по шаблону, после чего переименуйте файл в timetable.json

6. Запустите main.py


### Trivia

Что это за проект то вообще такой?

Если коротко, то:

Год назад я написала бота с аналогичным функционалом для своей группы в университете.

Он был написан крайне плохо.

Этот проект стал моей попыткой переписать того бота с нуля, по дороге пытаясь достичь нескольких целей:

- Научиться использовать основы ООП
- Научиться использовать GitHub в качестве VCS
- Начать писать код понемногу каждый день (#100DaysOfCode?..)

Основная цель была, возможно, не написать этот проект прямо *хорошо* (на моём уровне мне ещё достаточно сложно это сделать) главное — написать *лучше*.

В целом, я считаю что с задачами +- справилась, хотя и не реализовала весь функционал, который планировала. 

Этого бота дописала как раз к началу учебного года, запустила на стареньком ноутбуке, ставшем домашним сервером, и теперь он стабильно (ну почти) работает в чатике ВК моей группы.

### TODO

- Добавить обработку входящих сообщений, отвечать на запросы расписания на конкретные дни
- Добавить возможность добавлять пары с помощью личных сообщений боту
- Переработать логи в структурированную папку
