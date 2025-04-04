import requests

ACCESS_TOKEN = "put api here"  # Получить можно в Pinterest Developer Portal


def get_boards(access_token):
    url = "https://api.pinterest.com/v5/boards"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"fields": "id,name,url"}
    response = requests.get(url, headers=headers, params=params)
    return response.json().get("items", [])

boards = get_boards(ACCESS_TOKEN)
print("Список досок в аккаунте")
for board in boards:
    print(f"Owner{board['owner']}, Name: {board['name']}, ID: {board['id']}")
input("Нажми любую клавишу, чтобы выйти")