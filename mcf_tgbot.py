from telegram import Update
from telegram import ReplyKeyboardMarkup, KeyboardButton
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

snip = {
    "time": 0,
    "blue_kills": 0,
    "red_kills": 0,
    "blue_towers": 0,
    "red_towers": 0,
    "blue_gold": 0,
    "red_gold": 0,
    "is_active": 0
}

# Установка значения
for key, value in snip.items():
    r.set(key, value)

print(r.get('is_active'))

async def info(update: Update, context: CallbackContext):

    visitor = update.message.chat.first_name
    await update.message.reply_text(f'Да, здесь будет инфа. Нужно немного подождать, {visitor}')

async def start(update: Update, context: CallbackContext):

    keyboard = [ [KeyboardButton('/game'), KeyboardButton('/build')], [KeyboardButton('/predicts_global'), KeyboardButton('/predicts_daily')] ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    visitor = update.message.chat.first_name

    await update.message.reply_text(f'Привет, {visitor}. Для краткого ознакомления с ботом нажми /info', reply_markup=reply_markup)

async def devkit(update: Update, context: CallbackContext):
    keyboard = [ [KeyboardButton('/game'), KeyboardButton('/build')], [KeyboardButton('/predicts_result')],
                [KeyboardButton('/mcf_reload'), KeyboardButton('/mcf_stop'), KeyboardButton('/mcf_status')] ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text('Dev mode', reply_markup=reply_markup)

async def actual_mirror(update: Update, context: CallbackContext):
    with open(MIRROR_PAGE, 'r') as ex_url:
        await update.message.reply_text(f'Актуальное зеркало: {ex_url.read()}')

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
            time = ':'.join([str(minutes), str(seconds)]),
        )
        await update.message.reply_text(message_for_reply)
    else:
        await update.message.reply_text('Нет активной игры')

async def echo_build(update: Update, context: CallbackContext) -> None:
    
    try:
        with open(os.path.join('images_lib', 'buildcrop.png'), 'rb') as photo_file:
            await update.message.reply_photo(photo=photo_file)
    except:
        await update.message.reply_text('Нет активной игры')

async def mcf_reload(update: Update, context: CallbackContext) -> None:
    
    close_mcf_and_chrome()
    start_mcf()

    await update.message.reply_text('Бот перезагружен')

async def mcf_stop(update: Update, context: CallbackContext) -> None:
    
    close_mcf_and_chrome()
    # start_mcf()

    await update.message.reply_text('Бот остановлен')

async def mcf_status(update: Update, context: CallbackContext) -> None:
    
    status_path = status_mcf()

    with open(status_path, 'rb') as photo_file:
        await update.message.reply_photo(photo=photo_file)

    # await update.message.reply_text('Бот перезагружен')
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
    application.add_handler(CommandHandler("game", echo_score))
    application.add_handler(CommandHandler("build", echo_build))
    application.add_handler(CommandHandler("predicts_global", predicts_check))
    application.add_handler(CommandHandler("predicts_daily", predicts_check))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'https\S+'), change_actual_mirror))
    application.add_handler(CommandHandler('mcf_reload', mcf_reload))
    application.add_handler(CommandHandler('mcf_stop', mcf_stop))
    application.add_handler(CommandHandler('info', info))
    application.add_handler(CommandHandler('mcf_status', mcf_status))
    application.add_handler(CommandHandler('mirror', actual_mirror))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'\bfallside\b'), devkit))
    # application.add_handler(CommandHandler('stats_check', stats_check))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()