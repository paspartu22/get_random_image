import logging
import telegram  # Импортируем весь модуль telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
import os
import uuid
from base64 import urlsafe_b64encode
import json
import requests
import random
import asyncio
from oauth import start_oauth_server

from dotenv import load_dotenv
load_dotenv()

# Настройки
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
PINTEREST_CLIENT_ID = os.getenv('PINTEREST_CLIENT_ID')
REDIRECT_URI = os.getenv('PINTEREST_REDIRECT_URI')
SCOPES = ['boards:read', 'pins:read', 'user_accounts:read']

# Настройка логов
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Функция для загрузки токена из tokens.json
def load_token(user_id):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    token_file = os.path.join(current_dir, 'tokens.json')
    
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            tokens = json.load(f)
            return tokens.get(str(user_id))  # Приводим user_id к строке
    return None

# Функция для сохранения выбранных досок в tokens.json
def save_selected_boards(user_id, selected_boards):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    token_file = os.path.join(current_dir, 'tokens.json')
    
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            tokens = json.load(f)
    else:
        tokens = {}
    
    # Сохраняем выбранные доски для пользователя
    if str(user_id) in tokens:
        tokens[str(user_id)]['selected_boards'] = selected_boards
    else:
        tokens[str(user_id)] = {'selected_boards': selected_boards}
    
    with open(token_file, 'w') as f:
        json.dump(tokens, f, indent=4)

# Функция для сохранения досок и пинов
def save_selected_boards_and_pins(user_id, selected_boards, all_pins):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    token_file = os.path.join(current_dir, 'tokens.json')
    
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            tokens = json.load(f)
    else:
        tokens = {}
    
    # Сохраняем выбранные доски и пины для пользователя
    if str(user_id) in tokens:
        tokens[str(user_id)]['selected_boards'] = selected_boards
        tokens[str(user_id)]['pins'] = all_pins
    else:
        tokens[str(user_id)] = {
            'selected_boards': selected_boards,
            'pins': all_pins
        }
    
    with open(token_file, 'w') as f:
        json.dump(tokens, f, indent=4)

# Функция для получения списка досок пользователя
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
            logger.error(f"Ошибка при запросе досок: {e}")
            break

    return boards

# Функция для получения пинов из доски
def get_pins_from_board(access_token, board_id):
    url = f"https://api.pinterest.com/v5/boards/{board_id}/pins"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return [pin['id'] for pin in response.json().get('items', [])]
    else:
        logger.error(f"Ошибка при получении пинов для доски {board_id}: {response.status_code} - {response.text}")
        return []

# Функция для получения случайного пина
def get_random_pin(user_id):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    token_file = os.path.join(current_dir, 'tokens.json')
    
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            tokens = json.load(f)
            user_data = tokens.get(str(user_id))
            if user_data and 'pins' in user_data:
                return random.choice(user_data['pins'])  # Выбираем случайный пин
    return None

# Функция для получения данных пина, включая URL изображения и заголовок
def get_pin_details(access_token, pin_id):
    url = f"https://api.pinterest.com/v5/pins/{pin_id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        return {
            "image_url": data.get('media', {}).get('images', {}).get('1200x', {}).get('url'),
            "title": data.get('title', 'Без названия')  # Если заголовок отсутствует, используем "Без названия"
        }
    else:
        logger.error(f"Ошибка при получении данных пина {pin_id}: {response.status_code} - {response.text}")
        return None

# Функция для проверки, зарегистрирован ли пользователь
def is_user_registered(user_id):
    token_data = load_token(user_id)
    return token_data is not None

# Функция для создания кнопок
def create_buttons(user_id):
    if is_user_registered(user_id):
        # Загружаем данные пользователя
        token_data = load_token(user_id)
        has_pins = token_data and 'pins' in token_data and len(token_data['pins']) > 0
        
        # Формируем кнопки
        keyboard = [[InlineKeyboardButton("Настроить список досок", callback_data='set_boards')]]
        
        if has_pins:
            keyboard.append([InlineKeyboardButton("Следующая картинка", callback_data='next_image')])
    else:
        keyboard = [[InlineKeyboardButton("Register with Pinterest", callback_data='register')]]
    
    return InlineKeyboardMarkup(keyboard)

# Обработчик для выбора досок
async def select_boards_handler(update, context):
    query = update.callback_query
    await query.answer()
    
    telegram_user_id = update.effective_user.id
    selected_board_id = query.data.split(':')[1]  # Получаем ID выбранной доски
    
    # Сохраняем выбранные доски в контексте
    if 'selected_boards' not in context.user_data:
        context.user_data['selected_boards'] = []
    
    if selected_board_id in context.user_data['selected_boards']:
        # Если доска уже выбрана, снимаем выбор
        context.user_data['selected_boards'].remove(selected_board_id)
    else:
        # Если доска не выбрана, добавляем её
        context.user_data['selected_boards'].append(selected_board_id)
    
    # Загружаем токен пользователя
    token_data = load_token(telegram_user_id)
    if not token_data:
        await query.edit_message_text(
            "Токен не найден. Пожалуйста, зарегистрируйтесь через Pinterest.",
            reply_markup=create_buttons(telegram_user_id)
        )
        return
    
    access_token = token_data.get('access_token')
    if not access_token:
        await query.edit_message_text(
            "Токен недействителен. Пожалуйста, зарегистрируйтесь заново.",
            reply_markup=create_buttons(telegram_user_id)
        )
        return
    
    # Получаем список досок
    boards = get_boards(access_token)
    if boards is None:
        await query.edit_message_text(
            "Не удалось получить список досок. Проверьте токен или повторите попытку позже.",
            reply_markup=create_buttons(telegram_user_id)
        )
        return
    
    # Формируем кнопки для выбора досок
    keyboard = [
        [InlineKeyboardButton(
            f"{board['name']} {'✅' if board['id'] in context.user_data['selected_boards'] else ''}",
            callback_data=f"select_board:{board['id']}"
        )]
        for board in boards
    ]
    keyboard.append([InlineKeyboardButton("Завершить выбор", callback_data="finish_selection")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Обновляем сообщение с кнопками
    await query.edit_message_text(
        "Выберите доски (выбранные отмечены галочкой):",
        reply_markup=reply_markup
    )

# Обновленный обработчик завершения выбора досок
async def finish_selection_handler(update, context):
    query = update.callback_query
    await query.answer()
    
    telegram_user_id = update.effective_user.id
    selected_boards = context.user_data.get('selected_boards', [])
    
    # Загружаем токен пользователя
    token_data = load_token(telegram_user_id)
    if not token_data:
        await query.edit_message_text(
            "Токен не найден. Пожалуйста, зарегистрируйтесь через Pinterest.",
            reply_markup=create_buttons(telegram_user_id)
        )
        return
    
    access_token = token_data.get('access_token')
    if not access_token:
        await query.edit_message_text(
            "Токен недействителен. Пожалуйста, зарегистрируйтесь заново.",
            reply_markup=create_buttons(telegram_user_id)
        )
        return
    
    # Получаем список досок
    boards = get_boards(access_token)
    if boards is None:
        await query.edit_message_text(
            "Не удалось получить список досок. Проверьте токен или повторите попытку позже.",
            reply_markup=create_buttons(telegram_user_id)
        )
        return
    
    # Сопоставляем ID выбранных досок с их именами
    selected_board_names = [
        board['name'] for board in boards if board['id'] in selected_boards
    ]
    
    # Собираем все пины из выбранных досок в единый массив
    all_pins = []
    for board_id in selected_boards:
        pins = get_pins_from_board(access_token, board_id)
        all_pins.extend(pins)
    
    # Сохраняем выбранные доски и их пины в tokens.json
    save_selected_boards_and_pins(telegram_user_id, selected_boards, all_pins)
    
    # Формируем сообщение с именами выбранных досок
    board_names_message = "\n".join(selected_board_names)
    await query.edit_message_text(
        f"Выбор завершён. Выбранные доски:\n{board_names_message}",
        reply_markup=create_buttons(telegram_user_id)
    )

# Обновленный обработчик для кнопки Set Boards
async def set_boards_handler(update, context):
    query = update.callback_query
    await query.answer()
    
    telegram_user_id = update.effective_user.id  # Получаем Telegram user_id
    
    # Загружаем токен пользователя
    token_data = load_token(telegram_user_id)
    if not token_data:
        await query.edit_message_text(
            "Токен не найден. Пожалуйста, зарегистрируйтесь через Pinterest.",
            reply_markup=create_buttons(telegram_user_id)
        )
        return
    
    access_token = token_data.get('access_token')
    if not access_token:
        await query.edit_message_text(
            "Токен недействителен. Пожалуйста, зарегистрируйтесь заново.",
            reply_markup=create_buttons(telegram_user_id)
        )
        return
    
    # Получаем список досок
    boards = get_boards(access_token)
    if boards is None:
        await query.edit_message_text(
            "Не удалось получить список досок. Проверьте токен или повторите попытку позже.",
            reply_markup=create_buttons(telegram_user_id)
        )
        return
    
    # Загружаем выбранные доски из tokens.json
    selected_boards = token_data.get('selected_boards', [])
    context.user_data['selected_boards'] = selected_boards  # Сохраняем выбранные доски в контексте
    
    # Формируем кнопки для выбора досок
    keyboard = [
        [InlineKeyboardButton(
            f"{board['name']} {'✅' if board['id'] in selected_boards else ''}",
            callback_data=f"select_board:{board['id']}"
        )]
        for board in boards
    ]
    keyboard.append([InlineKeyboardButton("Завершить выбор", callback_data="finish_selection")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Проверяем, можно ли отредактировать сообщение
    try:
        await query.edit_message_text("Выберите доски (выбранные отмечены галочкой):", reply_markup=reply_markup)
    except telegram.error.BadRequest as e:
        if "message to edit" in str(e):
            # Если сообщение нельзя отредактировать, отправляем новое сообщение
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Выберите доски (выбранные отмечены галочкой):",
                reply_markup=reply_markup
            )

# Обновление обработчиков для использования кнопок
async def next_image_handler(update, context):
    query = update.callback_query
    await query.answer()  # Подтверждаем обработку запроса

    telegram_user_id = update.effective_user.id
    
    # Проверяем, зарегистрирован ли пользователь
    if not is_user_registered(telegram_user_id):
        await query.edit_message_text(
            "Вы не зарегистрированы. Пожалуйста, зарегистрируйтесь через Pinterest.",
            reply_markup=create_buttons(telegram_user_id)
        )
        return
    
    # Загружаем токен пользователя
    token_data = load_token(telegram_user_id)
    access_token = token_data.get('access_token')
    if not access_token:
        await query.edit_message_text(
            "Токен недействителен. Пожалуйста, зарегистрируйтесь заново.",
            reply_markup=create_buttons(telegram_user_id)
        )
        return
    
    # Получаем случайный пин
    random_pin = get_random_pin(telegram_user_id)
    if not random_pin:
        await query.edit_message_text(
            "Не удалось найти пины. Убедитесь, что вы выбрали доски.",
            reply_markup=create_buttons(telegram_user_id)
        )
        return
    
    # Получаем данные пина (URL изображения и заголовок)
    pin_details = get_pin_details(access_token, random_pin)
    if not pin_details or not pin_details.get("image_url"):
        await query.edit_message_text(
            "Не удалось загрузить изображение. Попробуйте снова.",
            reply_markup=create_buttons(telegram_user_id)
        )
        return
    
    # Отправляем изображение как фото
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=pin_details["image_url"],
        caption=f"Заголовок: {pin_details['title']}\nСсылка: https://www.pinterest.com/pin/{random_pin}/",
        reply_markup=create_buttons(telegram_user_id)
    )

async def start(update, context):
    telegram_user_id = update.effective_user.id
    reply_markup = create_buttons(telegram_user_id)
    await update.message.reply_text(
        'Добро пожаловать! Выберите действие:',
        reply_markup=reply_markup
    )

async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'register':
        # Получаем Telegram user_id
        telegram_user_id = update.effective_user.id
        
        # Генерируем URL с привязкой к пользователю
        auth_url, state = generate_auth_url(telegram_user_id)
        
        # Сохраняем state в контекст (для последующей проверки)
        context.user_data['oauth_state'] = state
        
        await query.edit_message_text(
            text=f"Нажмите на ссылку, чтобы авторизоваться:\n{auth_url}",
            disable_web_page_preview=True
        )
        
        # После отправки ссылки добавляем кнопку "Настроить список досок"
        keyboard = [
            [InlineKeyboardButton("Настроить список досок", callback_data='set_boards')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="После завершения регистрации нажмите на кнопку ниже, чтобы настроить список досок:",
            reply_markup=reply_markup
        )

def generate_auth_url(telegram_user_id):
    # Кодируем user_id в base64 для безопасной передачи в URL
    state_data = {
        "uid": telegram_user_id,
        "nonce": str(uuid.uuid4())  # Защита от повторов
    }
    
    # Преобразуем в строку и кодируем
    state_str = f"{state_data['uid']}:{state_data['nonce']}"
    state = urlsafe_b64encode(state_str.encode()).decode()
    
    base_url = "https://www.pinterest.com/oauth/"
    params = {
        "client_id": PINTEREST_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": ",".join(SCOPES),
        "state": state  # Передаем закодированный user_id
    }
    return f"{base_url}?{'&'.join(f'{k}={v}' for k,v in params.items())}", state

def run_bot():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_handler, pattern='^register$'))
    application.add_handler(CallbackQueryHandler(set_boards_handler, pattern='^set_boards$'))
    application.add_handler(CallbackQueryHandler(select_boards_handler, pattern='^select_board:'))
    application.add_handler(CallbackQueryHandler(finish_selection_handler, pattern='^finish_selection$'))
    application.add_handler(CallbackQueryHandler(next_image_handler, pattern='^next_image$'))  # Новый обработчик

    # Start the bot and keep it running
    application.run_polling()  # Use run_polling to keep the bot running

def main():
    run_bot()
    
    # # Run the bot as a background task
    # loop = asyncio.get_event_loop()
    # loop.create_task(run_bot())
    # # Other tasks can be added here if needed
    # loop.run_forever()

if __name__ == '__main__':
    main()