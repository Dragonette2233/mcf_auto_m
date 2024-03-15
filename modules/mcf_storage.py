import json
from global_data import Validator
from mcf_data import (
    DEBUG_STATS_PATH,
    JSON_GAMEDATA_PATH,
    PREVIOUS_GAMEID_PATH,
    ACTIVE_GAMESCORE_PATH,
    PREDICTS_TRACE_PATH
)

import logging
import redis

logger = logging.getLogger(__name__)
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

class MCFStorage:

    @classmethod
    def get_gameid(cls):
        with open(PREVIOUS_GAMEID_PATH, 'r') as file:
            gameid = file.read()
            return gameid

    @classmethod
    def save_gameid(cls, game_id: str):

        with open(PREVIOUS_GAMEID_PATH, 'w+') as file:
            file.write(game_id)
        # open()
    @classmethod
    def save_score(cls, score: dict = None, stop_tracking=False):

        if stop_tracking:
            r.set('is_active', 0)#  = 0
        else:
            for key, value in score.items():
                r.set(key, value)

    @classmethod
    def get_selective_data(cls, route: tuple):
        data = json.load(open(JSON_GAMEDATA_PATH, 'r'))
        if isinstance(route, tuple):
            if len(route) > 1:
                return data[route[0]][route[1]]
            else:
                return data[route[0]]
        else:
            raise TypeError('Provide touple for executing MCFData')


    @classmethod
    def get_all_data(cls) -> dict:
        data = json.load(open(JSON_GAMEDATA_PATH, 'r'))
        return data

    @classmethod
    def write_data(cls, route: tuple, value):
        data = json.load(open(JSON_GAMEDATA_PATH, 'r'))
        if isinstance(route, tuple):
            if len(route) > 1:
                data[route[0]][route[1]] = value
            else:
                data[route[0]] = value
            json.dump(data, open(JSON_GAMEDATA_PATH, 'w+'), indent=4)
        else:
            raise TypeError('Provide tuple for executing MCFData')
    
    @classmethod
    def rgs_predicts_monitor(cls, message: str, key: str):
        try:
            _tmp = message.split()
            predict_type = _tmp[1]
            value = _tmp[2]
            flet = _tmp[4][:-1]
            if predict_type.split('_')[0] == 'S':
                value = '_'.join(['S', value])
            Validator.predict_value_flet[key] = (value, flet)
        except Exception as ex_:
            logger.warning(ex_)



    @classmethod
    def predicts_monitor(cls, kills: int, key: str):
        
        if Validator.predict_value_flet[key] is None:
            return

        with open(PREDICTS_TRACE_PATH, 'r', encoding='utf-8') as file:
            data = json.load(file)

        print(data)
        match Validator.predict_value_flet[key]:
            case ("110Б" | "S_110Б" as ttl, fl):
                if kills >= 115:
                    data[f"{ttl} (FL {fl})"][0] += 1
                else:
                    data[f"{ttl} (FL {fl})"][1] += 1
            case ("110М" | "S_110М" as ttl, fl):
                if kills <= 105:
                    data[f"{ttl} (FL {fl})"][0] += 1
                else:
                    data[f"{ttl} (FL {fl})"][1] += 1
            case _:
                ...
        
        Validator.predict_value_flet[key] = None

    
        with open(PREDICTS_TRACE_PATH, 'w+', encoding='utf-8') as file:
            json.dump(data, file, indent=4)

    @classmethod
    def stats_monitor(cls, validor):

        is_plus = True

        match list(validor.values()):
            case [_, __, 0, 0]:
                return
            case [1, 0, 1, 0]:
                is_plus = True
            case [0, 1, 0, 1]:
                is_plus = True
            case [0, 1, 1, 0]:
                is_plus = False
            case [1, 0, 0, 1]:
                is_plus = False
            case _:
                # print(list(Validator.stats_register.values()))
                print('UNDEFINED IN STATS MONITOR. CHECK CODE')
                return

        import json

        with open(DEBUG_STATS_PATH, 'r', encoding='utf-8') as js_stats:

            stats_register = json.load(js_stats)

        if is_plus:
            stats_register['PLUS'] += 1
        else:
            stats_register['minus'] += 1

        with open(DEBUG_STATS_PATH, 'w+', encoding='utf-8') as js_stats:

            json.dump(stats_register, js_stats, indent=4)