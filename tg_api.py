import requests
import os
import logging
import time
from global_data import Validator
from mcf_data import (
    Switches,
    WINDOWS_USER,
)

logger = logging.getLogger(__name__)

class TGApi:

    # test_run = False
    token = os.getenv('BOT_TOKEN')
    method_send = 'sendMessage'
    method_updates = 'getUpdates'
    tg_api_url = 'https://api.telegram.org/bot{token}/{method}'
    RES_FOR_PREDICT = False
    CHAT_ID = os.getenv('CHAT_ID')
    CHAT_ID_PUB = os.getenv('CHAT_ID_PUB')
    CHAT_ID_TRIAL = os.getenv('CHAT_ID_TRIAL')

    # @classmethod
    def switch_active(func):
        def wrapper(*args, **kwargs):
            if WINDOWS_USER == 'ARA-M': # REMOVE !
                func(*args, **kwargs)
    
        return wrapper
    
    def timeout_handler(func):
        def wrapper(*args, **kwargs):
            while True:
                try:
                    func(*args, **kwargs)
                    break
                except (requests.exceptions.ConnectTimeout,
                        requests.exceptions.ConnectionError,
                        requests.exceptions.ReadTimeout):
                    print('here')
                    pass
    
        return wrapper

    @switch_active
    @timeout_handler
    def post_send(message: str, chat_id):

        requests.post(
            url=TGApi.tg_api_url.format(token=TGApi.token, method=TGApi.method_send),
            data={'chat_id': chat_id, 'text': message }, timeout=2
        )

        
    @classmethod
    def post_request(cls, message: str):
        
        # cls.post_send(message=message, chat_id=cls.CHAT_ID)
        cls.post_send(message=message, chat_id=cls.CHAT_ID_PUB)
        time.sleep(2)
        cls.post_send(message=message, chat_id=cls.CHAT_ID_TRIAL)


    @classmethod
    def gamestart_notification(cls, team_blue: list, team_red: list, status_message=''):

        sample_message: str = open('mcf_lib/tg_start_notification.txt', 'r', encoding='utf-8').read()
        
        full_message = sample_message.format(
            team_blue=team_blue,
            team_red=team_red,
            status_message=status_message
        )

        cls.post_request(message=full_message)

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
