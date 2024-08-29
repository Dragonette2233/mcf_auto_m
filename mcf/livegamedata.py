import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from mcf.ssim_recognition import ScoreRecognition
from mcf import autogui
from mcf.dynamic_data import CF
import time

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
        print('Game not launched')

    # Проверяем успешность запроса
    if response.status_code != 200:
        exit(0)
        
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

    
    # # from modules.mcf_storage import MCFStorage
    

    # blue_shot = None
    # red_shot = None
    
    score = get_live_gamedata()

    towers_gold = ScoreRecognition.screen_score_recognition()
    
    score |= towers_gold    
    
    if score['red_towers'] == 0:
        autogui.click_on_tower((1752, 970, 936, 620))
        blue_t1_health = ScoreRecognition.towers_healh_recognition()
        if not blue_t1_health or blue_t1_health > CF.LD.twh_blue:
            blue_t1_health = CF.LD.twh_blue
        else:
            CF.LD.twh_blue = blue_t1_health
    else:
        blue_t1_health = 0

    if score['blue_towers'] == 0:
        autogui.click_on_tower((1811, 919, 951, 490))
        red_t1_health = ScoreRecognition.towers_healh_recognition()
        if not red_t1_health or red_t1_health > CF.LD.twh_red:
            red_t1_health = CF.LD.twh_red
        else:
            CF.LD.twh_red = red_t1_health
    else:
        red_t1_health = 0
    
    score['blue_t1_hp'] = blue_t1_health
    score['red_t1_hp'] = red_t1_health

    # MCFStorage.save_score(score=score)

    return score