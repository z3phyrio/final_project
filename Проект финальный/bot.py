import telebot
from telebot import types
from utils import load_locations, get_menu_keyboard, get_keyboard_from_actions, get_current_location, load_user_data, save_user_data
from config import TOKEN, MENU

bot = telebot.TeleBot(TOKEN)
user_data = {}

try:
    locations = load_locations()
except FileNotFoundError:
    print('Проверьте, что файл существует.')
    raise

bot.set_my_commands([types.BotCommand(command, description) for command, description in MENU.items()])

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.from_user.id, '/start - Начать\n/help - Помощь', reply_markup=get_menu_keyboard())

@bot.message_handler(commands=['start'])
def start_command(message):
    current_location = get_current_location(user_data, str(message.from_user.id))
    send_location_description(message, current_location)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == 'Выйти из игры':
        if str(message.from_user.id) in user_data:
            del user_data[str(message.from_user.id)]
            save_user_data(user_data)
        bot.send_message(message.chat.id, "Конец приключения", reply_markup=types.ReplyKeyboardRemove())
        return

    if str(message.chat.id) not in user_data:
        bot.send_message(message.chat.id, "Пожалуйста, начните анкету с помощью команды /start")
        return

    try:
        current_location = get_current_location(user_data, str(message.from_user.id))
        next_location = locations['locations'][current_location]['actions'][message.text]
        send_location_description(message, next_location)
    except KeyError:
        bot.send_message(message.chat.id, "Пожалуйста, начните анкету с помощью команды /start")

def send_location_description(message, location_key):
    location = locations['locations'][location_key]
    description = location['description']
    actions = location.get('actions', {})
    image = location.get('image')

    if image:
        with open(image, 'rb') as photo:
            bot.send_photo(message.chat.id, photo)
    
    bot.send_message(message.from_user.id, description, reply_markup=get_keyboard_from_actions(actions))
    user_data[str(message.from_user.id)] = {'current_location': location_key}
    save_user_data(user_data)

if __name__ == "__main__":
    bot.polling(none_stop=True)