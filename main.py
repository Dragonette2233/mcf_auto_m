
import time
import logging
from modules.mcf_storage import MCFStorage
from modules import mcf_pillow
from modules import mcf_autogui
from dynamic_data import CF
from chrome_driver import Chrome
from static_data import (
    MCFThread,
    TelegramStr
)
from mcf_api import MCFApi
from tg_api import TGApi

logging.basicConfig(level=logging.INFO)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# check commit

def main():

    MCFApi.delete_scoreboard()
    # StatsRate.stats_clear()

    logger.info('BOT started')
    
    while True:
        
        chrome = Chrome()        
        chrome.start()
        chrome.open_league_page()
        chrome.remove_cancel()
        chrome.notify_when_starts()

        if chrome.RESTART_REQUIRED:
            del chrome
            break

        chrome.stream_fullscreen()
        teams = MCFApi.get_characters()
        
        if not teams:
            MCFStorage.save_gameid('Err')
            del chrome
            break

        chrome.open_activegame_page()
        nicknames = MCFApi.finded_game(teams=teams)

        logger.info(nicknames)
    
        if nicknames and MCFApi.get_activegame_parametres(nicknames=nicknames):
            
            TGApi.gamestart_notification(
                team_blue=' '.join(teams['blue']),
                team_red=' '.join(teams['red']),
                status_message=TelegramStr.game_founded.format(CF.ACT.nick_region)
            )

            MCFThread(func=MCFApi.awaiting_game_end, args=(chrome, )).start()
            MCFApi.spectate_active_game()

            while not mcf_pillow.is_league_stream_active():
                time.sleep(2)
            logger.info('Spectator activated')
            mcf_autogui.open_score_tab()

            while CF.SW.request.is_active():
                mcf_autogui.doubleClick(x=658, y=828)
                score = mcf_pillow.generate_scoreboard()
                chrome.generate_predict(score)
                
                TGApi.update_score(score, 
                                   is_total_opened=chrome.is_total_coeff_opened(),
                                   total_value=chrome.ACTIVE_TOTAL_VALUE)
                
                chrome.remove_cancel()
                time.sleep(3.5)

            TGApi.update_score(score=False)
            MCFApi.close_league_of_legends()

            logger.info('Game ended.')
            
            if not CF.SW.coeff_opened.is_active():
                for _ in range(120):
                    is_opened = chrome.is_total_coeff_opened(end_check=True)
                    if is_opened:
                        TGApi.send_simple_message('🟢 Открыты')
                        break
                    time.sleep(0.5)
            
        else:
            if CF.SW.quick_end.is_active():
                status = TelegramStr.game_remake
            else:
                status = TelegramStr.game_not_founded
            
            TGApi.gamestart_notification(
                team_blue=' '.join(teams['blue']),
                team_red=' '.join(teams['red']),
                status_message=status
            )

            if CF.SW.quick_end.is_active():
                TGApi.winner_is(
                            team=CF.END.winner,
                            kills=CF.END.kills,
                            timestamp=CF.END.time
                        )
            
        logger.info('Bot restarting')
        CF.reset()
        chrome.driver.quit()
        del chrome

if __name__ == "__main__":
    while True:
        main()
