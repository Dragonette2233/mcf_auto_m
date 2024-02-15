import os
import threading
import getpass
from modules import (
    mcf_pillow,
)

"""
    Values for interacting with League of Legends data

"""
ALL_CHAMPIONS_IDs = {
    1: 'Annie', 2: 'Olaf', 3: 'Galio', 4: 'TwistedFate',
    5: 'XinZhao', 6: 'Urgot', 7: 'LeBlanc', 8: 'Vladimir',
    9: 'Fiddlesticks', 10: 'Kayle', 11: 'MasterYi',
    12: 'Alistar', 13: 'Ryze', 14: 'Sion', 15: 'Sivir',
    16: 'Soraka', 17: 'Teemo', 18: 'Tristana', 19: 'Warwick',
    20: 'Nunu', 21: 'MissFortune', 22: 'Ashe', 23: 'Tryndamere',
    24: 'Jax', 25: 'Morgana', 26: 'Zilean', 27: 'Singed',
    28: 'Evelynn', 29: 'Twitch', 30: 'Karthus', 31: "ChoGath",
    32: 'Amumu', 33: 'Rammus', 34: 'Anivia', 35: 'Shaco',
    36: 'DrMundo', 37: 'Sona', 38: 'Kassadin', 39: 'Irelia', 
    40: 'Janna', 41: 'Gangplank', 42: 'Corki', 43: 'Karma',
    44: 'Taric', 45: 'Veigar', 48: 'Trundle', 50: 'Swain',
    51: 'Caitlyn', 53: 'Blitzcrank', 54: 'Malphite', 55: 'Katarina', 
    56: 'Nocturne', 57: 'Maokai', 58: 'Renekton', 59: 'JarvanIV', 
    60: 'Elise', 61: 'Orianna', 62: 'Wukong', 63: 'Brand',
    64: 'LeeSin', 67: 'Vayne', 68: 'Rumble', 69: 'Cassiopeia',
    72: 'Skarner', 74: 'Heimerdinger', 75: 'Nasus', 76: 'Nidalee',
    77: 'Udyr', 78: 'Poppy', 79: 'Gragas', 80: 'Pantheon',
    81: 'Ezreal', 82: 'Mordekaiser', 83: 'Yorick', 84: 'Akali',
    85: 'Kennen', 86: 'Garen', 89: 'Leona', 90: 'Malzahar',
    91: 'Talon', 92: 'Riven', 96: "KogMaw", 98: 'Shen',
    99: 'Lux', 101: 'Xerath', 102: 'Shyvana', 103: 'Ahri',
    104: 'Graves', 105: 'Fizz', 106: 'Volibear', 107: 'Rengar',
    110: 'Varus', 111: 'Nautilus', 112: 'Viktor', 113: 'Sejuani',
    114: 'Fiora', 115: 'Ziggs', 117: 'Lulu', 119: 'Draven',
    120: 'Hecarim', 121: "KhaZix", 122: 'Darius', 126: 'Jayce',
    127: 'Lissandra', 131: 'Diana', 133: 'Quinn', 134: 'Syndra',
    136: 'AurelionSol', 141: 'Kayn', 142: 'Zoe', 143: 'Zyra',
    145: "KaiSa", 147: "Seraphine", 150: 'Gnar', 154: 'Zac',
    157: 'Yasuo', 161: "VelKoz", 163: 'Taliyah', 166: "Akshan",
    164: 'Camille', 200: "BelVeth", 201: 'Braum', 202: 'Jhin',
    203: 'Kindred', 221: 'Zeri', 222: 'Jinx', 223: "TahmKench", 233: "Briar",
    234: 'Viego', 235: 'Senna', 236: 'Lucian', 238: 'Zed',
    240: 'Kled', 245: 'Ekko', 246: 'Qiyana', 254: 'Violet',
    266: 'Aatrox', 267: 'Nami', 268: 'Azir', 350: 'Yuumi',
    360: 'Samira', 412: 'Thresh', 420: 'Illaoi', 421: "RekSai",
    427: 'Ivern', 429: 'Kalista', 432: 'Bard', 497: 'Rakan',
    498: 'Xayah', 516: 'Ornn', 517: 'Sylas', 526: 'Rell',
    518: 'Neeko', 523: 'Aphelios', 555: 'Pyke', 875: "Sett",
    711: "Vex", 777: "Yone", 887: "Gwen", 876: "Lillia",
    888: "Renata", 895: "Nilah", 897: "KSante", 901: "Smolder", 902: "Milio", 950: "Naafiri", 
    2002: 'Kayn_b', 910: "Hwei",
    2001: "MonkeyKing"
}

ten_roles_dict = {

    '0': ('Aatrox', 'Belveth', 'Camille', 'Darius', 'Fiora', 'Gwen', 'Illaoi', 'Irelia', 'Kayn', 
           'Leesin', 'Renekton', 'Viego', 'Sett', 'Hecarim', 'Mordekaiser', 'Riven', 'Violet', # Vi is Violet
           'Kled', 'Warwick', 'Naafiri'),
    '1': ('Swain', 'Sylas', 'Jax', 'Yone', 'Yasuo', 'Trundle', 'Xinzhao', 'Graves', 'Monkeyking',
           'Tryndamere', 'Gnar', 'Wukong', 'Olaf', 'Nasus'),
    '2': ('Akali', 'Kassadin', 'Masteryi', 'Rengar', 'Khazix', 'Evelynn', 'Talon', 'Zed', 'Nocturne',
           'Qiyana', 'Katarina', 'Pyke', 'Samira', 'Briar'),
    '3': ('Azir', 'Cassiopeia', 'Lillia', 'Ryze', 'Viktor',  'Ekko', 'Gangplank', 'Anivia', 'Heimerdinger', 
           'Vladimir', 'Fiddlesticks', 'Kennen',  'Aurelionsol', 'Gragas', 'Ahri', 'Hwei'),
    '4': ('Bard', 'Janna', 'Karma', 'Lulu', 'Maokai', 'Morgana', 'Nami', 'Orianna', 'Rakan', 'Renata', 'Senna', 
           'Seraphine', 'Sona', 'Soraka', 'Twistedfate', 'Yuumi', 'Zilean', 'Ivern',  'Yorick', 'Annie', 'Milio'),
    '5': ('Akshan', 'Aphelios', 'Caitlyn', 'Jhin', 'Jinx', 'Kaisa', 'Kalista', 'Kayle', 'Kindred', 
           'Kogmaw', 'Lucian', 'Missfortune', 'Sivir', 'Tristana', 'Twitch', 'Vayne', 'Xayah', 
           'Zeri', 'Draven', 'Quinn', 'Nilah', 'Smolder'),
    '6':('Syndra', 'Velkoz', 'Xerath', 'Ziggs', 'Zoe', 'Corki', 'Ashe', 'Karthus', 'Malzahar', 'Lux', 'Zyra',
          'Brand', 'Taliyah', 'Vex', 'Shaco', 'Teemo',),
    '7': ('Lissandra', 'Nidalee', 'Neeko', 'Nunu', 'Varus', 'Veigar', 'Pantheon', 'Rumble', 'Shyvana',  
           'Reksai', 'Diana', 'Jayce', 'Elise', 'Malphite', 'Leblanc', 'Jarvaniv', 'Fizz', 'Ezreal',),
    '8': ('Drmundo', 'Galio', 'Garen', 'Ornn', 'Poppy', 'Sion', 'Udyr', 'Ksante', 'Singed',
           'Urgot', 'Volibear'),
    '9': ('Alistar', 'Amumu', 'Braum', 'Leona', 'Nautilus', 'Shen', 'Tahmkench', 'Thresh', 'Skarner',
           'Zac', 'Blitzcrank', 'Rammus', 'Sejuani', 'Chogath', 'Rell', 'Taric')

}


WINDOWS_USER = getpass.getuser()
SPECTATOR_MODE = 'spectator.{reg}.lol.pvp.net:8080'
FEATURED_GAMES_URL = "https://{region}.api.riotgames.com/lol/spectator/v4/featured-games"
URL_PORO_BY_REGIONS = "https://porofessor.gg/current-games/{champion}/{region}/queue-450"
URL_PORO_ADVANCE = "https://porofessor.gg/current-games/{champion}/{region}/bronze/queue-450"

REGIONS_TUPLE = (
    ('br', 'br1', 'americas'), ('lan', 'la1', 'americas'),
    ('na', 'na1', 'americas'), ('las', 'la2', 'americas'),
    ('oce', 'oc1', 'sea'), ('eune', 'eun1', 'europe'),
    ('tr', 'tr1', 'europe'), ('ru', 'ru', 'europe'),
    ('euw', 'euw1', 'europe'), ('kr', 'kr', 'asia'), 
    ('jp', 'jp1', 'asia'), ('vn', 'vn2', 'sea'),
    ('sg', 'sg2', 'sea'), ('ph', 'ph2', 'sea'),
    ('th', 'th2', 'sea'), ('tw', 'tw2', 'sea')
)

"""
    All pathes for app images
    
"""

MCF_BOT_PATH = os.environ.get('MCF_BOT')
JSON_GAMEDATA_PATH = os.path.join(MCF_BOT_PATH, 'mcf_lib', 'GameData.json')
SCREEN_GAMESCORE_PATH = os.path.join(MCF_BOT_PATH, 'images_lib', 'gamescore_PIL.png')
SPECTATOR_FILE_PATH = os.path.join(MCF_BOT_PATH, 'mcf_lib', 'spectate.bat')
STATISTICS_PATH = os.path.join(MCF_BOT_PATH, 'mcf_lib', 'stats_27.txt')

# SCREENSHOT_FILE_PATH = os.path.join(MCF_BOT_PATH, 'images_lib', 'screenshot_PIL.png')


"""
    Data for screen score recognizing (Time, kills, towers)

"""

GTIME_DATA_PATH = os.path.join(MCF_BOT_PATH, 'ssim_score_data', 'gametime')
BLUE_SCORE_PATH = os.path.join(MCF_BOT_PATH, 'ssim_score_data', 'team_blue', 'score_{pos}')
RED_SCORE_PATH =  os.path.join(MCF_BOT_PATH, 'ssim_score_data', 'team_red', 'score_{pos}')
BLUE_TOWER_PATH = os.path.join(MCF_BOT_PATH, 'ssim_score_data', 'team_blue', 'towers')
RED_TOWER_PATH = os.path.join(MCF_BOT_PATH, 'ssim_score_data', 'team_red', 'towers')
DEBUG_STATS_PATH = os.path.join(MCF_BOT_PATH, 'arambot_lib', 'debug_stats.json')
BLUE_CUT_PATH = os.path.join('.', 
                        'images_lib', 
                        'chars',  
                        'blue', 'char_{indx}.png')
RED_CUT_PATH = os.path.join('.', 
                        'images_lib', 
                        'chars', 
                        'red', 'char_{indx}.png')

BLUEPATH_IMAGES_TO_COMPARE = {
    char: os.path.join('.', 
                        'images_lib', 
                        'chars', 
                        'origin', 
                        'blue', f'{char.lower().capitalize()}.png') 
                        for char in ALL_CHAMPIONS_IDs.values()
    }
REDPATH_IMAGES_TO_COMPARE = {
    char: os.path.join('.', 
                        'images_lib', 
                        'chars', 
                        'origin', 
                        'red', f'{char.lower().capitalize()}.png') 
                        for char in ALL_CHAMPIONS_IDs.values()
    }
BLUE_GREYSHADE_ARRAY = {
            char: mcf_pillow.greyshade_array(img) for char, img in BLUEPATH_IMAGES_TO_COMPARE.items()
}
RED_GREYSHADE_ARRAY = {
            char: mcf_pillow.greyshade_array(img) for char, img in REDPATH_IMAGES_TO_COMPARE.items()
}

# GREYSHADE_CMP_MAP = mcf_pillow.greyshade_array(os.path.join('.', 'mcf_lib', 'cmp_map.png'))
GREYSHADE_CMP_RIOT = mcf_pillow.greyshade_array(os.path.join('.', 'mcf_lib', 'cmp_riot.png'))
GREYSHADE_CMP_BLUE = mcf_pillow.greyshade_array(os.path.join('.', 'mcf_lib', 'cmp_blue.png'))
GREYSHADE_CMP_RED = mcf_pillow.greyshade_array(os.path.join('.', 'mcf_lib', 'cmp_red.png'))

"""
    Classes for finded game and switches for controling threads and activity 

"""

class MCFException(Exception): ...
class MCFTimeoutError(Exception): ...
class MCFNoConnectionError(Exception): ...
class MCFThread(threading.Thread):
    def __init__(self, func, args=False):
        super().__init__()
        self._target = func
        self.daemon = True
        self.name = f"{func.__name__}-Thr"
        if args:
            self._args = args

class Validator:
    # active_mel_mirror = False
    # ahead_end = False
    quick_end = False
    findgame = 0
    gametime = False
    recognition = 0
    ended_game_characters = None
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

class Switches:
    coeff_opened = False
    request = False
    timer = None
    bot_activity = False
    predicted_total = False
    predicted_winner = False

class StatsRate:
    blue_rate: tuple[str] = None
    red_rate: tuple[str] = None
    tb_rate: tuple[str] = None
    tl_rate: tuple[str] = None
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


class TGsymbols:
    blue_square: str = ''
    green_square: str = ''


cookies = {
        'auid': 'LY0LGGVJT9xF3cMHBakaAg==',
        'SESSION': '22fdb02ab99445348a011c35f47c6452',
        'lng': 'ru',
        '_cfvwab': '-1',
        'cookies_agree_type': '3',
        'tzo': '3',
        'is12h': '0',
        'che_g': '3c2afae5-894d-df7a-91d5-ba2642fb4db5',
        'sh.session.id': '798cfbe4-33cb-434c-affa-b0862a224c4f',
        '_ga': 'GA1.1.368426760.1699302170',
        '_ym_uid': '1699731283765603681',
        '_ym_d': '1699731283',
        '_ym_isad': '1',
        '_ga_7JGWL9SV66': 'GS1.1.1699729869.10.1.1699731302.34.0.0',
        'ggru': '188',
        'platform_type': 'mobile',
        '_ga_0NQW4X2MPH': 'GS1.1.1699731283.1.1.1699737050.59.0.0',
        'window_width': '802',
    }

headers = {
    'authority': 'lite.1xbet-new.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
}

riot_headers = {
        'headers': { "X-Riot-Token": open('APIKEY', 'r').read().strip() },
        'timeout': 3
    }
poro_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36" }