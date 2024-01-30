import sys
import requests
import os

from mcf_data import (
    Switches,
    Validator
)

class TGApi:

    token = os.getenv('BOT_TOKEN')
    method_send = 'sendMessage'
    method_updates = 'getUpdates'
    tg_api_url = 'https://api.telegram.org/bot{token}/{method}'
    CHAT_ID = os.getenv('CHAT_ID')

    def switch_active(func):
        def wrapper(*args, **kwargs):
            if Switches.bot_activity:
                func(*args, **kwargs)
    
        return wrapper

    
    @classmethod
    @switch_active
    def gamestart_notification(cls, nickname: str, champions: list, statsrate: dict):

        sample_message: str = open('mcf_lib/telegram_message_sample.txt', 'r', encoding='utf-8').read()

        formated_dict = {}
        # print(len(champions))
        for i, name in enumerate(champions):
            formated_dict[f'p_{i}'] = name

        formated_dict['nickname'] = nickname
        # formated_dict['W1'], formated_dict['W1_e'] = statsrate['w1'][0], statsrate['w1'][1]
        # formated_dict['W2'], formated_dict['W2_e'] = statsrate['w2'][0], statsrate['w2'][1]
        formated_dict['TB'], formated_dict['TB_e'] = statsrate['tb'][0], statsrate['tb'][1]
        formated_dict['TL'], formated_dict['TL_e'] = statsrate['tl'][0], statsrate['tl'][1]
        formated_dict['ALL'] = statsrate['all_m'][0]
        formated_dict['TTL'] = statsrate['all_ttl'][0]

        full_message = sample_message.format(
            **formated_dict
        )

        requests.post(
            url=cls.tg_api_url.format(token=cls.token, method=cls.method_send),
            data={'chat_id': cls.CHAT_ID, 'text': full_message }
        )

        # Validator.stats_register['W1_pr'] = 0 if formated_dict['W1_e'] == '🟥' else 1
        # Validator.stats_register['W2_pr'] = 0 if formated_dict['W2_e'] == '🟥' else 1
        Validator.total_register['W1_pr'] = 0 if formated_dict['TB_e'] == '🟥' else 1
        Validator.total_register['W2_pr'] = 0 if formated_dict['TL_e'] == '🟥' else 1

    
    @classmethod
    @switch_active
    def send_simple_message(cls, message):
        Switches.predicted = True
        requests.post(
            url=cls.tg_api_url.format(token=cls.token, method=cls.method_send),
            data={'chat_id': cls.CHAT_ID, 'text': message }
        )

    
    @classmethod
    @switch_active
    def display_gamestart(cls, timer):

        requests.post(
            url=cls.tg_api_url.format(token=cls.token, method=cls.method_send),
            data={'chat_id': cls.CHAT_ID, 'text': f'⚪️ Игра началась -- {timer}' }
        )

    
    @classmethod
    @switch_active
    def winner_is(cls, team, kills, timestamp, disabled):
        
        match team, disabled:
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


        requests.post(
            url=cls.tg_api_url.format(token=cls.token, method=cls.method_send),
            data={'chat_id': cls.CHAT_ID, 'text': message}
        )