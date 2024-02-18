import time
import modules.mcf_autogui as mcf_autogui
import modules.mcf_pillow as mcf_pillow
from modules.mcf_storage import MCFStorage
import logging
from global_data import Validator
from tg_api import TGApi
from mcf_data import Switches, StatsRate, MIRROR_PAGE
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)

class Chrome:

    def __init__(self) -> None:
        self.XPATH_BTN_GAME = '//*[@id="app"]/div[3]/div/div/div[2]/main/div[2]/div/div/div[2]/div/ul/li/ul/li/div[1]/span[2]/span[2]/span/button'
                            # /html/body/div[1]/div/div/div[3]/div/div/div[2]/main/div[2]/div/div/div[2]/div/ul/li[2]/ul/li/div[1]/span[2]/span[2]/span/button
                            #  //*[@id="app"]/div[3]/div/div/div[2]/main/div[2]/div/div/div[2]/div/ul/li[2]/ul/li/div[1]/span[2]/span[2]/span/button
        self.CSS_BTN_REJECT_LIVE = 'button.ui-button.dashboard-redirect-message-timer__btn.ui-button--size-m.ui-button--theme-gray.ui-button--rounded'
        self.CSS_BTN_FOR_BET = 'li.ui-dashboard-champ.dashboard-champ.dashboard__champ.ui-dashboard-champ--theme-gray'
        self.CSS_TABLE_GAMES = 'li.ui-dashboard-champ.dashboard-champ.dashboard__champ.ui-dashboard-champ--theme-gray'
        self.URL_MAIN = 'https://lite.1xbet-new.com/ru/live/cyber-zone/league-of-legends'
        self.options = Options()
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
        self.driver = None
        self.game_index_new = ''
        self.game_index_ended = MCFStorage.get_gameid()
        
    
    def start(self):
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.maximize_window()
        time.sleep(3)
        mcf_autogui.click(x=1896, y=99) #disable infobar
        time.sleep(3)

    def open_league_page(self):
        with open(MIRROR_PAGE, 'r') as ex_url:
            url: str = ex_url.read().strip()
        
        if url.startswith('https://mel'):
            Validator.active_mel_mirror = True
        else:
            Validator.active_mel_mirror = False
        self.driver.get(url=url)
        time.sleep(6)

    def remove_cancel(self):
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, self.CSS_BTN_REJECT_LIVE)
            element.click()
        except (NoSuchElementException, TimeoutException):
            pass

    def delay(self, second: int):
        time.sleep(second)

    def stream_close(self):
        mcf_autogui.close_league_stream()

    def stream_fullscreen(self):
        if Validator.active_mel_mirror:
            mcf_autogui.click(x=1882, y=374)
        else:
            mcf_autogui.click(x=1871, y=325)
        time.sleep(3.5)


    def check_if_opened(self):
       
        try:
            games = self.driver.find_elements(By.CSS_SELECTOR, 'li.ui-dashboard-champ.dashboard-champ.dashboard__champ.ui-dashboard-champ--theme-gray')
            aram_title_outer = games[0].find_element(By.CSS_SELECTOR, 'span.caption.ui-dashboard-champ-name__caption.caption--size-m')
            aram_title_inner: str = aram_title_outer.find_element(By.CSS_SELECTOR, 'span.caption__label').get_attribute('innerText')
              
            if aram_title_inner == 'All Random All Mid':
                game_link = games[0].find_element(By.CSS_SELECTOR, 'a.dashboard-game-block__link.dashboard-game-block-link').get_attribute('href')
                game_index = '_'.join(game_link.split('/')[7:])
                if game_index == self.game_index_ended:
                    button = games[0].find_element(By.CSS_SELECTOR, 'button.ui-market.ui-market--nameless')
                    if not button.get_attribute('disabled'):
                        Switches.coeff_opened = True
                        return True
        except (NoSuchElementException, IndexError, Exception):
            pass
            
        return False
    
    def generate_predict_winner(self, score):

        gametime = int(score["time"])
        if StatsRate.is_stats_avaliable() and gametime < 600:
            blue_kills = score["blue_kills"] # "blue_kiils": 49,
            red_kills = score["red_kills"] # "red_kills": 43,
            blue_towers = score["blue_towers"] # "blue_towers": 3,
            red_towers = score["red_towers"]

            match StatsRate.blue_rate[1], StatsRate.red_rate[1]:
                case StatsRate.WINNER, StatsRate.LOSER:
                    if (blue_towers > 0 and red_towers == 0) and blue_kills > red_kills:
                        TGApi.send_simple_message('🐳 Predict П1 🐳', predict_win=True)
                    if gametime > 420 and blue_kills > red_kills and abs(blue_kills - red_kills) > 5:
                        TGApi.send_simple_message('🐳 Predict П1 🐳', predict_win=True)
                    if blue_kills > red_kills and abs(blue_kills - red_kills) > 7:
                        TGApi.send_simple_message('🐳 Predict П1 🐳', predict_win=True)
                case StatsRate.LOSER, StatsRate.WINNER:
                    if (blue_towers == 0 and red_towers > 0) and blue_kills < red_kills:
                        TGApi.send_simple_message('🐙 Predict П2 🐙', predict_win=True)
                    if gametime > 420 and blue_kills < red_kills and abs(blue_kills - red_kills) > 5:
                        TGApi.send_simple_message('🐙 Predict П2 🐙', predict_win=True)
                    if red_kills > blue_kills and abs(blue_kills - red_kills) > 7:
                        TGApi.send_simple_message('🐙 Predict П2 🐙', predict_win=True)
                case StatsRate.LOSER, StatsRate.LOSER:
                    pass



    def generate_predict_total(self, score):

        # is_opened = self.check_if_opened()
        gametime = int(score["time"])
        if gametime < 600:
            blue_kills = score["blue_kills"] # "blue_kiils": 49,
            red_kills = score["red_kills"] # "red_kills": 43,
            blue_towers = score["blue_towers"] # "blue_towers": 3,
            red_towers = score["red_towers"] # "red_towers": 1,

            all_kills = blue_kills + red_kills
            module_kills = abs(blue_kills - red_kills)
            # gametime = int(score["time"]) # "time": 1034,

            if blue_kills + red_kills >= 60 and abs(blue_kills - red_kills) < 5 and (blue_towers == 0 and red_towers == 0):
                TGApi.send_simple_message('⬆️ Predict 110Б (FL 1) ⬆️', predict_ttl=True)

            elif blue_kills + red_kills >= 80 and abs(blue_kills - red_kills) < 5 and (blue_towers == 1 and red_towers == 1):
                TGApi.send_simple_message('⬆️ Predict 110Б (FL 0.75) ⬆️', predict_ttl=True)

            elif blue_kills + red_kills <= 35 and abs(blue_kills - red_kills) >= 6 and (blue_towers != 0 or red_towers != 0):
                TGApi.send_simple_message('⬇️ Predict 110M (FL 0.75) ⬇️', predict_ttl=True)

            elif gametime > 420 and blue_kills + red_kills < 25 and abs(blue_kills - red_kills) > 5:
                TGApi.send_simple_message('⬇️ Predict 110M (FL 1) ⬇️', predict_ttl=True)

            elif gametime > 480 and blue_kills + red_kills < 40 and (blue_towers != 0 or red_towers != 0):
                TGApi.send_simple_message('⬇️ Predict 110M (FL 0.5) ⬇️', predict_ttl=True)
        
            elif gametime > 500 and blue_kills + red_kills < 30 and abs(blue_kills - red_kills) > 5:
                TGApi.send_simple_message('⬇️ Predict 110M (FL 1) ⬇️', predict_ttl=True)
            
            elif blue_kills + red_kills < 22 and (blue_towers > 0 or red_towers > 0):
                TGApi.send_simple_message('⬇️ Predict 110M (FL 1) ⬇️', predict_ttl=True)
            # else:
            #     app_blueprint.info_view.exception(f'PR: b{blue_kills} r{red_kills} twb {blue_towers} twr{red_towers}')

    def notify_when_starts(self):

        passages = 0

        while True:

            try:
                games = self.driver.find_elements(By.CSS_SELECTOR, 'li.ui-dashboard-champ.dashboard-champ.dashboard__champ.ui-dashboard-champ--theme-gray')
                aram_title_outer = games[0].find_element(By.CSS_SELECTOR, 'span.caption.ui-dashboard-champ-name__caption.caption--size-m')
                aram_title_inner: str = aram_title_outer.find_element(By.CSS_SELECTOR, 'span.caption__label').get_attribute('innerText')
              
                if aram_title_inner == 'All Random All Mid':
                    game_link = games[0].find_element(By.CSS_SELECTOR, 'a.dashboard-game-block__link.dashboard-game-block-link').get_attribute('href')
                    game_index = '_'.join(game_link.split('/')[7:])
                    # if self.game_index_ended == '':
                    #     self.game_index_ended = MCFStorage.get_gameid()
                    # logger.info(self.game_index_new)
                    # logger.info(self.game_index_ended)
                    if game_index != self.game_index_ended:
                        logger.info('Gamelink changed, refreshing driver')
                        self.open_league_page()
                        time.sleep(6)
                        self.game_index_new = game_index
                        self.game_index_ended = game_index
          
                    if game_index == self.game_index_new:
                        # self.game_index_ended = self.game_index_new
                        stream_btn = aram_title_outer.find_element(By.XPATH, self.XPATH_BTN_GAME)
                        stream_btn.click()
                        time.sleep(2)

                        if mcf_pillow.is_game_started():
                            logger.info('Game started: (from comparing stream)')
                            # self.game_index_ended = game_index
                            self.game_index_new = ''
                            MCFStorage.save_gameid(self.game_index_ended)
                            try:
                                gametime_element = games[0].find_element(By.CSS_SELECTOR, 'span.dashboard-game-info__item.dashboard-game-info__time')
                                gametime = str(gametime_element.get_attribute('innerText'))
                                minutes = gametime.split(':')[0]
                                if minutes in ('00', '01', '02', '03', '04', '05', '06'):
                            
                                    logger.info('Game started: {gametime}'.format(gametime=gametime))
                                    TGApi.display_gamestart(timer=gametime)
                                else:
                                    TGApi.display_gamestart(timer=None)
                            except:
                                TGApi.display_gamestart(timer=None)
                                pass
                            return
                        else:
                            stream_btn.click()
                            time.sleep(1)
                    else:
                        self.remove_cancel()
                        time.sleep(1)
            except AttributeError:
                time.sleep(1)
            except IndexError:
                time.sleep(1)
            except (NoSuchElementException, StaleElementReferenceException):
                time.sleep(1)
            except Exception as ex_:
                logger.info(self.game_index_new)
                logger.info(self.game_index_ended)
                logger.warning(ex_)
                # logger.warning(exc_info=True)
                time.sleep(1)

            self.remove_cancel()


            if passages == 40:
                passages = 0
                self.open_league_page()
            else:
                time.sleep(0.5)
                passages += 1
            