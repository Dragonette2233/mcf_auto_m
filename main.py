
import time
import logging
from mcf.storage import MCFStorage
from mcf import pillow
from mcf import autogui
from mcf.dynamic_data import CF
from chrome_driver import Chrome
from mcf.static_data import (
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


    logger.info('BOT started')
            
    chrome = Chrome()        
    chrome.start()
    chrome.open_league_page()
    chrome.remove_cancel()
    chrome.notify_when_starts()

    if chrome.RESTART_REQUIRED:
        return

    chrome.stream_fullscreen()
    teams = MCFApi.get_characters()
    
    if not teams:
        MCFStorage.save_gameid('Err')
        return

    chrome.open_activegame_page()
    nicknames = MCFApi.finded_game(teams=teams)

    logger.info(nicknames)

    if nicknames and MCFApi.is_game_active(nicknames=nicknames):
        
        TGApi.gamestart_notification(
            team_blue=' '.join(teams['blue']),
            team_red=' '.join(teams['red']),
            status_message=TelegramStr.game_founded.format(CF.ACT.nick_region)
        )

        MCFThread(func=MCFApi.awaiting_game_end, args=(chrome, )).start()
        MCFApi.spectate_active_game()

        while not pillow.is_league_stream_active():
            time.sleep(2)
        
    
        while CF.SW.request.is_active():
            autogui.doubleClick(x=658, y=828) # flash foward game
            score = pillow.generate_scoreboard() # generating score using kills, towers, gold and time info
            chrome.generate_predict(score) # generating predict based on score data
            
            TGApi.update_score(score, 
                                is_total_opened=chrome.is_total_coeff_opened(),
                                total_value=chrome.ACTIVE_TOTAL_VALUE) # updating score info in telegram channel
            
            chrome.remove_cancel() # preventing unwanted jump to Live page in Chrome
            time.sleep(3.5) 

        TGApi.update_score(score=False) # deleting score info from game notification in telegram channel
        MCFApi.close_league_of_legends() # clong Leaguee of Legends process

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
        
    logger.info('Bot restarting...')
    CF.reset()
    chrome.driver.quit()

if __name__ == "__main__":
    while True:
        main()
