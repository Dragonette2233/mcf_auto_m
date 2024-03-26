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



class Validator:
    tracer = {
        "300s": False,
        "420s": False,
        "540s": False
    }

    # predicts_value_flet[key] = [98.5, 'Б', '0.5']

    predict_value_flet = {
        'main': None,
        'stats': None,
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