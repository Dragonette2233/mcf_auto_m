import urllib3
import logging
import requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from mcf.api import cmouse
from mcf.dynamic import CF
from mcf.ssim_recognition import ScoreRecognition

logger = logging.getLogger(__name__)

def process_structure_health(score: dict, teams: tuple, click_coords_t1: tuple, click_coords_t2: tuple) -> tuple:
    
    """
        This function returns current health of tower or inhibitor (in the dev).
        
        :params score: dict with current scoredata
        :params teams: current team tw health require and opossite team. Example ('blue', 'red')
        :params click_coords: coords X, Y where mouse clicking to get tower health

    Returns:
        `tuple` of towers health (t1_health, t2_health)
    """
    
    
    if score[f'{teams[0]}_towers'] == 0:
        t2_health = 100
        cmouse.click_on_tower(click_coords_t1)
        t1_health = ScoreRecognition.towers_healh_recognition()
        if not t1_health or t1_health > CF.LD.tw_health_T1[teams[1]]:
            t1_health = CF.LD.tw_health_T1[teams[1]]
        else:
            CF.LD.tw_health_T1[teams[1]] = t1_health
            
    elif score[f'{teams[0]}_towers'] == 1:
        CF.LD.tw_health_T1[teams[1]] = 0
        t1_health = 0
        cmouse.click_on_tower(click_coords_t2)
        t2_health = ScoreRecognition.towers_healh_recognition()
        if not t2_health or t2_health > CF.LD.tw_health_T2[teams[1]]:
            t2_health = CF.LD.tw_health_T2[teams[1]]
        else:
            CF.LD.tw_health_T2[teams[1]] = t2_health
    else:
        CF.LD.tw_health_T2[teams[1]] = 0
        t1_health = 0
        t2_health = 0
    
    return (t1_health, t2_health)

def get_live_gamedata() -> dict:
    
    """
        Return gamedata from Live Game Data API
        
        time, kills
    """
    
    url = "https://127.0.0.1:2999/liveclientdata/allgamedata"

    # Выполняем GET запрос
    try:
        response = requests.get(url, verify=False)
    except requests.exceptions.ConnectionError:
        logger.error("Game crashed!")
        return False
        # TG NOTIFICATION

    # Проверяем успешность запроса
    # if response.status_code != 200:
    #     exit(0)
        
    data = response.json()
    blue_kills = 0
    red_kills = 0
    time_nix = int(data['gameData']['gameTime'])
    # time_divmod = divmod(int(time_nix), 60)
    # time_repr = f"{time_divmod[0]:02}:{time_divmod[1]:02}"

    for i in data['allPlayers'][0:5]:
        blue_kills += i['scores']['kills']
        
    for i in data['allPlayers'][5:]:
        red_kills += i['scores']['kills']
    
    
    # turrets_red = {
    #     'Turret_T1_C_07_A': 0,
    #     "Turret_T1_C_08_A": 0,
    #     'Turret_T1_C_09_A': 0,
    #     'Turret_T1_C_10_A': 0,
        
    # }

    # turrets_blue = {
    #     'Turret_T2_L_01_A': 0,    
    #     'Turret_T2_L_02_A': 0,    
    #     'Turret_T2_L_03_A': 0,    
    #     'Turret_T2_L_04_A': 0,
    # }

    
    # for e in data['events']['Events']:
    #     if e['EventName'] == 'TurretKilled':
    #         print(e['TurretKilled'])
    #         if turrets_red.get(e['TurretKilled']) == 0:
    #             turrets_red[e['TurretKilled']] = 1
    #         elif turrets_blue.get(e['TurretKilled']) == 0:
    #             turrets_blue[e['TurretKilled']] = 1
                
    return {
        'time': int(time_nix),
        'blue_kills': int(blue_kills),
        'red_kills': int(red_kills),
        # 'blue_towers': sum(turrets_red.values()),
        # 'red_towers': sum(turrets_blue.values())
    }
    
def generate_scoreboard() -> dict[str, int]:
    
    score = get_live_gamedata()
    
    # Возвращаем False для перезапуска игры если она крашнулась
    if not score:
        return score
    
    towers_gold = ScoreRecognition.screen_score_recognition()
    score |= towers_gold    
    
    # Бэкап значений blue_gold и red_gold в CF.LD
    if score['blue_gold'] > CF.LD.gold_blue:
        CF.LD.gold_blue = score['blue_gold']
    else:
        # Проверка, что значение blue_gold не упало
        score['blue_gold'] = CF.LD.gold_blue

    if score['red_gold'] > CF.LD.gold_red:
        CF.LD.gold_red = score['red_gold']
    else:
        # Проверка, что значение red_gold не упало
        score['red_gold'] = CF.LD.gold_red
    
    
    blue_t1_health, blue_t2_health = process_structure_health(score, 
                                                           teams=('red', 'blue'),
                                                           click_coords_t1=(1752, 970, 936, 620,),
                                                           click_coords_t2=(1730, 993, 956, 493,))    
    red_t1_health, red_t2_health = process_structure_health(score, 
                                                         teams=('blue', 'red'),
                                                         click_coords_t1=(1811, 919, 951, 490,),
                                                         click_coords_t2=(1833, 892, 934, 543,))
    
    score['blue_t1_hp'] = blue_t1_health
    score['red_t1_hp'] = red_t1_health
    score['blue_t2_hp'] = blue_t2_health
    score['red_t2_hp'] = red_t2_health

    return score