class TowersHealth:
    blue_backup = 100
    red_backup = 100

    @classmethod
    def reset(cls):
        cls.blue_backup = 0
        cls.red_backup = 0
        
class ActiveGame:
    cached_parse = None
    
    nick_region = None
    region = None
    area = None
    puuid = None
    blue_team = None
    red_team = None
    match_id = None
    is_game_founded = False
    encryptionKey = None

    @classmethod
    def refresh(cls):
        cls.nick_region = None
        cls.blue_team = None
        cls.red_team = None
        cls.region: str = None
        cls.puuid = None
        cls.area = None
        cls.match_id = None
        cls.is_game_founded = False
        cls.encryptionKey = None

class Switches:
    coeff_opened = False
    request = False
    cache_done = False

class Validator:
    tracer = False

    # predicts_value_flet[key] = [98.5, 'Б', '0.5']

    predict_value_flet = {
        'main': None,
        'stats': None,
    }
    predicts_debug = {
        'main': None,
        'stats': None
    }
    active_mel_mirror = False
    quick_end = False
    findgame = 0
    loop = False
    recognition = 0
    ended_blue_characters = None
    ended_red_characters = None
    ended_kills = None
    ended_time = None
    ended_winner = None
    finded_game_characerts = None
    stats_register = {
        'W1_res': 0,
        'W2_res': 0,
        'W1_pr': 0,
        'W2_pr': 0,
    }
    total_register = {
        'W1_res': 0,
        'W2_res': 0,
        'W1_pr': 0,
        'W2_pr': 0,
    }

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
    def tanks_in_teams(cls, one_side=False):
        if cls.games_all == 0:
            return

        tank_in_blue = '8' in cls.blue_roles or '9' in cls.blue_roles
        tank_in_red = '8' in cls.red_roles or '9' in cls.red_roles

        if one_side:
            return tank_in_blue or tank_in_red
        
        return tank_in_blue and tank_in_red

    @classmethod
    def tb_accepted(cls):
        if (cls.games_all != 0) and (cls.tb_rate[1] == cls.WINNER):
            return True
                    
    @classmethod
    def tl_accepted(cls):
        if (cls.games_all != 0) and (cls.tl_rate[1] == cls.WINNER):
            return True