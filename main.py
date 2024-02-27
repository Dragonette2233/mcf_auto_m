import logging
import time
logging.basicConfig(level=logging.INFO)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from modules import mcf_pillow
from modules import mcf_autogui
from global_data import ActiveGame
from chrome_driver import Chrome
from global_data import Validator
from mcf_data import (
    Switches,
    MCFThread,
    StatsRate
)
from mcf_api import MCFApi
from tg_api import TGApi

def main():

    MCFApi.delete_scoreboard()
    StatsRate.stats_clear()
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
        chrome.stream_close()
        nicknames = MCFApi.finded_game(teams=teams)

        logger.info(nicknames)
    
        if nicknames and MCFApi.get_activegame_parametres(nicknames=nicknames):
            
            TGApi.gamestart_notification(
                team_blue=' '.join(teams['blue']),
                team_red=' '.join(teams['red']),
                status_message=f'✅ {ActiveGame.nick_region}'
            )

            MCFThread(func=MCFApi.awaiting_game_end, args=(chrome, )).start()
            MCFApi.spectate_active_game()

            while not mcf_pillow.is_league_stream_active():
                time.sleep(2)
            logger.info('Spectator activated')
            mcf_autogui.open_score_tab()

            while Switches.request:
                mcf_autogui.doubleClick(x=658, y=828)
                score = mcf_pillow.generate_scoreboard()
                if score["time"] < 600:
                    chrome.generate_predict(score)
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
            Switches.spredicted = False
            StatsRate.stats_clear()
            ActiveGame.refresh()
            # time.sleep(300)
        else:
            if Validator.quick_end:
                status = '❌ Remake'
            else:
                status = '❌ Не найдена'
            
            TGApi.gamestart_notification(
                team_blue=' '.join(teams['blue']),
                team_red=' '.join(teams['red']),
                status_message=status
            )

            if Validator.quick_end:
                TGApi.winner_is(
                            team=Validator.ended_winner, 
                            kills=Validator.ended_kills,
                            timestamp=Validator.ended_time
                        )
                Validator.quick_end = False


            
        logger.info('Bot restarting')
        chrome.driver.quit()
        del chrome

if __name__ == "__main__":
    main()