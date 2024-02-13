import logging
import time
from PIL import ImageGrab
import numpy as np
from mcf_data import GREYSHADE_CLOCKS_CUT
from modules import mcf_utils
from skimage.metrics import structural_similarity as ssim
logging.basicConfig(level=logging.INFO)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


command: str = input('Enter test command: ')

match command:
    case 'cut':
        from selenium import webdriver
        from PIL import ImageGrab
        driver = webdriver.Chrome()
        driver.get('https://melbet-545738.top/ru/live/cyber-zone/league-of-legends')
        input('press to grab')
        ImageGrab.grab().save('x_full.png')
    case 'parse':
        from mcf_api import MCFApi
        MCFApi.parse_from_all_sources(char_r='Leona')
        featured: list[str] = MCFApi.get_games_by_character(character='Malphite')
        finded_game_characerts = ['Kogmaw', 'Ezreal', 'Aphelios', 'Fizz', 'Malphite']
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
            from global_data import ActiveGame
            from mcf_data import Switches
            import mcf_api
            logger.info('Debugging last game')
            ActiveGame.area = 'europe'
            ActiveGame.region = 'euw1'
            ActiveGame.match_id = 'EUW1_5942324637'
            
            Switches.bot_activity = True
            mcf_api.MCFApi.awaiting_game_end()
            logger.info('Debug end.')
    case 'parse_test':
        
        # tests_1 = ['Aatrox', 'AurelionSol', 'Vayne', 'Sylas', 'Rengar']
        tests_1 = 'Malphite Brand Mordekaiser Vayne'.split()
        for i in tests_1:
            logger.info(f'Parsing from RiotAPI and Poro... {i}')
            mcf_utils.async_poro_parsing(champion_name=i) # Parse full PoroARAM by region
            mcf_utils.direct_poro_parsing(red_champion=i) # Parse only main page PoroARAM
            mcf_utils.async_riot_parsing() # Parse featured games from Riot API
            logger.info(f'Games parsed succesfully. {i}')
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
        from mcf_data import MCFThread, Switches
        from modules import mcf_pillow
        from modules import mcf_autogui
        from global_data import ActiveGame
    
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