import requests
import os
import logging
import time
from global_data import Validator
from mcf_data import (
    Switches,
    WINDOWS_USER,
    SCORE_SNIPPET,
)

logger = logging.getLogger(__name__)

class TGApi:

    # test_run = False
    active_post_id = 0
    active_post_text = ''
    token = os.getenv('BOT_TOKEN')
    method_send = 'sendMessage'
    method_edit = 'editMessageText'
    tg_api_url = 'https://api.telegram.org/bot{token}/{method}'
    RES_FOR_PREDICT = False
    CHAT_ID = os.getenv('CHAT_ID')
    CHAT_ID_PUB = os.getenv('CHAT_ID_PUB')
    CHAT_ID_TRIAL = os.getenv('CHAT_ID_TRIAL')

    
    def timeout_handler(func):
        def wrapper(*args, **kwargs):
            while True:
                try:
                    return func(*args, **kwargs)
                except (requests.exceptions.ConnectTimeout,
                        requests.exceptions.ConnectionError,
                        requests.exceptions.ReadTimeout) as ex_:
                    logger.warning(ex_)
                    pass
    
        return wrapper

    @timeout_handler
    def post_send(message: str, chat_id):

        resp = requests.post(
            url=TGApi.tg_api_url.format(token=TGApi.token, method=TGApi.method_send),
            data={'chat_id': chat_id, 'text': message }, timeout=2
        )

        # print(resp.json())
        return resp.json()
            

        
    @classmethod
    def post_request(cls, message: str, save_post_result=False):
        
        request = cls.post_send(message=message, chat_id=cls.CHAT_ID_PUB)
        # print(request)
        if save_post_result:
            cls.active_post_id = request['result']['message_id']
            cls.active_post_text = request['result']['text']

            # print(cls.active_post_id, cls.active_post_text)

        time.sleep(2)
        cls.post_send(message=message, chat_id=cls.CHAT_ID_TRIAL)

    @classmethod
    def run_score_updating(cls):
        
        while Switches.request:

            score = {
                'time': 
                'blue_kills'
                'red_kills'
                'blue_towers'
                'red_towers'
                'blue_gold'
                'red_gold'
                'blue_t1_hp'
                'red_t1_hp'
            }
            


    @classmethod
    def update_score(cls, score, is_total_opened=False, total_value=0):
        
        if score:
            timestamp = divmod(int(score['time']), 60)
            minutes = timestamp[0] if timestamp[0] > 9 else f"0{timestamp[0]}"
            seconds = timestamp[1] if timestamp[1] > 9 else f"0{timestamp[1]}"

            score['time'] = ':'.join([str(minutes), str(seconds)])
            score['total_value'] = total_value
            if is_total_opened:
                open_snip = f'\n\nTotal event {total_value}: ❕ Opened'
            else:
                open_snip = '\n\nTotal event: ❗️ Closed'
            # score['total_value']
            text = cls.active_post_text + SCORE_SNIPPET.format(**score) + open_snip
        else:
            text = cls.active_post_text

        try:
            requests.post(
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

        sample_message: str = open('mcf_lib/tg_start_notification.txt', 'r', encoding='utf-8').read()
        
        full_message = sample_message.format(
            team_blue=team_blue,
            team_red=team_red,
            status_message=status_message
        )

        cls.post_request(message=full_message, save_post_result=True)

    @classmethod
    def send_simple_message(cls, message: str):        
        cls.post_request(message=message)
    
    @classmethod
    def winner_is(cls, team, kills, timestamp, opened=False):
        
        match team, opened:
            case 'blue', True:
                message = f'🟢🔵 П1 -- {kills} -- {timestamp}'
            case 'blue', False:
                message = f'🔵 П1 -- {kills} -- {timestamp}'
            case 'red', True:
                message = f'🟢🔴 П2 -- {kills} -- {timestamp}'
            case 'red', False:
                message = f'🔴 П2 -- {kills} -- {timestamp}'
            case _:
                pass

        cls.post_request(message=message)
