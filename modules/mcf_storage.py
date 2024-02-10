import json
import os
from mcf_data import (
    DEBUG_STATS_PATH,
    JSON_GAMEDATA_PATH,
    MCF_BOT_PATH,
)

class MCFStorage:

    @classmethod
    def get_gameid():
        with open(os.path.join(MCF_BOT_PATH, 'mcf_lib', 'previous_gameid.txt'), 'r') as file:
            return file.read()

    @classmethod
    def save_gameid(game_id: str):

        with open(os.path.join(MCF_BOT_PATH, 'mcf_lib', 'previous_gameid.txt'), 'w+') as file:
            file.write(game_id)
        # open()
    @classmethod
    def save_score(cls, score: dict = None, stop_tracking=False):

        with open(os.path.join(MCF_BOT_PATH, 'arambot_lib', 'activegame_score.json'), 'r') as file:
            data = json.load(file)

        if stop_tracking:
            data['is_active'] = False
        else:
            data = score
        
        with open(os.path.join(MCF_BOT_PATH, 'arambot_lib', 'activegame_score.json'), 'w+') as file:
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
            raise TypeError('Provide touple for executing MCFData')
    
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