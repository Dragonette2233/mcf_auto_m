class ActiveGame:
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