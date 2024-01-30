import logging
import time
from PIL import ImageGrab
logging.basicConfig(level=logging.INFO)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


command = input('Enter test command: ')

match command:
    case 'cstm':
        # from PIL import ImageGrab

        # from PIL import ImageGrab
        screen = ImageGrab.grab().crop((485, 21, 593, 73))
        # image = screen.crop((693, 160, 721, 172))
        screen.save('xbt.png')
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