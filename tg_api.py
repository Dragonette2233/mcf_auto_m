import requests
import os
from mcf_data import (
    Switches,
    Validator,
    WINDOWS_USER

)

class TGApi:

    token = os.getenv('BOT_TOKEN')
    method_send = 'sendMessage'
    method_updates = 'getUpdates'
    tg_api_url = 'https://api.telegram.org/bot{token}/{method}'
    CHAT_ID = os.getenv('CHAT_ID')

    # @classmethod
    def switch_active(func):
        def wrapper(*args, **kwargs):
            if WINDOWS_USER == 'ARA-M':
                func(*args, **kwargs)
    
        return wrapper
    
    def timeout_handler(func):
        def wrapper(*args, **kwargs):
            while True:
                try:
                    func(*args, **kwargs)
                    break
                except (requests.exceptions.ConnectTimeout,
                        requests.exceptions.ConnectionError):
                    
                    pass
    
        return wrapper

    
    @classmethod
    @switch_active
    @timeout_handler
    def gamestart_notification(cls, champions: list, statsrate: dict):

        formated_dict = {}

        if statsrate is None:
            sample_message: str = open('mcf_lib/tg_send_empty.txt', 'r', encoding='utf-8').read()
        else:
            sample_message: str = open('mcf_lib/tg_send_statistics.txt', 'r', encoding='utf-8').read()

            # formated_dict['W1'], formated_dict['W1_e'] = statsrate['w1'][0], statsrate['w1'][1]
            # formated_dict['W2'], formated_dict['W2_e'] = statsrate['w2'][0], statsrate['w2'][1]
            formated_dict['TB'], formated_dict['TB_e'] = statsrate['tb'][0], statsrate['tb'][1]
            formated_dict['TL'], formated_dict['TL_e'] = statsrate['tl'][0], statsrate['tl'][1]
            formated_dict['ALL'] = statsrate['all_m']
            formated_dict['TTL'] = statsrate['all_ttl']

        
        for i, name in enumerate(champions):
            formated_dict[f'p_{i}'] = name

        full_message = sample_message.format(
            **formated_dict
        )

        requests.post(
            url=cls.tg_api_url.format(token=cls.token, method=cls.method_send),
            data={'chat_id': cls.CHAT_ID, 'text': full_message }, timeout=2
        )

        # Validator.stats_register['W1_pr'] = 0 if formated_dict['W1_e'] == '🟥' else 1
        # Validator.stats_register['W2_pr'] = 0 if formated_dict['W2_e'] == '🟥' else 1
        # Validator.total_register['W1_pr'] = 0 if formated_dict['TB_e'] == '🟥' else 1
        # Validator.total_register['W2_pr'] = 0 if formated_dict['TL_e'] == '🟥' else 1

    
    @classmethod
    @switch_active
    @timeout_handler
    def send_simple_message(cls, message, predict = False):
        # Switches.predicted = True
        if predict:
            Switches.predicted = True

        requests.post(
            url=cls.tg_api_url.format(token=cls.token, method=cls.method_send),
            data={'chat_id': cls.CHAT_ID, 'text': message }, timeout=2
        )

    
    @classmethod
    @switch_active
    @timeout_handler
    def display_gamestart(cls, timer):
        
        if timer is None:
            message = '⚪️ Игра началась'
        else:
            message = '⚪️ Игра началась -- {timer}'.format(timer=timer)
    
        requests.post(
            url=cls.tg_api_url.format(token=cls.token, method=cls.method_send),
            data={'chat_id': cls.CHAT_ID, 'text': message }, timeout=2
        )

    
    @classmethod
    @switch_active
    @timeout_handler
    def winner_is(cls, team, kills, timestamp, opened):
        
        match team, opened:
            case 'blue', True:
                # Switches.coeff_opened = True
                message = f'🟢🔵 П1 -- {kills} -- {timestamp}'
            case 'blue', False:
                message = f'🔵 П1 -- {kills} -- {timestamp}'
            case 'red', True:
                # Switches.coeff_opened = True
                message = f'🟢🔴 П2 -- {kills} -- {timestamp}'
            case 'red', False:
                message = f'🔴 П2 -- {kills} -- {timestamp}'
            case _:
                pass


        requests.post(
            url=cls.tg_api_url.format(token=cls.token, method=cls.method_send),
            data={'chat_id': cls.CHAT_ID, 'text': message}, timeout=2
        )