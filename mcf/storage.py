import json
import logging
from datetime import datetime
from mcf.dynamic import CF
from mcf.static import PATH
from mcf.api.telegram import TGApi

logger = logging.getLogger(__name__)

class SafeJson:

    @staticmethod
    def load(json_path: str) -> dict:

        with open(json_path, 'r', encoding='utf-8') as file:
            data: dict = json.load(file)
        return data
    
    @staticmethod
    def dump(json_path, data: dict):

        with open(json_path, 'w+', encoding='utf-8') as file:
            json.dump(data, file, indent=4)

class MCFStorage:

    TODAY = datetime.now().day

    @classmethod
    def get_gameid(cls):
        with open(PATH.PREVIOUS_GAMEID, 'r') as file:
            gameid = file.read()
            return gameid

    @classmethod
    def save_gameid(cls, game_id: str):

        with open(PATH.PREVIOUS_GAMEID, 'w+') as file:
            file.write(game_id)

    @classmethod
    def get_selective_data(cls, route: tuple):
        data = json.load(open(PATH.JSON_GAMEDATA, 'r'))
        if isinstance(route, tuple):
            if len(route) > 1:
                return data[route[0]][route[1]]
            else:
                return data[route[0]]
        else:
            raise TypeError('Provide touple for executing MCFData')


    @classmethod
    def get_all_data(cls) -> dict:
        data = json.load(open(PATH.JSON_GAMEDATA, 'r'))
        return data

    @classmethod
    def write_data(cls, route: tuple, value):
        data = json.load(open(PATH.JSON_GAMEDATA, 'r'))
        if isinstance(route, tuple):
            if len(route) > 1:
                data[route[0]][route[1]] = value
            else:
                data[route[0]] = value
            json.dump(data, open(PATH.JSON_GAMEDATA, 'w+'), indent=4)
        else:
            raise TypeError('Provide tuple for executing MCFData')
    
    @classmethod
    def rgs_predicts_monitor(cls, message: str, idx: int):
        try:
            _tmp = message.split()
            value = _tmp[1][0:-1]
            direction = 'Т' + _tmp[1][-1]
            flet = _tmp[2].split('_')[1][:-1]
            
            CF.VAL.pr_cache = (value, direction, flet)
            CF.VAL.pr_debug = idx

            logger.info(f"PR accepted: {value} | {direction} | {flet}")
            
        except Exception as ex_:
            logger.warning(ex_)


    @classmethod
    def predicts_monitor(cls, kills: int, daily=False):

        if CF.VAL.pr_cache in (None, 'closed'):
            return

        if daily:
            predicts_path = PATH.PREDICTS_TRACE_DAILY
            trace_day = datetime.now().day

            if trace_day != cls.TODAY:
                data = SafeJson.load(predicts_path)
                
                for predict in data.keys():
                   data[predict][0] = 0
                   data[predict][1] = 0
                
                SafeJson.dump(json_path=predicts_path, data=data)
                
                cls.TODAY = trace_day
                   
        else:
            predicts_path = PATH.PREDICTS_TRACE_GLOBAL

        data = SafeJson.load(predicts_path)

        # # sample of predicts_value_flet = ('96.5', 'ТМ', '0.5')
        match CF.VAL.pr_cache:
            case (value, 'ТБ' as direction, flet):
                if kills > float(value):
                    data[f"{direction} (FL {flet})"][0] += 1
                    TGApi.update_predict_result(state='plus')
                else:
                    data[f"{direction} (FL {flet})"][1] += 1
                    TGApi.update_predict_result(state='minus')

            case (value, 'ТМ' as direction, flet):
                if kills < float(value):
                    data[f"{direction} (FL {flet})"][0] += 1
                    TGApi.update_predict_result(state='plus')
                else:
                    data[f"{direction} (FL {flet})"][1] += 1
                    TGApi.update_predict_result(state='minus')
            case other:
                logger.info(f"Undefined value: {other}")

        if CF.VAL.pr_debug is not None:
            
            value, direction, flet = CF.VAL.pr_cache

            open('./untracking/reg_debug.txt', 'a+', encoding='utf-8').writelines(
                    f"{direction}_{flet} #{CF.VAL.pr_debug} | Val_End: {value}_{kills} | Roles: {CF.SR.blue_roles}_{CF.SR.red_roles}\n"
                )
            CF.VAL.pr_debug = None
        
        SafeJson.dump(json_path=predicts_path, data=data)
        logger.info(f"PR {predicts_path} - register done")