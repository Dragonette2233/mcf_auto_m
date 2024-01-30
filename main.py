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

game = ActiveGame()

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

    while True:
        
        chrome.open_league_stream()
        chrome.delay(6)
        chrome.remove_cancel()
        logger.info('Waiting for game...')
        chrome.notify_when_starts()

        stream_avaliable = chrome.stream_activate()

        if stream_avaliable:
            chrome.stream_reactivate()
            chrome.stream_fullscreen()
            teams = MCFApi.get_characters()

            if not teams:
                TGApi.send_simple_message('Распрознавание неудачно. Ждем следующую игру')
                logger.warning('Recognizing failed. Bot restart in 300s')
                chrome.driver.quit()
                time.sleep(300)
                break
            
            MCFApi.parse_from_all_sources()
            
            nicknames = MCFApi.finded_game(teams=teams)

            if not nicknames:
                TGApi.send_simple_message('Игра не найдена. Повторная попытка')
                chrome.driver.quit()
                break
            
            if MCFApi.get_activegame_parametres(nicknames=nicknames):

                MCFThread(func=MCFApi.awaiting_game_end, args=(chrome, )).start()
                MCFApi.spectate_active_game()

                while not mcf_pillow.is_league_stream_active():
                    time.sleep(2)
                mcf_autogui.open_score_tab()

                while Switches.request:
                    mcf_autogui.doubleClick(x=658, y=828)
                    score = mcf_pillow.generate_scoreboard()
                    if not Switches.predicted:
                        chrome.generate_predict(score)
                    chrome.remove_cancel()
                    time.sleep(2)

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
                time.sleep(130)
            

            logger.info('Bot restart in 200 seconds')
            time.sleep(200)

        else:
            TGApi.send_simple_message('Кнопка стрима не активна. Ждем следующую')
            time.sleep(300)


if __name__ == "__main__":
    while True:
        main()