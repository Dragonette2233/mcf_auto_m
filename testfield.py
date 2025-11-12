
import time
import sys
from mcf import utils
from mcf.dynamic import CF
from skimage.metrics import structural_similarity as ssim
from shared.logger import logger

# command: str = input('Enter test command: ')
command = sys.argv[1]
match command:
    case 'prsignal':
        from shared.storage import uStorage
        uStorage.upd_pr_signal("PR 108.5Б FL_0.75")
    # case 'pr_test':
        
    #     from mcf.livegamedata import generate_scoreboard
        
    #     print(generate_scoreboard)
    case 'pr_link':
        from mcf.dynamic import CF
        from mcf.api.telegram import TGApi
        from mcf.api.chrome import Chrome
        from shared.storage import uStorage
        
        link = uStorage.get_key(key="CURRENT_GAME_LINK")


        chrome = Chrome()
        
        message = '🔽PR 108.5M FL_0.69🔽'
        CF.SR.blue_characters = 'One two bool free zed'
        CF.SR.red_characters = 'One less bool cool zed'
        
        # TGApi.post_request(message=message, message_type='predict', link=link)
        TGApi.winner_is(winner='blue', kills=67, timestamp=(10, 1), opened=True, link=link)
    case 'drv':
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.action_chains import ActionChains
        # from static im

                
        def _fnd(drv: webdriver.Chrome, el):
            
            # Найти iframe и переключиться на него
            container = drv.find_element(By.CSS_SELECTOR, 'section media-container media-container--theme-primary media-side__item'.replace(' ', '.'))
            iframe = container.find_element(By.CSS_SELECTOR, 'iframe')
            drv.switch_to.frame(iframe)

            
            video_player = drv.find_element(By.CSS_SELECTOR, el)
            # video_player.

            # Перевести видеоплеер в полноэкранный режим через JavaScript
            # drv.switch_to.default_content()
            # drv.switch_to.window(drv.current_window_handle)  # Активировать окно Selenium
            actions = ActionChains(drv)
            actions.move_to_element(video_player).click().perform()
            drv.execute_script("arguments[0].requestFullscreen();", video_player)
            # Теперь можно искать элементы внутри секции
            # inner_element = drv.find_element(By.CSS_SELECTOR, el)
            # print(inner_element)
            # print(f"IS: {inner_element.is_displayed()}")
            # actions = ActionChains(drv)
            # actions.move_to_element(inner_element).click().perform()
            # drv.execute_script("arguments[0].click();", inner_element)

            # Вернуться обратно к основному контенту
            drv.switch_to.default_content()

            
            
            # media = drv.find_elements(By.CSS_SELECTOR, media_css)
            
            # if len(media) != 0:
            #     nxt = media[0].find_elements(By.CSS_SELECTOR, el)
            #     print(nxt)
            
        
        from mcf.dynamic import CF
        from mcf.api.telegram import TGApi
        from mcf.api.chrome import Chrome
        
        chrome = Chrome()   
        
        chrome.start()
        chrome.open_league_page()
        
        while True:
            try:
                el = input()
                _fnd(chrome.driver, el.strip().replace(' ', '.'))
            except Exception as e:
                print(e)
        
    case 'spectate':
        from mcf.api.overall import MCFApi
        
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

        MCFApi.search_game(nick_region='VendettaCorrida#RU1:RU')

    case 'ktt':
        from shared.storage import uStorage
        from mcf.api.telegram import TGApi
        from mcf.predicts import PR
        import copy

        def ktt_round(values: tuple = (420, 12, 14)):
            CF.SR.tb_rate[1] = CF.SR.WINNER
            CF.SR.games_all = 1

            score = {
                'time': values[0],
                'blue_kills': values[1],
                'red_kills': values[2],
                'blue_towers': 1,
                'red_towers': 0,
                'blue_gold': 32.6,
                'red_gold': 30.9,
                'blue_t1_hp': 49,
                'red_t1_hp': 0,
                'blue_t2_hp': 100,
                'red_t2_hp': 100
            }
            
            PR.sc = copy.deepcopy(score)
            PR.prepare_predict_values()
            pr = PR.gen_main_predict()
            
            print(pr)
        
        # ktt_round((240, 16, 16))
        ktt_round((535, 30, 27))
    
    case 'pr_test':
        from shared.storage import uStorage
        from mcf.api.telegram import TGApi
        from mcf.predicts import PR
        import copy

        CF.SR.tb_rate[1] = CF.SR.WINNER
        CF.SR.games_all = 1

        score = {
            'time': 370,
            'blue_kills': 11,
            'red_kills': 12,
            'blue_towers': 0,
            'red_towers': 0,
            'blue_gold': 24.8,
            'red_gold': 27.6,
            'blue_t1_hp': 70,
            'red_t1_hp': 100,
            'blue_t2_hp': 70,
            'red_t2_hp': 100
        }
        
        PR.sc = copy.deepcopy(score)
        PR.prepare_predict_values()
        
        # pr = PR.gen_main_predict()
        pr = '🔽PR 110.5М FL_1🔽'
        if pr:

            PR.pr_message_to_tuple(message='🔽PR 110.5М FL_1🔽')
            
        
            CF.SR.blue_characters = 'Gnar Pyke Leblanc Darius Vayne'
            CF.SR.red_characters = 'Rengar Illaoi Jinx Smolder Morgana'

            # TGApi.post_request(message=pr[0], message_type='predict')
            
            total = 112
            uStorage.save_predict_result(kills=total)
            
            # print(pr)

            
            # alert = f"⚠️ Тотал: 98 | На сайте: 110.5 | Время: {PR.sc['time']}"
            # TGApi.post_send(message=alert, chat_id=TGApi.CHAT_ID_PR)
        # print(pr_2)


    case 'bot':
        from tg_api import TGApi

        # message = input('message?: ')
        TGApi.post_request(message='kak nehui delat', predicts_chat=True)
    case 'gettime':
        from mcf.ssim_recognition import ScoreRecognition
        from PIL import ImageGrab
        
        data = ScoreRecognition.screen_score_recognition()
        
        red_tw_img = ImageGrab.grab().crop((681, 7, 1261, 99)).crop((503, 13, 519, 29))
        
        print(red_tw_img.size)
        red_tw_img.show()
        
        print(data)
        
       # data = ssim_recognition
    case 'sim_start':
        from mcf.pillow import is_game_started
        from mcf.dynamic import Validator

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
        from mcf.api.overall import MCFApi
        MCFApi.parse_from_all_sources(char_r='Sona')
        featured: list[str] = MCFApi.get_games_by_character(character='DrMundo')
        finded_game_characerts = 'DrMundo Jhin Fiora Azir Rumble'.split()
        # print(featured)
        for charlist in featured:
            nicknames = charlist.split('-|-')[1].split('_|_')
            characters = charlist.split('-|-')[0].split(' | ')
            common_elements = MCFApi.count_of_common(sequence_1=characters, sequence_2=finded_game_characerts)

            if common_elements >= 4:
                logger.info('Finded!: {characters}'.format(characters=nicknames))
                break
            
    case 'cmpactive':
        from mcf import pillow
        pillow.is_league_stream_active(debug=True)
    case 'scrgrab':
        from PIL import ImageGrab
        ImageGrab.grab().crop((862, 2, 951, 22)).save('spectator_compare.png')
        # ImageGrab.grab().save('screenshot.png')
    case 'last':
            from mcf.dynamic import ActiveGame
            from mcf.static_data import Switches
            import mcf_api
            logger.info('Debugging last game')
            ActiveGame.area = 'europe'
            ActiveGame.region = 'euw1'
            ActiveGame.match_id = 'EUW1_5942324637'
            
            Switches.bot_activity = True
            mcf_api.MCFApi.awaiting_game_end()
            logger.info('Debug end.')
    case 'parse_test':
        
        
        test_featured = utils.async_riot_parsing() # Parse featured games from Riot API
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
        from mcf import pillow
        from mcf import autogui
        logger.info('Diff check. Press any key to start')
        input()
        
        while not pillow.is_league_stream_active():
            logger.info('Waiting for stream')
            time.sleep(2)
        autogui.open_score_tab()

    case 'force':
        from mcf_api import MCFApi
        from mcf.static_data import MCFThread, Switches
        from mcf import pillow
        from mcf import autogui
        from mcf.dynamic import ActiveGame
    
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

            while not pillow.is_league_stream_active():
                logger.info('Waiting for stream')
                time.sleep(2)
            autogui.open_score_tab()

            while Switches.request:
                autogui.doubleClick(x=658, y=828)
                time.sleep(2)