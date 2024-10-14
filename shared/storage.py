import json
import logging
from datetime import datetime
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
    def upd_pr_signal(cls, pr_message: str = "", endgame_total=None, diff_total=None):
        # msg example PR 108.5М FL_0.75
        
        if endgame_total:
            pr = f"PR_E{endgame_total}"
        elif diff_total:
            pr = f"PR_DIFF{diff_total}"
        else:
            _, msg, _ = pr_message.split()
            
            if msg[-1] in ('M', 'М'):
                pr = "PR_LESS"
            elif msg[-1] == 'Б':
                pr = "PR_BIG"
        
        profiles = SafeJson.load(PATH.CASTER_PROFILES_BASE)
        
        for k in profiles.keys():
            profiles[k] = pr
        
        SafeJson.dump(PATH.CASTER_PROFILES_BASE, data=profiles)
        
        # SafeJson.load_and_dump(cls.UPATH, key="PR_STATE", value=pr)
    
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
    def _reset_daily_pr_stats(cls):
        trace_day = datetime.now().day

        if trace_day != cls.TODAY:
            data: dict = SafeJson.load(PATH.PR_TRACE)
            # data = SafeJson.load(predicts_path)
            
            for predict in data["DAILY"].keys():
                data["DAILY"][predict][0] = 0
                data["DAILY"][predict][1] = 0
            
            SafeJson.dump(json_path=PATH.PR_TRACE, data=data)
            
            cls.TODAY = trace_day
    
    @classmethod
    def save_predict_result(cls, kills, pr_data=None):
        # pr_data format ('96.5', 'ТМ', '0.5')
        
        result = None
        
        cls._reset_daily_pr_stats()
        
        if pr_data in (None, 'closed'):
            return
        
        data = SafeJson.load(PATH.PR_TRACE)
        result = ''
        
        value, direction, fl = pr_data
        value = float(value)
        
        # for pr_key in ("DAILY", "GLOBAL"):
        plus_condition = (
            (kills > value and direction == 'ТБ'),
            (kills < value and direction == 'ТМ')
            ) 
            
        if any(plus_condition):
            data["DAILY"][f"{direction} (FL {fl})"][0] += 1
            data["GLOBAL"][f"{direction} (FL {fl})"][0] += 1
            result = 'plus'
        else:
            data["DAILY"][f"{direction} (FL {fl})"][1] += 1
            data["GLOBAL"][f"{direction} (FL {fl})"][1] += 1
            result = 'minus'
        
        SafeJson.dump(json_path=PATH.PR_TRACE, data=data)
        logger.info(f"PR result saving done")
        
        return result