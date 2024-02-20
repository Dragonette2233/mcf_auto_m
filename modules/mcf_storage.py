import json
from global_data import Validator
from mcf_data import (
    DEBUG_STATS_PATH,
    JSON_GAMEDATA_PATH,
    PREVIOUS_GAMEID_PATH,
    ACTIVE_GAMESCORE_PATH,
    PREDICTS_TRACE_PATH
)

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

        with open(ACTIVE_GAMESCORE_PATH, 'r') as file:
            data = json.load(file)

        if stop_tracking:
            data['is_active'] = False
        else:
            data = score
        
        with open(ACTIVE_GAMESCORE_PATH, 'w+') as file:
            json.dump(data, file, indent=4)

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
    def predicts_monitor(cls, kills: int):
        
        if Validator.predict_value_flet is None:
            return

        with open(PREDICTS_TRACE_PATH, 'r', encoding='utf-8') as file:
            data = json.load(file)

        print(data)
        match Validator.predict_value_flet:
            case ("110Б", fl):
                if kills >= 115:
                    data[f"110Б (FL {fl})"][0] += 1
                else:
                    data[f"110Б (FL {fl})"][1] += 1
            case ("110М", fl):
                if kills <= 105:
                    data[f"110М (FL {fl})"][0] += 1
                else:
                    data[f"110М (FL {fl})"][1] += 1
            case _:
                ...
        
        Validator.predict_value_flet = None

    
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