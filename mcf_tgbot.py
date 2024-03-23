from telegram import Update
from telegram import ReplyKeyboardMarkup, KeyboardButton
from functools import wraps
from telegram.ext import Application, CommandHandler, CallbackContext, StringRegexHandler, MessageHandler, filters
from arambot_lib.bot_reload import (
    close_mcf_and_chrome,
    start_mcf,
    status_mcf
)
import json
import os
import logging
import redis
from mcf_data import MIRROR_PAGE
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

with open('./untracking/authorized_users', 'r') as us:
    authorized_users = [i[:-1] for i in us.readlines()]

snip = {
    "time": 0,

    "blue_kills": 0,
    "red_kills": 0,

    "blue_towers": 0,
    "red_towers": 0,

    "blue_t1_hp": 0,
    "red_t1_hp": 0,

    "blue_gold": 0,
    "red_gold": 0,

    "is_active": 0
}

# Установка значения
for key, value in snip.items():
    r.set(key, value)

print(r.get('is_active'))

def auth(authorized_users):
    def decorator(func):
        @wraps(func)
        async def wrapper(update: Update, context: CallbackContext):
            user_id = update.message.from_user.id
            # print(user_id)
            # print(authorized_users)
            if str(user_id) in authorized_users:
                return await func(update, context)
            else:
                await update.message.reply_text("🚫 Unauthorized")
        return wrapper
    return decorator

async def first_auth(update: Update, context: CallbackContext):
    us_id = str(update.message.from_user.id)
    
    if us_id in authorized_users:
        await update.message.reply_text('✅ Вы уже авторизовались')
    else:
        authorized_users.append(us_id)

        with open('./untracking/authorized_users', 'w+') as us:
            for i in authorized_users:
                us.writelines(i + '\n')

        await update.message.reply_text('✅ Авторизация успешна')

@auth(authorized_users=authorized_users)
async def info(update: Update, context: CallbackContext):

    visitor = update.message.chat.first_name
    print(update.message.from_user.id)
    await update.message.reply_text(f'Да, здесь будет инфа. Нужно немного подождать, {visitor}')

@auth(authorized_users=authorized_users)
async def start(update: Update, context: CallbackContext):

    keyboard = [ [KeyboardButton('/game'), KeyboardButton('/build')], [KeyboardButton('/predicts_global'), KeyboardButton('/predicts_daily')] ]

    if update.message.from_user.id == 577810613:
        keyboard.append([KeyboardButton('/mcf_status')])

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    visitor = update.message.chat.first_name

    await update.message.reply_text(f'Привет, {visitor}. Для краткого ознакомления с ботом нажми /info', reply_markup=reply_markup)

@auth(authorized_users=authorized_users)
async def emul(update: Update, context: CallbackContext):
    
    r.set('emulation', '0')

    await update.message.reply_text('Emulation stoped')

@auth(authorized_users=authorized_users)
async def devkit(update: Update, context: CallbackContext):
    keyboard = [ [KeyboardButton('/game'), KeyboardButton('/build')], [KeyboardButton('/predicts_result')],
                [KeyboardButton('/mcf_reload'), KeyboardButton('/mcf_stop'), KeyboardButton('/mcf_status')] ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text('Dev mode', reply_markup=reply_markup)

@auth(authorized_users=authorized_users)
async def actual_mirror(update: Update, context: CallbackContext):
    with open(MIRROR_PAGE, 'r') as ex_url:
        await update.message.reply_text(f'Актуальное зеркало: {ex_url.read()}')

@auth(authorized_users=authorized_users)
async def change_actual_mirror(update: Update, context: CallbackContext):
    # logger.info('here')
    # league_route = '/live/cyber-zone/league-of-legends'
    league_alt_rout = '/ru/live/cyber-zone/league-of-legends'
    message = update.message.text

    if not message.startswith('https://1xlite-') and not message.startswith('https://melb'):
        await update.message.reply_text(f'Неверная ссылка для зеркала')
    else:
        link_parts = message.split('/')
        new_link = '/'.join(link_parts[0:3]) + league_alt_rout
        with open('./untracking/mirror_page.txt', 'w+') as ex_url:
            ex_url.write(new_link)

        await update.message.reply_text(f'Зеркало добавлено: {new_link}')

@auth(authorized_users=authorized_users)
async def echo_score(update: Update, context: CallbackContext) -> None:
    

    if r.get('is_active') != '0':
        
        with open(os.path.join('.', 'arambot_lib', 'score_answer_sample.txt'), 'r', encoding='utf-8') as sample:
            message_sample = sample.read()

        # 🐳 Киллы: {blue_kills} | Башни: {blue_towers}
        # 🐙 Киллы: {red_kills} | Башни: {red_towers}
        timestamp = divmod(int(r.get('time')), 60)
        minutes = timestamp[0] if timestamp[0] > 9 else f"0{timestamp[0]}"
        seconds = timestamp[1] if timestamp[1] > 9 else f"0{timestamp[1]}"
        message_for_reply = message_sample.format(
            blue_kills = r.get('blue_kills'),
            blue_towers = r.get('blue_towers'),
            red_kills = r.get('red_kills'),
            red_towers = r.get('red_towers'),
            blue_gold = r.get('blue_gold'),
            red_gold = r.get('red_gold'),
            blue_t1_hp = r.get('blue_t1_hp'),
            red_t1_hp = r.get('red_t1_hp'),
            time = ':'.join([str(minutes), str(seconds)]),
        )
        await update.message.reply_text(message_for_reply)
    else:
        await update.message.reply_text('Нет активной игры')

@auth(authorized_users=authorized_users)
async def echo_build(update: Update, context: CallbackContext) -> None:
    
    try:
        with open(os.path.join('images_lib', 'buildcrop.png'), 'rb') as photo_file:
            await update.message.reply_photo(photo=photo_file)
    except:
        await update.message.reply_text('Нет активной игры')

@auth(authorized_users=authorized_users)
async def mcf_reload(update: Update, context: CallbackContext) -> None:
    
    close_mcf_and_chrome()
    start_mcf()

    await update.message.reply_text('Бот перезагружен')

@auth(authorized_users=authorized_users)
async def mcf_stop(update: Update, context: CallbackContext) -> None:
    
    close_mcf_and_chrome()
    # start_mcf()

    await update.message.reply_text('Бот остановлен')

@auth(authorized_users=authorized_users)
async def mcf_status(update: Update, context: CallbackContext) -> None:
    
    status_path = status_mcf()

    with open(status_path, 'rb') as photo_file:
        await update.message.reply_photo(photo=photo_file)

@auth(authorized_users=authorized_users)
async def predicts_check(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""

    with open(os.path.join('.', 'arambot_lib', 'predicts_answer_sample.txt'), 'r', encoding='utf-8') as file:
        predicts_answer_message = file.read()

    if update.message.text == '/predicts_global':
        top_message = 'Результат по предиктам за все время'
        predicts_path = os.path.join('.', 'untracking', 'predicts_trace.json')
    else:
        top_message = 'Результат по предиктам за сутки'
        predicts_path = os.path.join('.', 'untracking', 'predicts_trace_daily.json')

    with open(predicts_path, 'r', encoding='utf-8') as js_stats:
        predicts: dict = json.load(js_stats)
        itms = list(predicts.items())

        ordered_plus = [value[1][0] for value in itms]
        ordered_minus = [value[1][1] for value in itms]

        message = predicts_answer_message.format(*ordered_plus, *ordered_minus, top_message=top_message)

    await update.message.reply_text(message)
       
def main() -> None:
    """Start the bot."""
    application = Application.builder().token(os.getenv('BOT_TOKEN')).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("gabe_pidoras", first_auth))
    application.add_handler(CommandHandler("game", echo_score))
    # application.add_handler(CommandHandler("build", echo_build))
    application.add_handler(CommandHandler("predicts_global", predicts_check))
    application.add_handler(CommandHandler("predicts_daily", predicts_check))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'https\S+'), change_actual_mirror))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'https\S+'), change_actual_mirror))
    application.add_handler(CommandHandler('info', info))
    application.add_handler(CommandHandler('mirror', actual_mirror))


    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'\bfallside\b'), devkit))
    application.add_handler(CommandHandler('mcf_reload', mcf_reload))
    application.add_handler(CommandHandler('mcf_stop', mcf_stop))
    application.add_handler(CommandHandler('emul_stop', emul))
    application.add_handler(CommandHandler('mcf_status', mcf_status))
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()