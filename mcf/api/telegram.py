import requests
import logging
from functools import wraps
from shared.config import Config
from shared.storage import uStorage
from mcf.api.common import get_session, retry_on_network
from static import (
    TelegramStr
)
from mcf.dynamic import CF

logger = logging.getLogger(__name__)

class TGApi:

    active_pr_id = 0
    active_pr_text = ''
    active_post_id = 0
    active_post_text = ''
    token = Config.tg_token()
    method_send = 'sendMessage'
    method_edit = 'editMessageText'
    tg_api_url = 'https://api.telegram.org/bot{token}/{method}'
    RES_FOR_PREDICT = False
    # CHAT_ID = os.getenv('CHAT_ID')
    CHAT_ID_PUB = Config.tg_chat_pub()
    CHAT_ID_PR = Config.tg_chat_pr()
    # CHAT_ID_TRIAL = os.getenv('CHAT_ID_TRIAL')

    
    # Shared HTTP session with retries (common)
    _session = get_session()

    def timeout_handler(func):
        # Backward-compatible alias using common retry decorator
        return wraps(func)(retry_on_network()(func))

    @timeout_handler
    def post_edit(message: str, chat_id: int, post_id: int):

        TGApi._session.post(
            url=TGApi.tg_api_url.format(token=TGApi.token, method=TGApi.method_edit),
            data={'chat_id': chat_id, 
                'message_id': post_id,
                'text': message,
                'disable_web_page_preview': True}, timeout=2
            )

    @timeout_handler
    def post_send(message: str, chat_id: int):

        resp = TGApi._session.post(
            url=TGApi.tg_api_url.format(token=TGApi.token, method=TGApi.method_send),
            data={'chat_id': chat_id, 
                  'text': message,
                  'disable_web_page_preview': True}, timeout=2
        )
 
        return resp.json()
             
    @classmethod
    def post_request(cls, message: str, save_post_result=False, message_type=None, link=None):
        
        if message_type == 'predict':
            message_pr = TelegramStr.only_pr_message.format(
                pr_message = message,
                chars_blue = CF.SR.blue_characters,
                chars_red = CF.SR.red_characters,
                link=link
            )

            result = cls.post_send(message=message_pr, chat_id=cls.CHAT_ID_PR)
            logger.info(result)
            cls.active_pr_id = result['result']['message_id']
            cls.active_pr_text = result['result']['text']
            
            

        # if message_type == 'winner_opened':
            
        #     cls.post_send(message=message + '\n' + link, chat_id=cls.CHAT_ID_PR)
        
        request = cls.post_send(message=message, chat_id=cls.CHAT_ID_PUB)

        if save_post_result:
            cls.active_post_id = request['result']['message_id']
            cls.active_post_text = request['result']['text']

    @classmethod
    def update_predict_result(cls, state=None):
        
        "Функция обновляет значок плюса или минуса в канале OnlyPredicts"
        
        if state == 'plus':
            result = '✅' + cls.active_pr_text
        elif state == 'minus':
            result = '❌' + cls.active_pr_text
        
        cls.post_edit(
            message=result,
            chat_id=cls.CHAT_ID_PR,
            post_id=cls.active_pr_id,
        )

    @classmethod
    def update_score(cls, score, is_total_opened=False, total_value=0):
        
        if score:
            timestamp = divmod(int(score['time']), 60)
            
            score['time'] = f"{timestamp[0]:02}:{timestamp[1]:02}"
            score['total_value'] = total_value
            
            if is_total_opened:
                open_snip = TelegramStr.events_opened.format(total_value=total_value)

                # all_kills = score['blue_kills'] + score['red_kills']
                # if not CF.SW.total_diff.is_active() and abs(all_kills - int(float(total_value))) < 20:
                    
                #     alert = f"⚠️ В игре: {all_kills} | ТБ: {total_value} | {TelegramStr.CLOCK}: {score['time']}"
                #     cls.post_send(message=alert, chat_id=cls.CHAT_ID_PR)
                #     uStorage.upd_pr_signal(diff_total=all_kills)
                #     CF.SW.total_diff.activate()

            else:
                open_snip = TelegramStr.events_closed
            # score['total_value']
            text = cls.active_post_text + TelegramStr.SNIPPET_SCORE.format(**score) + open_snip
        else:
            text = cls.active_post_text

        try:
            TGApi._session.post(
            url=TGApi.tg_api_url.format(token=TGApi.token, method=cls.method_edit),
            data={'chat_id': cls.CHAT_ID_PUB, 
                'message_id': cls.active_post_id, 
                'text': text }, timeout=2
            )
            
        except (requests.exceptions.ConnectTimeout,
                requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout) as ex_:
            logger.warning(ex_)
            pass
        
    @classmethod
    def gamestart_notification(cls, team_blue: list, team_red: list, status_message=''):

        full_message = TelegramStr.SNIPPET_GAMESTART.format(
            team_blue=team_blue,
            team_red=team_red,
            status_message=status_message
        )

        cls.post_request(message=full_message, save_post_result=True)
    
    @classmethod
    def winner_is(cls, winner: str, kills: int, timestamp: str, opened=False, link=None):
        
        minutes = int(timestamp[0])

        timestamp_string = f"{timestamp[0]:02}:{timestamp[1]:02}"
        
        match winner, opened:
            case 'blue' | 'red', True:
                message = TelegramStr.winner_opened[winner].format(kills, timestamp_string)
                if minutes >= 10:
                    uStorage.upd_pr_signal(endgame_total=kills)
                    cls.post_send(message=message + '\n\n' + link, chat_id=cls.CHAT_ID_PR)

                cls.post_request(message=message, message_type='winner_opened', link=link)
                
            case 'blue' | 'red', False:
                message = TelegramStr.winner[winner].format(kills, timestamp_string)
                cls.post_request(message=message)
                pass
