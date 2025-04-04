Как пользоваться этой штукой

1. Установить Python
    1. Открыть Microsoft store
    2. Ввести в поиске Python
    3. Установить Python 3.12 
  
2. Скачать репозиторий 
    1. Для этого нужно нажать на зеленую кнопку справа сверху `<> Code` и выбрать download Zip
    2. Скачать архив, распаковать

3. Настроить приложение 
    1. Устанавливаем библиотеки. Для этого кликаешь по requirements.py. Он скорее всего спросит с помощью чего его открыть, там должен быть Python 3.12. Можно кликнуть его, а можно указать ему так, чтобы он запомнил. Для этого
        1. Указываем как открывать .py файлы. Для этого кликаем по файлу правой кнопкой -> Open with/Открыть с помощью -> Choose another app/Выбрать другое -> Выбираем Python и кликаем галочку Always use.../Всегда использовать...
    2. Добавляешь ключ API. Для этого открываешь файлы main.py и get_boards_id.py блокнотом и вставляешь в `ACCESS_TOKEN = "put key here"  # Ключ API` ключ, который я дал. Получится `ACCESS_TOKEN = "pina_AM..."`
    3. Готовишь список id досок. Для этого запускаешь get_board_id.py, он выдает id всех досок в аккаунте. Выбираешь из них все id, которые тебе хочетсся и добавляешь их в список main.py BOARDS_ARRAY через запятую как в примере
    4. Настраиваешь повторы. Для этого ставишь `NO_REPEATS = True `или` NO_REPEATS = False`

4. Запускаешь main.py 