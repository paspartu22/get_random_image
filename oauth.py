import json
import os
from flask import Flask, request, redirect
import requests
import base64

app = Flask(__name__)

from dotenv import load_dotenv
load_dotenv()

# Настройки
CLIENT_ID = os.getenv('PINTEREST_CLIENT_ID')
REDIRECT_URI = os.getenv('PINTEREST_REDIRECT_URI')
CLIENT_SECRET = os.getenv('PINTEREST_CLIENT_SECRET')
MY_ADDRESS = os.getenv('MY_ADDRESS')

# Получаем путь текущей директории скрипта
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(CURRENT_DIR, 'tokens.json')

# Функция сохранения токенов
def save_token(user_id, access_token, refresh_token, expires_in):
    # Загружаем текущие данные (если файл есть)
    tokens = {}
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            tokens = json.load(f)

    # Обновляем или добавляем нового пользователя
    tokens[user_id] = {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expires_in': expires_in
    }
    
    # Сохраняем в файл
    with open(TOKEN_FILE, 'w') as f:
        json.dump(tokens, f, indent=4)






@app.route('/auth/pinterest/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return 'Ошибка: нет code'


    # Кодируем client_id:client_secret в base64
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}".encode('utf-8')
    b64_auth_str = base64.b64encode(auth_str).decode('utf-8')

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {b64_auth_str}'  # Добавляем Basic Auth
    }

    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI  # Убедитесь что URI совпадает с настройками приложения
    }
    
    # Обмен кода на access_token
    token_url = 'https://api.pinterest.com/v5/oauth/token'
    # headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    # data = {
    #     'grant_type': 'authorization_code',
    #     'code': code,
    #     'client_id': CLIENT_ID,
    #     'client_secret': CLIENT_SECRET,
    #     'redirect_uri': REDIRECT_URI
    # }

    r = requests.post(token_url, data=data, headers=headers)
    print(r)
    token_response = r.json()
    telegram_user_id = request.args.get('state')
    # Декодируем state из base64
    if telegram_user_id:
        try:
            decoded_state = base64.urlsafe_b64decode(telegram_user_id).decode()
            telegram_user_id = decoded_state.split(':')[0]  # Извлекаем user_id
        except Exception as e:
            print(f"Ошибка декодирования state: {e}")
            telegram_user_id = None
            
    if 'access_token' in token_response and telegram_user_id:
        access_token = token_response['access_token']
        refresh_token = token_response.get('refresh_token', '')
        expires_in = token_response.get('expires_in', 3600)

        # Сохраняем токен в файл (используем user_id = 'default' как пример)
        save_token(telegram_user_id, access_token, refresh_token, expires_in)

        print('Токен успешно получен:', token_response)
        return f'Успешная авторизация! Токен сохранён.<br>'
    else:
        print('Ошибка получения токена:', token_response)
        return f'Ошибка получения токена: {token_response}'


def start_oauth_server():
    app.run(host = MY_ADDRESS, port = 5001)

if __name__ == '__main__':
    app.run(host = MY_ADDRESS, port = 5001)