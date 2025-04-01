import requests
import random
import webbrowser
from datetime import datetime

    # Замените эти значения на свои    
ACCESS_TOKEN = "ваш_access_token"  # Получить можно в Pinterest Developer Portal
BOARD_ID = "andrewovodov/my-saves/"  # Например: "user1234/my-board"

def get_random_pin_from_board(access_token, board_id):
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
            
        random_pin = random.choice(pins)
        return random_pin
        
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к API Pinterest: {e}")
        return None

def main():

    
    print("Подключаемся к Pinterest...")
    random_pin = get_random_pin_from_board(ACCESS_TOKEN, BOARD_ID)
    
    if random_pin:
        print("\nСлучайная картинка из вашей папки:")
        print(f"Описание: {random_pin.get('note', 'Без описания')}")
        print(f"Дата создания: {random_pin.get('created_at', 'Неизвестно')}")
        
        # Получаем URL изображения
        image_url = None
        if 'media' in random_pin:
            media = random_pin['media']
            if 'images' in media and 'orig' in media['images']:
                image_url = media['images']['orig']['url']
        
        if image_url:
            print(f"URL изображения: {image_url}")
            # Открываем изображение в браузере
            webbrowser.open(image_url)
        else:
            print("Не удалось получить URL изображения.")
    else:
        print("Не удалось получить случайный пин.")

if __name__ == "__main__":
    main()