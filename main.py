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

    chrome = Chrome()
    chrome.start()
    chrome.delay(3)

    logger.info('BOT started')
    Switches.bot_activity = True
    while True:
        
        chrome.open_league_stream()
        chrome.delay(6)
        chrome.remove_cancel()
        chrome.notify_when_starts()
        chrome.stream_fullscreen()

        teams = MCFApi.get_characters()

        if not teams:
            TGApi.send_simple_message('Распрознавание неудачно. Ждем следующую игру')
            logger.warning('Recognizing failed!')
            nicknames = False
        else:
            MCFApi.parse_from_all_sources(teams['red'][0])
            nicknames = MCFApi.finded_game(teams=teams)
            logger.info(nicknames)

            if not nicknames:
                TGApi.send_simple_message('Игра не найдена. Ждем следующую')
                # chrome.driver.quit()
        
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
                if not Switches.predicted:
                    chrome.generate_predict(score)
                chrome.remove_cancel()
                time.sleep(2)

            MCFApi.delete_scoreboard()
            MCFApi.close_league_of_legends()

            logger.info('Game {game_id} ended.')
            if Switches.coeff_opened is False:
                for _ in range(120):
                    is_opened = chrome.check_if_opened()
                    if is_opened:
                        TGApi.send_simple_message('🟢Открыты')
                        break
                    time.sleep(1)
            
            Switches.coeff_opened = False
            ActiveGame.refresh()
        

        logger.info('Bot restarting')


if __name__ == "__main__":
    while True:
        main()