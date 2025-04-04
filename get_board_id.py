import requests

ACCESS_TOKEN = "put_token_here"  # Получить можно в Pinterest Developer Portal

def get_boards(access_token):
    url = "https://api.pinterest.com/v5/boards"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"fields": "id,name,url"}
    response = requests.get(url, headers=headers, params=params)
    return response.json().get("items", [])

# boards = get_boards(ACCESS_TOKEN)
# print("Список досок в аккаунте")
# for board in boards:
#     print(f"Owner{board['owner']}, Name: {board['name']}, ID: {board['id']}")
# input("Нажми любую клавишу, чтобы выйти")


def get_all_boards(access_token):
    """
    Получает все доски: как созданные вами, так и те, куда вас добавили
    """
    url = "https://api.pinterest.com/v5/boards"  # Ключевое изменение!
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "fields": "id,name,url,owner",  # Добавляем owner для проверки владельца
        "page_size": 100,  # Максимальное количество досок за один запрос
        "privacy": "ALL"  # Получаем только shared доски
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Проверка ошибок
        return response.json().get("items", [])
    except Exception as e:
        print(f"Ошибка при запросе досок: {e}")
        return []

boards = get_all_boards(ACCESS_TOKEN)
print("Все доски (включая shared):")
for board in boards:
    owner = board.get("owner", {}).get("username", "unknown")
    print(f"Владелец: @{owner}, Название: {board['name']}, ID: {board['id']}")

input("Нажмите Enter для выхода...")