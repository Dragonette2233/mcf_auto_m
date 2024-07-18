import os
import threading
import getpass
from datetime import datetime
from modules import mcf_pillow

"""
    Values for interacting with League of Legends data

"""

RISK_AREA_CHARACTERS = (
    'Sion', 'Viego', 'Shaco', 'Teemo'
)

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
    888: "Renata", 893: "Aurora", 895: "Nilah", 897: "KSante", 901: "Smolder", 902: "Milio", 950: "Naafiri", 
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
           'Vladimir', 'Fiddlesticks', 'Kennen',  'Aurelionsol', 'Gragas', 'Ahri', 'Hwei', 'Aurora'),
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
TRACE_RANGE = range(360, 420)
TODAY = datetime.now().day
SPECTATOR_MODE = 'spectator.{reg}.lol.pvp.net:8080'
FEATURED_GAMES_URL = "https://{region}.api.riotgames.com/lol/spectator/v5/featured-games"
URL_PORO_BY_REGIONS = "https://porofessor.gg/current-games/{champion}/{region}/queue-450"
URL_PORO_ADVANCE = "https://porofessor.gg/current-games/{champion}/{region}/{elo}/queue-450"

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

class CSS:
    # BTN_STREAM = 'button.ui-dashboard-game-button.dashboard-game-action-bar__item'
    BTN_REJECT_LIVE = 'button.ui-button.dashboard-redirect-message-timer__btn.ui-button--size-m.ui-button--theme-gray.ui-button--rounded'
    # BTN_FOR_BET = 'li.ui-dashboard-champ.dashboard-champ.dashboard__champ.ui-dashboard-champ--theme-gray'
    TABLE_GAMES = 'li.ui-dashboard-champ.dashboard-champ.dashboard__champ.ui-dashboard-champ--theme-gray'
    GAMELINK = 'a.dashboard-game-block__link.dashboard-game-block-link'
    SPAN_BTN_STREAM = 'span.dashboard-game-action-bar__group'
    OBJ_BTN_STREAM = 'button.ui-dashboard-game-button.dashboard-game-action-bar__item'
    TITLE_ARAM_OUTER = 'span.caption.ui-dashboard-champ-name__caption.caption--size-m'
    

class MelSelenium:
    ...

class URL:

    FEATURED_GAMES = "https://{region}.api.riotgames.com/lol/spectator/v5/featured-games"
    PORO_BY_REGIONS = "https://porofessor.gg/current-games/{champion}/{region}/queue-450"
    PORO_ADVANCE = "https://porofessor.gg/current-games/{champion}/{region}/{elo}/queue-450"


class PATH:
    
    """
        All pathes for app images

    """

    MCF_BOT: str = os.environ.get('MCF_BOT')
    JSON_GAMEDATA = os.path.join(MCF_BOT, 'untracking', 'GameData.json')
    SCREEN_GAMESCORE = os.path.join(MCF_BOT, 'images_lib', 'gamescore_PIL.png')
    SPECTATOR_FILE = os.path.join(MCF_BOT, 'mcf_lib', 'spectate.bat')
    STATISTICS = os.path.join(MCF_BOT, 'mcf_lib', 'stats_59.txt')

    """
        Untracking pathes

    """
    JSON_GAMEDATA = os.path.join(MCF_BOT, 'untracking', 'GameData.json')
    MIRROR_PAGE = os.path.join(MCF_BOT, 'untracking', 'mirror_page.txt')
    PREVIOUS_GAMEID = os.path.join(MCF_BOT, 'untracking', 'previous_gameid.txt')
    ACTIVE_GAMESCORE = os.path.join(MCF_BOT, 'untracking', 'activegame_score.json')
    SCORE_TRACE = os.path.join(MCF_BOT, 'untracking', 'score_trace.json')
    PREDICTS_TRACE_GLOBAL = os.path.join(MCF_BOT, 'untracking', 'predicts_trace.json')
    PREDICTS_TRACE_DAILY = os.path.join(MCF_BOT, 'untracking', 'predicts_trace_daily.json')

    SNIPPET_SCORE = os.path.join(MCF_BOT, 'mcf_lib', 'score_snip.txt')
    SNIPPET_GAMESTART = os.path.join(MCF_BOT, 'mcf_lib', 'tg_start_notification.txt')

    """
        Data for screen score recognizing (Time, kills, towers)

    """

    GTIME_DATA = os.path.join(MCF_BOT, 'ssim_score_data', 'gametime')
    BLUE_SCORE = os.path.join(MCF_BOT, 'ssim_score_data', 'team_blue', 'score_{pos}')
    RED_SCORE =  os.path.join(MCF_BOT, 'ssim_score_data', 'team_red', 'score_{pos}')
    BLUE_TOWER = os.path.join(MCF_BOT, 'ssim_score_data', 'team_blue', 'towers')
    RED_TOWER = os.path.join(MCF_BOT, 'ssim_score_data', 'team_red', 'towers')
    DEBUG_STATS = os.path.join(MCF_BOT, 'arambot_lib', 'debug_stats.json')
    
    TEMP_BLUE_CUT = [os.path.join('.', 
                                'images_lib', 
                                'chars', 
                                "blue",
                                f'char_{i}.png') for i in range(5)]
    
    TEMP_RED_CUT = [os.path.join('.', 
                                'images_lib', 
                                'chars', 
                                "red",
                                f'char_{i}.png') for i in range(5)]
    
    BLUE_CUT = os.path.join(MCF_BOT, 
                            'images_lib',
                            'chars',  
                            'blue', 'char_{indx}.png')
    RED_CUT = os.path.join(MCF_BOT, 
                            'images_lib', 
                            'chars', 
                            'red', 'char_{indx}.png')

    BLUE_IMAGES_TO_COMPARE = {
        char: os.path.join('.', 
                            'images_lib', 
                            'chars', 
                            'origin', 
                            'blue', f'{char.lower().capitalize()}.png') 
                            for char in ALL_CHAMPIONS_IDs.values()
        }
    RED_IMAGES_TO_COMPARE = {
        char: os.path.join('.', 
                            'images_lib', 
                            'chars', 
                            'origin', 
                            'red', f'{char.lower().capitalize()}.png') 
                            for char in ALL_CHAMPIONS_IDs.values()
        }
    
class GREYSHADE:

    BLUE_ARRAY = {
                char: mcf_pillow.greyshade_array(img) for char, img in PATH.BLUE_IMAGES_TO_COMPARE.items()
    }
    RED_ARRAY = {
                char: mcf_pillow.greyshade_array(img) for char, img in PATH.RED_IMAGES_TO_COMPARE.items()
    }

    # GREYSHADE_CMP_MAP = mcf_pillow.greyshade_array(os.path.join('.', 'mcf_lib', 'cmp_map.png'))
    CMP_RIOT = mcf_pillow.greyshade_array(os.path.join('.', 'mcf_lib', 'cmp_riot.png'))
    CMP_BLUE = mcf_pillow.greyshade_array(os.path.join('.', 'mcf_lib', 'cmp_blue.png'))
    CMP_RED = mcf_pillow.greyshade_array(os.path.join('.', 'mcf_lib', 'cmp_red.png'))
    mCMP_RIOT = mcf_pillow.greyshade_array(os.path.join('.', 'mcf_lib', 'mcmp_riot.png'))
    mCMP_BLUE = mcf_pillow.greyshade_array(os.path.join('.', 'mcf_lib', 'mcmp_blue.png'))
    mCMP_RED = mcf_pillow.greyshade_array(os.path.join('.', 'mcf_lib', 'mcmp_red.png'))
    mCMP_LOADING = mcf_pillow.greyshade_array(os.path.join('.', 'mcf_lib', 'mcmp_loading.png'))


class TelegramStr:
    FAILURE = '❌'
    SUCCESS = '✅'
    SHARK = '🐳'
    OCTUPUS = '🐙'
    GREEN_CIRCLE = '🟢'
    BLUE_CIRCLE = '🔵'
    RED_CIRCLE = '🔴'
    EXCLAM_RED = '❗️'
    EXCLAM_WHITE = '❕'
    ARROW_UP = '🔼'
    ARROW_DOWN = '🔽'
    CLOCK = '⏳'

    '''
        Telegram notifictations for predicts
    '''
    tb_predict_half = '{0}PR 110.5Б FL_0.5{0}'.format(ARROW_UP)
    tb_predict_full = '{0}PR 110.5Б FL_1{0}'.format(ARROW_UP)
    
    tl_predict_half = '{0}PR 110.5М FL_0.5{0}'.format(ARROW_DOWN)
    tl_predict_middle = '{0}PR 110.5М FL_0.75{0}'.format(ARROW_DOWN)
    tl_predict_full = '{0}PR 110.5М FL_1{0}'.format(ARROW_DOWN)

    '''
        Telegram notifications about ended game
        First argument - kills, second argument - time
    '''
    winner_blue = BLUE_CIRCLE + ' П1 -- {0} -- {1}'
    winner_red = RED_CIRCLE + ' П2 -- {0} -- {1}'
    winner_blue_opened = GREEN_CIRCLE + BLUE_CIRCLE + ' П1 -- {0} -- {1}'
    winner_red_opened = GREEN_CIRCLE + RED_CIRCLE + ' П2 -- {0} -- {1}'

    '''
        Telegram notification for started game
    '''
    SNIPPET_SCORE = open(PATH.SNIPPET_SCORE, 'r', encoding='utf-8').read()
    SNIPPET_GAMESTART = open(PATH.SNIPPET_GAMESTART, 'r', encoding='utf-8').read()

    game_founded = SUCCESS + ' {0}'
    game_not_founded = FAILURE + ' Игра не найдена'
    game_remake = FAILURE + ' Remake'

    events_opened = '\n\nTotal event {total_value}: ' + EXCLAM_WHITE + 'Opened'
    events_closed = '\n\nTotal event: ' + EXCLAM_RED + 'Closed'

    '''
        Only predicts message
    '''

    only_pr_message = open('untracking/only_pr_message.txt', 'r', encoding='utf-8').read()

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

class Headers:

    default = {
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

    riot = {
            'headers': { "X-Riot-Token": open('APIKEY', 'r').read().strip() },
            'timeout': 3
        }

COOKIES = {
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