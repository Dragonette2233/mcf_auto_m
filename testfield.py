import logging
import time
# from PIL import ImageGrab
# import numpy as np
# from mcf_data import GREYSHADE_CLOCKS_CUT
from modules import mcf_utils
from dynamic_data import ControlFlow
from skimage.metrics import structural_similarity as ssim
logging.basicConfig(level=logging.INFO)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
CF = ControlFlow()

# command: str = input('Enter test command: ')
command = 'pr_test'
match command:
    case 'spectate':
        from mcf_api import MCFApi
        
        spec_file = open('stats_field/LoG.bat').readlines()
        g_data = spec_file[-21].split()
        rg = g_data[9][:-1]
        

        CF.ACT.encryptionKey = g_data[7]
        CF.ACT.region = rg.lower()
        CF.ACT.match_id =f"{rg}_{g_data[8]}"
        
        print(CF.ACT.encryptionKey)
        print(CF.ACT.region)
        print(CF.ACT.match_id)
        # input()

        MCFApi.spectate_active_game()


    case 'game_find':
        from mcf_api import MCFApi

        MCFApi.search_game(nick_region='Losseheli#EUNE:EUNE')

    case 'pr_test':
        from modules.mcf_storage import MCFStorage
        from tg_api import TGApi
        from modules.mcf_predicts import PR
        import copy

        CF.SR.tb_rate[1] = CF.SR.WINNER
        CF.SR.games_all = 1

        score = {
            'time': 370,
            'blue_kills': 40,
            'red_kills': 40,
            'blue_towers': 0,
            'red_towers': 0,
            'blue_gold': 24.8,
            'red_gold': 27.6,
            'blue_t1_hp': 70,
            'red_t1_hp': 100
        }
        
        PR.sc = copy.deepcopy(score)
        PR.prepare_predict_values()

        pr = PR.gen_main_predict()
        if pr:

            MCFStorage.rgs_predicts_monitor(message=pr[0], idx=pr[1])
            
        
            CF.SR.blue_characters = 'Gnar Pyke Leblanc Darius Vayne'
            CF.SR.red_characters = 'Rengar Illaoi Jinx Smolder Morgana'

            TGApi.post_request(message=pr[0], message_type='predict')

            time.sleep(4)
            MCFStorage.predicts_monitor(kills=110)
        # print(pr_2)


    case 'bot':
        from tg_api import TGApi

        # message = input('message?: ')
        TGApi.post_request(message='kak nehui delat', predicts_chat=True)

    case 'sim_start':
        from modules.mcf_pillow import is_game_started
        from dynamic_data import Validator

        if is_game_started():
            
            print('LEELEE')

    case 'cut':
        from selenium import webdriver
        from PIL import ImageGrab
        driver = webdriver.Chrome()
        driver.get('https://melbet-545738.top/ru/live/cyber-zone/league-of-legends')
        input('press to grab')
        ImageGrab.grab().save('x_full.png')
    case 'parse':
        from mcf_api import MCFApi
        MCFApi.parse_from_all_sources(char_r='Darius')
        featured: list[str] = MCFApi.get_games_by_character(character='Vayne')
        finded_game_characerts = 'Karthus Zilean Vayne Gragas Trundle'.split()
        # print(featured)
        for charlist in featured:
            nicknames = charlist.split('-|-')[1].split('_|_')
            characters = charlist.split('-|-')[0].split(' | ')
            common_elements = MCFApi.count_of_common(sequence_1=characters, sequence_2=finded_game_characerts)

            if common_elements >= 4:
                logger.info('Finded!: {characters}'.format(characters=nicknames))
                break
    case 'cmpactive':
        from modules import mcf_pillow
        mcf_pillow.is_league_stream_active(debug=True)
    case 'scrgrab':
        ImageGrab.grab().crop((862, 2, 951, 22)).save('spectator_compare.png')
        # ImageGrab.grab().save('screenshot.png')
    case 'last':
            from dynamic_data import ActiveGame
            from static_data import Switches
            import mcf_api
            logger.info('Debugging last game')
            ActiveGame.area = 'europe'
            ActiveGame.region = 'euw1'
            ActiveGame.match_id = 'EUW1_5942324637'
            
            Switches.bot_activity = True
            mcf_api.MCFApi.awaiting_game_end()
            logger.info('Debug end.')
    case 'parse_test':
        
        
        test_featured = mcf_utils.async_riot_parsing() # Parse featured games from Riot API
        print(test_featured)
            # logger.info(f'Games parsed succesfully. {i}')
    case 'cstm':

        while True:
            screen = np.array(ImageGrab.grab().crop((1855, 310, 1872, 320)).convert('L'))
            print(ssim(screen, GREYSHADE_CLOCKS_CUT))
            time.sleep(0.75)
        # image = screen.crop((693, 160, 721, 172))
        # screen.save('xbt.png')
    case 'ssim':
        logger.info('SSIM test running...')
        import mcf_api
        chars = mcf_api.MCFApi.get_characters()
    case 'sdiff':
        from modules import mcf_pillow
        from modules import mcf_autogui
        logger.info('Diff check. Press any key to start')
        input()
        
        while not mcf_pillow.is_league_stream_active():
            logger.info('Waiting for stream')
            time.sleep(2)
        mcf_autogui.open_score_tab()

    case 'force':
        from mcf_api import MCFApi
        from static_data import MCFThread, Switches
        from modules import mcf_pillow
        from modules import mcf_autogui
        from dynamic_data import ActiveGame
    
        nickname = input('Enter nickname:region: ')
        # maitretays#EUW:EUW
        if MCFApi.get_activegame_parametres(nicknames=[nickname, ]):

            MCFThread(func=MCFApi.awaiting_game_end, args=(MCFApi, )).start()
            logger.info('Checker started')
            logger.info(ActiveGame.region)
            logger.info(ActiveGame.encryptionKey)
            logger.info(ActiveGame.area)
            logger.info(ActiveGame.match_id)
            input('Spectate game?')
            MCFApi.spectate_active_game()

            while not mcf_pillow.is_league_stream_active():
                logger.info('Waiting for stream')
                time.sleep(2)
            mcf_autogui.open_score_tab()

            while Switches.request:
                mcf_autogui.doubleClick(x=658, y=828)
                time.sleep(2)