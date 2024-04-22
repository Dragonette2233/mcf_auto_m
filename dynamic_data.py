from mcf_asbstract import BoolSwitch, Singleton
from typing import Any

class ActiveGameData():
    def __init__(self) -> None:
        self.cache_parse = None
        self.nick_region = None
        self.region = None
        self.area = None
        self.puuid = None
        self.blue_team = None
        self.red_team = None
        self.finded_chars = None
        self.match_id = None
        self.is_game_founded = False
        self.encryptionKey = None

    def _reset(self):
        for attr in vars(self):
            setattr(self, attr, None)

class EndedGameData():
    def __init__(self) -> None:
        self.blue_chars = None
        self.red_chars = None
        self.kills = None
        self.time = None
        self.winner = None
    
    def _reset(self):
        for attr in vars(self):
            setattr(self, attr, None)

class Switches():
    def __init__(self) -> None:
        self.coeff_opened = BoolSwitch()
        self.request = BoolSwitch()
        self.cache_done = BoolSwitch()
        self.tracer = BoolSwitch()
        # self.active_mel_mirror = BoolSwitch()
        self.quick_end = BoolSwitch()
        self.loop = BoolSwitch()
    
    def _reset(self):
        for switch_name in self.__dict__:
            switch: BoolSwitch = getattr(self, switch_name)
            switch.deactivate()

class TowersHealth:
    def __init__(self) -> None:     
        self.blue_backup = 100
        self.red_backup = 100

    def _reset(self):
        self.blue_backup = 100
        self.red_backup = 100

class Validator():
    def __init__(self) -> None:
        self.pr_cache: dict[str, tuple] = {
            'main': None,
            'stats': None,
        }
        self.pr_debug: dict[str, int] = {
            'main': 0,
            'stats': 0
        }
        self.findgame = 0
        self.recognition = 0

    def _reset(self):
        self.pr_cache['main'] = None
        self.pr_cache['stats'] = None
        self.pr_debug['main'] = 0
        self.pr_debug['stats'] = 0
        self.findgame = 0
        self.recognition = 0

class ControlFlow(Singleton):
    def init(self) -> None:
        super().__init__()
        self.SW = Switches()
        self.VAL = Validator()
        self.END = EndedGameData()
        self.ACT = ActiveGameData()
        self.TW_HP = TowersHealth()
        
    def reset(self):
        self.SW._reset()
        self.VAL._reset()
        self.END._reset()
        self.TW_HP._reset()
        self.ACT._reset()
    # sw = Switches()

class StatsRate:
    blue_roles = None
    red_roles = None

    blue_rate: list[str] = [0, '']
    red_rate: list[str] = [0, '']
    tb_rate: list[str] = [0, '']
    tl_rate: list[str] = [0, '']
    games_all: int = 0
    games_totals: int = 0

    WINNER = '🟩'
    LOSER = '🟥'

    @classmethod
    def calculate(cls, team_blue, team_red):
        from modules import stats_by_roles
        stats_result = stats_by_roles.get_aram_statistic(
                blue_entry=team_blue,
                red_entry=team_red,
            )
        if stats_result is not None:
            cls.blue_roles = stats_result['blue_roles']
            cls.red_roles = stats_result['red_roles']
            cls.blue_rate = stats_result['w1']
            cls.red_rate = stats_result['w2']
            cls.tb_rate = stats_result['tb']
            cls.tl_rate = stats_result['tl']
            cls.games_all = stats_result['all_m']
            cls.games_totals = stats_result['all_ttl']
    
    @classmethod
    def is_stats_avaliable(cls):
        if cls.games_all != 0:
            return True
    
    @classmethod
    def stats_clear(cls):
        cls.games_all = 0

    @classmethod
    def win_blue_accepted(cls):
        if (cls.games_all != 0) and (cls.blue_rate[1] == cls.WINNER):
            return True
        
    @classmethod
    def win_red_accepted(cls):
        if (cls.games_all != 0) and (cls.red_rate[1] == cls.WINNER):
            return True

    @classmethod
    def tanks_in_teams(cls, one_side=False, both_excluded=False):
        if cls.games_all == 0:
            return

        tank_in_blue = '8' in cls.blue_roles or '9' in cls.blue_roles
        tank_in_red = '8' in cls.red_roles or '9' in cls.red_roles

        if one_side:
            return tank_in_blue or tank_in_red
        
        if both_excluded:
            return not tank_in_blue and not tank_in_red
        
        return tank_in_blue and tank_in_red

    @classmethod
    def tb_accepted(cls):
        if (cls.games_all != 0) and (cls.tb_rate[1] == cls.WINNER):
            return True
                    
    @classmethod
    def tl_accepted(cls):
        if (cls.games_all != 0) and (cls.tl_rate[1] == cls.WINNER):
            return True