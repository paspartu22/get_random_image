import requests
import random
import webbrowser
from datetime import datetime

    # Замените эти значения на свои    
ACCESS_TOKEN = "put token here"  # Получить можно в Pinterest Developer Portal
MY_BOARD_ID = "636766903503568067"  # это моя маленькая борда на 3 случайных картинки
BOARDS_ARRAY = ["636766903503568067"] #


def get_boards(access_token):
    url = "https://api.pinterest.com/v5/boards"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"fields": "id,name,url"}
    response = requests.get(url, headers=headers, params=params)
    return response.json().get("items", [])



def get_pins_from_boards(access_token, boards_id):
    pins_array = []
    for board_id in boards_id:
        """
        Получает случайный пин из указанной доски Pinterest
        """
        url = f"https://api.pinterest.com/v5/boards/{board_id}/pins"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        params = {
            "fields": "id,link,url,media,note"
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            pins = response.json().get('items', [])
            
            if not pins:
                print("В этой папке нет пинов.")
                return None
            for pin in pins:
                pins_array.append(pin)    
            
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к API Pinterest: {e}")
            return None
    return pins_array

def main():
    # boards = get_boards(ACCESS_TOKEN)
    # for board in boards:
    #     print(f"ID: {board['id']}, Name: {board['name']}")
    
    print("Подключаемся к Pinterest...")
    pins_array = get_pins_from_boards(ACCESS_TOKEN, BOARDS_ARRAY)
    
    if pins_array:
        while(1):
            random_pin = random.choice(pins_array)
            print("\nСлучайная картинка из вашей папки:")
            print(f"Описание: {random_pin.get('note', 'Без описания')}")
            print(f"Дата создания: {random_pin.get('created_at', 'Неизвестно')}")
            
            # Получаем URL изображения
            image_url = None
            if 'media' in random_pin:
                media = random_pin['media']
                if 'images' in media and '1200x' in media['images']:
                    image_url = media['images']['1200x']['url']
            
            if image_url:
                print(f"URL изображения: {image_url}")
                # Открываем изображение в браузере
                webbrowser.open(image_url)
            else:
                print("Не удалось получить URL изображения.")
            if (input("Нажми q чтобы выйти, любую другую клавишу, чтобы открыть еще одну картинку \n") == 'q'):
                break

    else:
        input("Не удалось получить случайный пин. Нажмите любую клавишу, чтобы выйти")

if __name__ == "__main__":
    main()