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
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext):
    keyboard = [ [KeyboardButton('game'), KeyboardButton('build')], [KeyboardButton('stats_result')] ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text('Здарова, тварына', reply_markup=reply_markup)

async def gen_url(update: Update, context: CallbackContext):
    logger.info('here')
    league_route = '/live/cyber-zone/league-of-legends'
    league_alt_rout = '/ru/live/cyber-zone/league-of-legends'
    message = (update.message.text).split('_')[1]

    if not message.startswith('https://1xlite-'):
        await update.message.reply_text(f'Неверная ссылка для зеркала')
    elif message.endswith('ru/') or message.endswith('/ru'):
        new_link = message + league_route
        with open('./mcf_lib/mirror_page.txt', 'w+') as ex_url:
            ex_url.write(new_link)

        await update.message.reply_text(f'Зеркало добавлено: {new_link}')
    elif message.endswith('.top'):
        new_link = message + league_alt_rout
        with open('./mcf_lib/mirror_page.txt', 'w+') as ex_url:
            ex_url.write(new_link)

        await update.message.reply_text(f'Зеркало добавлено: {new_link}')

    # await update.message.reply_text(f'Result: {message}')# {message}'.format(message=message))

async def echo_score(update: Update, context: CallbackContext) -> None:
    
    with open(os.path.join('.', 'arambot_lib', 'activegame_score.json'), 'r') as file:
        score_data = json.load(file)

    if score_data['is_active']:
        with open(os.path.join('.', 'arambot_lib', 'score_answer_sample.txt'), 'r', encoding='utf-8') as sample:
            message_sample = sample.read()

        # 🐳 Киллы: {blue_kills} | Башни: {blue_towers}
        # 🐙 Киллы: {red_kills} | Башни: {red_towers}
        timestamp = divmod(score_data['time'], 60)
        minutes = timestamp[0] if timestamp[0] > 9 else f"0{timestamp[0]}"
        seconds = timestamp[1] if timestamp[1] > 9 else f"0{timestamp[1]}"
        message_for_reply = message_sample.format(
            blue_kills = score_data['blue_kills'],
            blue_towers = score_data['blue_towers'],
            red_kills = score_data['red_kills'],
            red_towers = score_data['red_towers'],
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

async def mcf_status(update: Update, context: CallbackContext) -> None:
    
    status_path = status_mcf()

    with open(status_path, 'rb') as photo_file:
        await update.message.reply_photo(photo=photo_file)

    # await update.message.reply_text('Бот перезагружен')
async def stats_check(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    with open(os.path.join('.', 'arambot_lib', 'debug_stats.json'), 'r', encoding='utf-8') as js_stats:
        stats_register = json.load(js_stats)
        message = f"Результат по стате | + ({stats_register['PLUS']}) - ({stats_register['minus']})"
        await update.message.reply_text(message)
       
def main() -> None:
    """Start the bot."""
    application = Application.builder().token(os.getenv('BOT_TOKEN')).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'\bgame\b'), echo_score))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'\bbuild\b'), echo_build))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'\bstats_result\b'), stats_check))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'mirr_\S+'), gen_url))
    # application.add_handler(CommandHandler('build', echo_build))
    # application.add_handler(CommandHandler('stats_check', stats_check))
    application.add_handler(CommandHandler('mcf_reload', mcf_reload))
    application.add_handler(CommandHandler('mcf_status', mcf_status))
    # application.add_handler(CommandHandler('stats_check', stats_check))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()