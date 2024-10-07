
import time
import logging
from mcf.api.storage import uStorage
from mcf.ssim_recognition import ScoreRecognition
from mcf.api import cmouse, winscreen
from mcf.dynamic import CF
from mcf.utils import is_riot_apikey_valid
from mcf.livegamedata import generate_scoreboard
from mcf.api.chrome import Chrome
from mcf.api.overall import MCFApi
from mcf.api.telegram import TGApi
from static import (
    MCFThread,
    TelegramStr,
)

logging.basicConfig(level=logging.INFO)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    is_riot_apikey_valid()
    # uStorage.upd_current_game_link(link=None)
    
    logger.info('BOT started')
    chrome = Chrome()        
    chrome.start()
    chrome.open_league_page()
    chrome.remove_cancel()
    chrome.awaiting_for_start()

    if chrome.RESTART_REQUIRED:
        return

    chrome.stream_fullscreen()
    teams = MCFApi.get_characters()
    
    if not teams:
        uStorage.upd_previous_game_id('Err')
        return

    chrome.open_mobile_page()
    nicknames = MCFApi.get_activegame_by_teams(teams=teams)

    logger.info(nicknames)

    if nicknames and MCFApi.is_game_active(nicknames=nicknames):
        
        TGApi.gamestart_notification(
            team_blue=' '.join(teams['blue']),
            team_red=' '.join(teams['red']),
            status_message=TelegramStr.game_founded.format(CF.ACT.nick_region)
        )

        MCFThread(func=MCFApi.awaiting_game_end, args=(chrome, )).start()
        MCFApi.spectate_active_game()

        while not ScoreRecognition.is_game_started_spectator():
            time.sleep(2)
            
        winscreen.make_league_foreground()
        uStorage.upd_current_game_status("Online")
        
        while CF.SW.request.is_active():
            cmouse.double_click_left(x=658, y=828) # flash foward game
            score = generate_scoreboard() # generating score using kills, towers, gold and time info
            
            if not score:
                MCFApi.spectate_active_game()
                while not ScoreRecognition.is_game_started_spectator():
                    time.sleep(2)
                cmouse.double_click_left(x=658, y=828)
                score = generate_scoreboard()
            else:
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
            for _ in range(136):
                is_opened = chrome.is_total_coeff_opened(end_check=True)
                if is_opened:
                    TGApi.post_send(message='🟢 Открыты', chat_id=TGApi.CHAT_ID_PR)
                    break
                time.sleep(0.5)
        
    else:
        uStorage.upd_current_game_status(status="Не состоялась или не найдена")
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
            winner, kills, timestamp = CF.END.extract()
            TGApi.winner_is(
                        winner=winner,
                        kills=kills,
                        timestamp=timestamp
                    )
        
    logger.info('Bot restarting...')
    CF.reset()
    chrome.driver.quit()

if __name__ == "__main__":
    while True:
        main()
