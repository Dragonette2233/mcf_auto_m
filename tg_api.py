import requests
import os
import logging
from global_data import Validator
from mcf_data import (
    Switches,
    WINDOWS_USER,
    StatsRate

)

logger = logging.getLogger(__name__)

class TGApi:

    token = os.getenv('BOT_TOKEN')
    method_send = 'sendMessage'
    method_updates = 'getUpdates'
    tg_api_url = 'https://api.telegram.org/bot{token}/{method}'
    RES_FOR_PREDICT = False
    CHAT_ID = os.getenv('CHAT_ID')
    CHAT_PREDICTS = os.getenv('CHAT_PREDICTS')

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
                    
                    pass
    
        return wrapper

    @switch_active
    @timeout_handler
    # @classmethod
    def post_request(message: str, predicts_chat=False):

        if predicts_chat:
            chat_id = TGApi.CHAT_PREDICTS
        else:
            chat_id = TGApi.CHAT_ID

        requests.post(
            url=TGApi.tg_api_url.format(token=TGApi.token, method=TGApi.method_send),
            data={'chat_id': chat_id, 'text': message }, timeout=2
        )
    
    @classmethod
    def gamestart_notification(cls, champions: list):

        formated_dict = {}

        # if StatsRate.is_stats_avaliable():
        #     formated_dict['W1'], formated_dict['W1_e'] = StatsRate.blue_rate[0], StatsRate.blue_rate[1]
        #     formated_dict['W2'], formated_dict['W2_e'] = StatsRate.red_rate[0], StatsRate.red_rate[1]
        #     formated_dict['TB'], formated_dict['TB_e'] = StatsRate.tb_rate[0], StatsRate.tb_rate[1]
        #     formated_dict['TL'], formated_dict['TL_e'] = StatsRate.tl_rate[0], StatsRate.tl_rate[1]
        #     formated_dict['ALL'] = StatsRate.games_all
        #     formated_dict['TTL'] = StatsRate.games_totals

        sample_message: str = open('mcf_lib/tg_send_empty.txt', 'r', encoding='utf-8').read()

        
        for i, name in enumerate(champions):
            formated_dict[f'p_{i}'] = name

        full_message = sample_message.format(
            **formated_dict
        )

        cls.post_request(message=full_message)

        # Validator.stats_register['W1_pr'] = 0 if formated_dict['W1_e'] == '🟥' else 1
        # Validator.stats_register['W2_pr'] = 0 if formated_dict['W2_e'] == '🟥' else 1
        # Validator.total_register['W1_pr'] = 0 if formated_dict['TB_e'] == '🟥' else 1
        # Validator.total_register['W2_pr'] = 0 if formated_dict['TL_e'] == '🟥' else 1

    
    @classmethod
    def send_simple_message(cls, message: str, predict_ttl = False, predict_win = False, spredict = False):
        # Switches.predicted = True
        if predict_ttl:
            Switches.predicted_total = True
            try:
                _tmp = message.split()
                value = _tmp[2]
                flet = _tmp[4][:-1]
                Validator.predict_value_flet = (value, flet)
                cls.post_request(message=message, predicts_chat=True)
                cls.RES_FOR_PREDICT = True
            except Exception as ex_:
                logger.warning(ex_)
        if predict_win:
            Switches.predicted_winner = True
            cls.post_request(message=message, predicts_chat=True)
            cls.RES_FOR_PREDICT = True
        if spredict:
            Switches.spredicted = True
            cls.post_request(message=message, predicts_chat=True)
            cls.RES_FOR_PREDICT = True

        
        cls.post_request(message=message)
    
    @classmethod
    def winner_is(cls, team, kills, timestamp, opened=False):
        
        match team, opened:
            case 'blue', True:
                # Switches.coeff_opened = True
                message = f'🟢🔵 П1 -- {kills} -- {timestamp}'
                cls.RES_FOR_PREDICT = True
            case 'blue', False:
                message = f'🔵 П1 -- {kills} -- {timestamp}'
            case 'red', True:
                # Switches.coeff_opened = True
                message = f'🟢🔴 П2 -- {kills} -- {timestamp}'
                cls.RES_FOR_PREDICT = True
                # if not cls.RES_FOR_PREDICT:
                #     cls.post_request(message=message, predicts_chat=True)
            case 'red', False:
                message = f'🔴 П2 -- {kills} -- {timestamp}'
            case _:
                pass

        cls.post_request(message=message)
        if cls.RES_FOR_PREDICT:
            cls.post_request(message=message, predicts_chat=True)
            cls.RES_FOR_PREDICT = False