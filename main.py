import requests
import random
import webbrowser

# Настройки
ACCESS_TOKEN = "put key here"  # Ключ API
MY_BOARD_ID = "636766903503568067"  # это моя маленькая борда на 3 случайных картинки

# Это список досок, из которых он будет забирать пины, ID можно получить запустив get_board_id.py
BOARDS_ARRAY = [588071732533373497] #

# = True если хочешь, чтобы пины не повторялись, = False, если пины могут повторяться
NO_REPEATS = True 
# NO_REPEATS = False


##########################

def get_pins_from_boards(access_token, boards_id):
    pins_array = []
    for board_id in boards_id:
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
    print("Подключаемся к Pinterest...")
    pins_array = get_pins_from_boards(ACCESS_TOKEN, BOARDS_ARRAY)
    
    if pins_array:
        while(1):
            random_pin = random.choice(pins_array)
            if NO_REPEATS:
                pins_array.remove(random_pin)
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
            if (not pins_array):
                print("Все пины закончились")
                break

    else:
        input("Не удалось получить случайный пин. Нажмите любую клавишу, чтобы выйти")

if __name__ == "__main__":
    main()