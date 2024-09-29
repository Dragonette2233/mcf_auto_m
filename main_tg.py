import logging
from telegram import Update
from functools import wraps
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters
from io import BytesIO
from PIL import ImageGrab
from static import TGSMP
from mcf.api.storage import uStorage


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

OWNER = int(uStorage.get_key('OWNER'))
AUTH_COMMAND = uStorage.get_key('AUTH_COMMAND')
BOT_TOKEN = uStorage.get_key("BOT_TOKEN")
CHAT_LINK = '\nhttps://t.me/' + uStorage.get_key('CHAT_LINK')
NFA_LINK = '\nhttps://t.me/' + uStorage.get_key('NFA_LINK')

# def auth():
def auth(func):
    @wraps(func)
    async def wrapper(update: Update, context: CallbackContext):
        user_id = update.message.from_user.id
        if user_id == OWNER:
            
            return await func(update, context)
        else:
            
            await update.message.reply_text("🚫 Unauthorized")
    return wrapper


async def info(update: Update, context: CallbackContext):
    
    if update.message.text == '/info':
        answer = TGSMP.MAIN_INFO
    elif update.message.text == '/info_bets':
        answer = TGSMP.BETS_INFO
    await update.message.reply_text(answer)

async def start(update: Update, context: CallbackContext):

    visitor = update.message.chat.first_name

    await update.message.reply_text(TGSMP.GREET_MESSAGE.format(visitor=visitor,
                                                               chat_link=CHAT_LINK,
                                                               nfa_link=NFA_LINK))
async def actual_mirror(update: Update, context: CallbackContext):
    
    msg = update.message.text
        
    if msg == '/mirror':
        mirror = uStorage.get_key("MIRROR_PAGE")
        await update.message.reply_text('Актуальное зеркало: %s' % mirror)
    elif msg == '/current_game':
        curr = uStorage.get_key("CURRENT_GAME_LINK")
        
        if curr == 'None':
            resp = "В данный момент нет отслеживаемой игры"
        else:
            resp = f'Ссылка на актуальную игру: {curr}'
            
        await update.message.reply_text(resp)

@auth
async def change_actual_mirror(update: Update, context: CallbackContext):

    league_alt_rout = '/ru/live/cyber-zone/league-of-legends'
    message = update.message.text

    if not message.startswith('https://1xlite-') and not message.startswith('https://melb'):
        await update.message.reply_text(f'Неверная ссылка для зеркала')
    else:
        link_parts = message.split('/')
        new_link = '/'.join(link_parts[0:3]) + league_alt_rout
        uStorage.upd_mirror_page(link=new_link)
        await update.message.reply_text(f'Зеркало добавлено: {new_link}')

@auth
async def mcf_status(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id == OWNER:
        
        
        screen = ImageGrab.grab()
        img_byte_array = BytesIO()
        screen.save(img_byte_array, format='PNG')
        img_byte_array.seek(0)

        # Отправка изображения как фото
        await update.message.reply_photo(photo=img_byte_array)


async def pr_channel(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(TGSMP.PR_CHANNEL_MESSAGE)

async def predicts_check(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    predicts_answer_message = TGSMP.PREDICTS_ANSWER

    if update.message.text == '/pr_global':
        top_message = 'Результат по предиктам за все время'
        predicts = uStorage.get_pr_result(key="GLOBAL")
    else:
        top_message = 'Результат по предиктам за сутки'
        predicts = uStorage.get_pr_result(key="DAILY")

    # with open(predicts_STORAGE, 'r', encoding='utf-8') as js_stats:
    # predicts: dict = json.load(js_stats)
    itms = list(predicts.items())

    ordered_plus = [value[1][0] for value in itms]
    ordered_minus = [value[1][1] for value in itms]

    message = predicts_answer_message.format(*ordered_plus, *ordered_minus, top_message=top_message)

    await update.message.reply_text(message)
       
def main() -> None:
    """Start the bot."""

    application = Application.builder().token(BOT_TOKEN).build()
    
    command_handler = (
        ('start', start),
        ('pr_global', predicts_check),
        ('pr_daily', predicts_check),
        ('pr_channel', pr_channel),
        ('info', info),
        ('info_bets', info),
        ('mirror', actual_mirror),
        ('current_game', actual_mirror),
        ('mcf_status', mcf_status)
        
    )
    
    for cmd, hndl in command_handler:
        application.add_handler(CommandHandler(cmd, hndl))
        
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'https\S+'), change_actual_mirror))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()