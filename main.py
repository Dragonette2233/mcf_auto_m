import logging
import time
logging.basicConfig(level=logging.INFO)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from modules import mcf_pillow
from modules import mcf_autogui
from global_data import ActiveGame
from chrome_driver import Chrome
from mcf_data import (
    Switches,
    MCFThread,
)
from mcf_api import MCFApi
from tg_api import TGApi

# game = ActiveGame()

# Примеры использования логгера
# logger.debug('Это сообщение уровня DEBUG')
# logger.info('Это сообщение уровня INFO')
# logger.warning('Это сообщение уровня WARNING')
# logger.error('Это сообщение уровня ERROR')
# logger.critical('Это сообщение уровня CRITICAL')


def main():

    MCFApi.delete_scoreboard()
    # chrome = Chrome()
    # chrome.start()
    logger.info('BOT started')
    
    while True:
        
        chrome = Chrome()
        chrome.start()
        chrome.open_league_page()
        chrome.remove_cancel()
        chrome.notify_when_starts()
        chrome.stream_fullscreen()
        teams = MCFApi.get_characters()

        if not teams:
            TGApi.send_simple_message('Распрознавание неудачно. Ждем следующую игру')
            logger.warning('Recognizing failed!')
            nicknames = False
        else:
            chrome.stream_close()
            nicknames = MCFApi.finded_game(teams=teams)
            logger.info(nicknames)
    
        if nicknames and MCFApi.get_activegame_parametres(nicknames=nicknames):
            
            MCFThread(func=MCFApi.awaiting_game_end, args=(chrome, )).start()
            MCFApi.spectate_active_game()

            while not mcf_pillow.is_league_stream_active():
                time.sleep(2)
            logger.info('Spectator activated')
            mcf_autogui.open_score_tab()

            while Switches.request:
                mcf_autogui.doubleClick(x=658, y=828)
                score = mcf_pillow.generate_scoreboard()
                
                if not Switches.predicted_total:
                    chrome.generate_predict_total(score)

                if not Switches.predicted_winner:
                    chrome.generate_predict_winner(score)
                
                chrome.remove_cancel()
                time.sleep(2)

            MCFApi.delete_scoreboard()
            MCFApi.close_league_of_legends()

            logger.info('Game ended.')
            
            if Switches.coeff_opened is False:
                for _ in range(120):
                    is_opened = chrome.check_if_opened()
                    if is_opened:
                        TGApi.send_simple_message('🟢 Открыты')
                        break
                    time.sleep(1)
            
            Switches.coeff_opened = False
            Switches.predicted_total = False
            Switches.predicted_winner = False
            ActiveGame.refresh()
            time.sleep(300)
        else:
            mcf_autogui.close_league_stream()
            TGApi.send_simple_message('❌ Игра не найдена')
            time.sleep(500)

        logger.info('Bot restarting')
        chrome.driver.quit()
        del chrome

if __name__ == "__main__":
    main()