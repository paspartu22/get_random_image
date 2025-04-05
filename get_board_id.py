import json
import requests

# Путь к файлу tokens.json
TOKENS_FILE = "tokens.json"

def load_user_token(user_id):
    """
    Загружает токен пользователя из tokens.json
    """
    try:
        with open(TOKENS_FILE, "r") as f:
            tokens = json.load(f)
            user_data = tokens.get(str(user_id))
            if user_data and "access_token" in user_data:
                return user_data["access_token"]
            else:
                print(f"Токен для пользователя {user_id} не найден.")
                return None
    except FileNotFoundError:
        print(f"Файл {TOKENS_FILE} не найден.")
        return None
    except json.JSONDecodeError:
        print(f"Ошибка чтения JSON из файла {TOKENS_FILE}.")
        return None

def get_boards(access_token):
    """
    Получает список всех досок пользователя через Pinterest API с поддержкой пагинации
    """
    url = "https://api.pinterest.com/v5/boards"
    headers = {"Authorization": f"Bearer {access_token}"}
    boards = []
    next_page = None

    while True:
        params = {"page_size": 100}  # Увеличиваем количество элементов на странице
        if next_page:
            params["bookmark"] = next_page  # Добавляем bookmark для перехода на следующую страницу

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # Проверка на ошибки
            data = response.json()
            boards.extend(data.get("items", []))  # Добавляем доски из текущей страницы
            next_page = data.get("bookmark")  # Получаем bookmark для следующей страницы

            if not next_page:  # Если нет следующей страницы, выходим из цикла
                break
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе досок: {e}")
            break

    return boards

# ID пользователя из tokens.json
USER_ID = 348404614

# Загружаем токен пользователя
access_token = load_user_token(USER_ID)

if access_token:
    # Получаем список досок
    boards = get_boards(access_token)
    print(f"Доступные доски ({len(boards)}):")
    for board in boards:
        # Проверяем наличие ключа 'url'
        board_url = board.get('url', 'URL отсутствует')
        print(f"Название: {board['name']}, ID: {board['id']}, URL: {board_url}")
else:
    print("Не удалось загрузить токен пользователя.")

