from mcf.asbstract import BoolSwitch, Singleton, gData

class StatsRate:
    def __init__(self) -> None:
        self.blue_characters = ''
        self.red_characters = ''

        self.blue_roles = None
        self.red_roles = None

        self.blue_rate: list[str] = [0, '']
        self.red_rate: list[str] = [0, '']
        self.tb_rate: list[str] = [0, '']
        self.tl_rate: list[str] = [0, '']
        self.games_all: int = 0
        self.games_totals: int = 0

        self.WINNER = '🟩'
        self.LOSER = '🟥'

    def calculate(self, team_blue, team_red):
        from mcf import stats_by_roles
        stats_result = stats_by_roles.get_aram_statistic(
                blue_entry=team_blue,
                red_entry=team_red,
            )
       
        self.blue_characters = ' '.join(team_blue)
        self.red_characters = ' '.join(team_red)
        self.blue_roles = stats_result['blue_roles']
        self.red_roles = stats_result['red_roles']
        self.blue_rate = stats_result['w1']
        self.red_rate = stats_result['w2']
        self.tb_rate = stats_result['tb']
        self.tl_rate = stats_result['tl']
        self.games_all = stats_result['all_m']
        self.games_totals = stats_result['all_ttl']
    
    def is_stats_avaliable(self):
        if self.games_all != 0:
            return True
    
    def _reset(self):
        self.games_all = 0
        self.games_totals = 0
        self.blue_roles = None
        self.red_roles = None

    def win_blue_accepted(self):
        if (self.games_all != 0) and (self.blue_rate[1] == self.WINNER):
            return True
        
    def win_red_accepted(self):
        if (self.games_all != 0) and (self.red_rate[1] == self.WINNER):
            return True

    def tanks_in_teams(self, one_side=False, both_excluded=False):
        if self.games_all == 0:
            return

        tank_in_blue = '8' in self.blue_roles or '9' in self.blue_roles
        tank_in_red = '8' in self.red_roles or '9' in self.red_roles

        if one_side:
            return tank_in_blue or tank_in_red
        
        if both_excluded:
            return not tank_in_blue and not tank_in_red
        
        return tank_in_blue and tank_in_red

    def tb_accepted(self):
        if (self.games_all != 0) and (self.tb_rate[1] == self.WINNER):
            return True
                    
    def tl_accepted(self):
        if (self.games_all != 0) and (self.tl_rate[1] == self.WINNER):
            return True

class ActiveGameData(gData):
    def __init__(self) -> None:
        self.cache_parse = None
        self.nick_region: str = None
        self.region: str = None
        self.area: str = None
        self.puuid: str = None
        self.blue_chars = None
        self.red_chars = None
        self.finded_chars = None
        self.match_id: str = None
        self.is_game_founded: bool = False
        self.encryptionKey: str = None
        
    def save(self, data: tuple) -> None:
        
        """
            Saving data from activegame which founded from mel-stream.\n
            `data` args position ( blue_chars, red_chars, nick_region, encryptionKey, is_game_founded )
        
        """
        attributes = ['blue_chars', 
                      'red_chars', 
                      'nick_region', 
                      'encryptionKey', 
                      'is_game_founded']
        
        # Присваиваем данные атрибутам
        
        for attr, value in zip(attributes, data):
            setattr(self, attr, value)
    
    def _reset(self):
        for attr in vars(self):
            setattr(self, attr, None)

class EndedGameData(gData):
    def __init__(self) -> None:
        self.blue_chars = None
        self.red_chars = None
        self.kills = None
        self.time = None
        self.winner = None
    
    def is_ended(self):
        if self.blue_chars:
            return True
    
    def extract(self) -> tuple:
        """
            Extracting data from game which ended with remake.\n
            :return `tuple`: args position ( winner, kills, time )
        
        """
        return (self.winner, self.kills, self.time)
    
    def save(self, data: tuple):
        
        """
            Saving data from game which ended with remake.\n
            `data` args position ( blue_chars, red_chars, kills, winner, time )
        
        """
        attributes = ['blue_chars', 'red_chars', 'kills', 'winner', 'time']
        
        # Присваиваем данные атрибутам
        
        for attr, value in zip(attributes, data):
            setattr(self, attr, value)
        
    def _reset(self):
        for attr in vars(self):
            setattr(self, attr, None)

class Switches():
    def __init__(self) -> None:
        self.coeff_opened = BoolSwitch()
        self.request = BoolSwitch()
        self.cache_done = BoolSwitch()
        self.tracer = BoolSwitch()
        self.quick_end = BoolSwitch()
        self.loop = BoolSwitch()
        self.total_diff = BoolSwitch()
    
    def _reset(self):
        for switch_name in self.__dict__:
            switch: BoolSwitch = getattr(self, switch_name)
            switch.deactivate()

class LiveData(gData):
    def __init__(self) -> None:
        self.tw_health_T1 = {
            'blue': 100,
            'red': 100
        }
        self.tw_health_T2 = {
            'blue': 100,
            'red': 100
        }
        
        self.tw_blue = 0
        self.tw_red = 0
        
        self.gold_blue = 10.0
        self.gold_red = 10.0

    def _reset(self):
        self.tw_health_T1['blue'] = 100
        self.tw_health_T1['red'] = 100
        self.tw_health_T2['blue'] = 100
        self.tw_health_T2['red'] = 100
        
        self.tw_blue = 0
        self.tw_red = 0
        self.gold_blue = 10.0
        self.gold_red = 10.0

class Validator(gData):
    def __init__(self) -> None:
        self.pr_cache: tuple = None
        self.pr_track: list = []
        self.findgame = 0
        self.recognition = 0
        self.tb_approve = 0
        self.tl_approve = 0

    def _reset(self):
        self.pr_cache = None
        self.pr_track.clear()
        self.findgame = 0
        self.recognition = 0
        self.tb_approve = 0
        self.tl_approve = 0

class ControlFlow(Singleton):
    def init(self) -> None:
        super().__init__()
        self.SW = Switches()
        self.VAL = Validator()
        self.ACT = ActiveGameData()
        self.LD = LiveData()
        self.END = EndedGameData()
        self.SR = StatsRate()
        
    def reset(self):
        self.SW._reset()
        self.VAL._reset()
        self.END._reset()
        self.LD._reset()
        self.ACT._reset()
        self.SR._reset()

CF = ControlFlow()