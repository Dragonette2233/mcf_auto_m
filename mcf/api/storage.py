import json
import logging
from datetime import datetime
from mcf.dynamic import CF
from static import PATH

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

    @staticmethod
    def load_and_dump(json_path, key, value):
        
        sdata = SafeJson.load(json_path)
        sdata[key] = value
        SafeJson.dump(json_path, sdata)
        
class uStorage():
    """summary_

    class for untracking data
    """
    UPATH = PATH.UPARAMS
    PR_TRACE = PATH.PR_TRACE
    TODAY = datetime.now().day
    
    @classmethod
    def get_pr_result(cls, key: str) -> dict | None:
        data = SafeJson.load(PATH.PR_TRACE)
        
        try:
            return data[key]
        except KeyError:
            logger.fatal("Key %s doesnt exist in `pr_trace` " % key)
            
    @classmethod
    def get_key(cls, key: str) -> str:
        data = SafeJson.load(cls.UPATH)
        
        try:
            return data[key]
        except KeyError:
            logger.fatal("Key %s doesnt exist in `uparams` " % key)
    
    @classmethod
    def upd_pr_message(cls, pr_message: str = "", endgame_total=None):
        # msg example PR 108.5М FL_0.75
        
        if endgame_total:
            pr = f"PR_E{endgame_total}"
        else:
            _, msg, _ = pr_message.split()
            
            if msg[-1] in ('M', 'М'):
                pr = "PR_LESS"
            elif msg[-1] == 'Б':
                pr = "PR_BIG"
        
        SafeJson.load_and_dump(cls.UPATH, key="PR_STATE", value=pr)
    
    @classmethod
    def upd_current_game_status(cls, status=''):
        SafeJson.load_and_dump(cls.UPATH, key="CURRENT_GAME_STATUS", value=status)
    
    @classmethod
    def upd_current_game_link(cls, link=None):
        if link is not None:
            SafeJson.load_and_dump(cls.UPATH, key="CURRENT_GAME_LINK", value=link)
        else:
            SafeJson.load_and_dump(cls.UPATH, key="CURRENT_GAME_LINK", value="None")
    
    @classmethod
    def upd_previous_game_id(cls, game_id=None):
        if game_id is not None:
            SafeJson.load_and_dump(cls.UPATH, key="PREVIOUS_GAME_ID", value=game_id)
            
    @classmethod
    def upd_mirror_page(cls, link=None):
        if link is not None:
            SafeJson.load_and_dump(cls.UPATH, key="MIRROR_PAGE", value=link)
    
    @classmethod
    def save_predict_result(cls, kills):
        pr_result = cls.upd_pr_result(kills=kills)
        cls.upd_pr_result(kills=kills, daily=True)
        
        return pr_result
    
    @classmethod
    def upd_pr_result(cls, kills: int, daily=False):

        result = None
        
        if CF.VAL.pr_cache in (None, 'closed'):
            return
        
        # print

        if daily:
            pr_key = "DAILY"
            trace_day = datetime.now().day

            if trace_day != cls.TODAY:
                data: dict = SafeJson.load(PATH.PR_TRACE)
                # data = SafeJson.load(predicts_path)
                
                for predict in data[pr_key].keys():
                   data[pr_key][predict][0] = 0
                   data[pr_key][predict][1] = 0
                
                SafeJson.dump(json_path=PATH.PR_TRACE, data=data)
                
                cls.TODAY = trace_day
            
            print(pr_key)
                   
        else:
            pr_key = "GLOBAL"

        data = SafeJson.load(PATH.PR_TRACE)

        # # sample of predicts_value_flet = ('96.5', 'ТМ', '0.5')\
        print(CF.VAL.pr_cache)
        match CF.VAL.pr_cache:
            
            case (value, 'ТБ' as direction, flet):
                if kills > float(value):
                    data[pr_key][f"{direction} (FL {flet})"][0] += 1
                    # print("THERE")
                    result = 'plus'
                    # TGApi.update_predict_result(state='plus')
                else:
                    data[pr_key][f"{direction} (FL {flet})"][1] += 1
                    result = 'minus'
                    # TGApi.update_predict_result(state='minus')

            case (value, 'ТМ' as direction, flet):
                if kills < float(value):
                    data[pr_key][f"{direction} (FL {flet})"][0] += 1
                    result = 'plus'
                    # TGApi.update_predict_result(state='plus')
                else:
                    data[pr_key][f"{direction} (FL {flet})"][1] += 1
                    result = 'minus'
                    # TGApi.update_predict_result(state='minus')
            case other:
                print(other)
                logger.info(f"Undefined value: {other}")

        # if CF.VAL.pr_debug is not None:
            
        #     value, direction, flet = CF.VAL.pr_cache

        #     open('./untracking/reg_debug.txt', 'a+', encoding='utf-8').writelines(
        #             f"{direction}_{flet} #{CF.VAL.pr_debug} | Val_End: {value}_{kills} | Roles: {CF.SR.blue_roles}_{CF.SR.red_roles}\n"
        #         )
        #     CF.VAL.pr_debug = None
        # print('saved')
        # print(data)
        SafeJson.dump(json_path=PATH.PR_TRACE, data=data)
        logger.info(f"PR {pr_key} - register done")
        
        return result
        
    # @classmethod
    # def get_previous_game_id(cls):
    #     # if game_id is not None:
    #     data = SafeJson.load(cls.UPATH)
    #     return data["PREVIOUS_GAME_ID"]
        
class MCFStorage:

    TODAY = datetime.now().day

    @classmethod
    def update_pr_message(cls, pr_message: str = "", endgame_total=None):
        # msg example PR 108.5М FL_0.75
        
        if endgame_total:
            pr = f"PR_E{endgame_total}"
        else:
            _, msg, _ = pr_message.split()
            
            if msg[-1] in ('M', 'М'):
                pr = "PR_LESS"
            elif msg[-1] == 'Б':
                pr = "PR_BIG"
            
        with open(PATH.PR_STATE_FILE, 'w+') as file:
            file.write(pr)
    
    # @classmethod
    # def get_gameid(cls):
    #     with open(PATH.PREVIOUS_GAMEID, 'r') as file:
    #         gameid = file.read()
    #         return gameid

    # @classmethod
    # def save_gameid(cls, game_id: str):

    #     with open(PATH.PREVIOUS_GAMEID, 'w+') as file:
    #         file.write(game_id)
    
    # @classmethod
    # def current_game_tracking(cls, link=None):
    #     with open(PATH.CURRENT_GAME_LINK, 'w+') as file:
    #         file.write(str(link))

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

    

    # @classmethod
    # def _predicts_monitor(cls, kills: int, daily=False):

    #     result = None
        
    #     if CF.VAL.pr_cache in (None, 'closed'):
    #         return

    #     if daily:
    #         predicts_path = PATH.PREDICTS_TRACE_DAILY
    #         trace_day = datetime.now().day

    #         if trace_day != cls.TODAY:
    #             data = SafeJson.load(predicts_path)
                
    #             for predict in data.keys():
    #                data[predict][0] = 0
    #                data[predict][1] = 0
                
    #             SafeJson.dump(json_path=predicts_path, data=data)
                
    #             cls.TODAY = trace_day
                   
    #     else:
    #         predicts_path = PATH.PREDICTS_TRACE_GLOBAL

    #     data = SafeJson.load(predicts_path)

    #     # # sample of predicts_value_flet = ('96.5', 'ТМ', '0.5')
    #     match CF.VAL.pr_cache:
    #         case (value, 'ТБ' as direction, flet):
    #             if kills > float(value):
    #                 data[f"{direction} (FL {flet})"][0] += 1
    #                 result = 'plus'
    #                 # TGApi.update_predict_result(state='plus')
    #             else:
    #                 data[f"{direction} (FL {flet})"][1] += 1
    #                 result = 'minus'
    #                 # TGApi.update_predict_result(state='minus')

    #         case (value, 'ТМ' as direction, flet):
    #             if kills < float(value):
    #                 data[f"{direction} (FL {flet})"][0] += 1
    #                 result = 'plus'
    #                 # TGApi.update_predict_result(state='plus')
    #             else:
    #                 data[f"{direction} (FL {flet})"][1] += 1
    #                 result = 'minus'
    #                 # TGApi.update_predict_result(state='minus')
    #         case other:
    #             logger.info(f"Undefined value: {other}")

    #     if CF.VAL.pr_debug is not None:
            
    #         value, direction, flet = CF.VAL.pr_cache

    #         open('./untracking/reg_debug.txt', 'a+', encoding='utf-8').writelines(
    #                 f"{direction}_{flet} #{CF.VAL.pr_debug} | Val_End: {value}_{kills} | Roles: {CF.SR.blue_roles}_{CF.SR.red_roles}\n"
    #             )
    #         CF.VAL.pr_debug = None
        
    #     SafeJson.dump(json_path=predicts_path, data=data)
    #     logger.info(f"PR {predicts_path} - register done")
        
    #     return result