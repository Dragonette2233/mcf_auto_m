import time
import modules.mcf_autogui as mcf_autogui
import modules.mcf_pillow as mcf_pillow
import logging
from mcf_data import Validator
from PIL import Image
from tg_api import TGApi
from mcf_data import Switches
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
        self.CSS_BTN_REJECT_LIVE = 'button.ui-button.dashboard-redirect-message-timer__btn.ui-button--size-m.ui-button--theme-gray.ui-button--rounded'
        self.CSS_BTN_FOR_BET = 'li.ui-dashboard-champ.dashboard-champ.dashboard__champ.ui-dashboard-champ--theme-gray'
        self.CSS_TABLE_GAMES = 'li.ui-dashboard-champ.dashboard-champ.dashboard__champ.ui-dashboard-champ--theme-gray'
        self.URL_MAIN = 'https://lite.1xbet-new.com/ru/live/cyber-zone/league-of-legends'
        self.options = Options()
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
        self.driver = None
        self.game_index_new = ''
        self.game_index_ended = ''
        
    
    def start(self):
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.maximize_window()
        time.sleep(3)
        mcf_autogui.click(x=1896, y=99) #disable infobar

    def open_league_stream(self):
        with open('./mcf_lib/mirror_page.txt', 'r') as ex_url:
            url = ex_url.read().strip()
        self.driver.get(url=url)

    def remove_cancel(self):
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, self.CSS_BTN_REJECT_LIVE)
            element.click()
        except NoSuchElementException:
            pass

    def delay(self, second: int):
        time.sleep(second)

    def stream_activate(self, aram_block):
        stream_active = 0
        while True:
            try:
                element = WebDriverWait(self.driver, 4).until(
                    EC.element_to_be_clickable((By.XPATH, self.XPATH_BTN_GAME))
                )
                element.click()
                break
            except (TimeoutException, NoSuchElementException):
                if stream_active == 20:
                    return False
                logger.info('No stream finded yet')
                time.sleep(1.5)
                stream_active += 1
                continue
    
        return True

    def stream_reactivate(self):
        self.stream_activate()
        time.sleep(2)
        self.stream_activate()
        time.sleep(2)

    def stream_fullscreen(self):
        time.sleep(1.5)
        mcf_autogui.click(x=1871, y=325)
        time.sleep(3.5)


    def check_if_opened(self):
        # for _ in range(120):
        try:
            games = self.driver.find_elements(By.CSS_SELECTOR, 'li.ui-dashboard-champ.dashboard-champ.dashboard__champ.ui-dashboard-champ--theme-gray')
        except Exception as ex_:
            games = []
            # print(ex_)
            
        try:
            button = games[0].find_element(By.CSS_SELECTOR, 'button.ui-market.ui-market--nameless')
            if not button.get_attribute('disabled'):
                return True
        except NoSuchElementException:
            pass
        except IndexError:
            pass
  
    def generate_predict(self, score):

        is_opened = self.check_if_opened()
        if is_opened:
            blue_kills = score["blue_kills"] # "blue_kiils": 49,
            red_kills = score["red_kills"] # "red_kills": 43,
            blue_towers = score["blue_towers"] # "blue_towers": 3,
            red_towers = score["red_towers"] # "red_towers": 1,
            gametime = int(score["time"]) # "time": 1034,

            if blue_kills + red_kills >= 60 and abs(blue_kills - red_kills) < 5 and (blue_towers == 0 and red_towers == 0):
                TGApi.send_simple_message('⬆️ Predict 110Б ⬆️')

            elif blue_kills + red_kills >= 80 and abs(blue_kills - red_kills) < 5 and (blue_towers == 1 and red_towers == 1):
                TGApi.send_simple_message('⬆️ Predict 110Б ⬆️')

            elif blue_kills + red_kills <= 35 and abs(blue_kills - red_kills) >= 7 and (blue_towers > 0 or red_towers > 0):
                TGApi.send_simple_message('⬇️ Predict 110M ⬇️')

            elif gametime > 420 and blue_kills + red_kills < 25 and abs(blue_kills - red_kills) > 5:
                TGApi.send_simple_message('⬇️ Predict 110M ⬇️')
            # else:
            #     app_blueprint.info_view.exception(f'PR: b{blue_kills} r{red_kills} twb {blue_towers} twr{red_towers}')


    def notify_when_starts(self):

        

        while True:

            # if Switches.force_start:
            #     Switches.force_start = False
            #     return

            try:
                games = self.driver.find_elements(By.CSS_SELECTOR, 'li.ui-dashboard-champ.dashboard-champ.dashboard__champ.ui-dashboard-champ--theme-gray')
                aram_title_outer = games[0].find_element(By.CSS_SELECTOR, 'span.caption.ui-dashboard-champ-name__caption.caption--size-m')
                aram_title_inner: str = aram_title_outer.find_element(By.CSS_SELECTOR, 'span.caption__label').get_attribute('innerText')
              
                if aram_title_inner == 'All Random All Mid':
                    game_link = games[0].find_element(By.CSS_SELECTOR, 'a.dashboard-game-block__link.dashboard-game-block-link').get_attribute('href')
                    game_index = '_'.join(game_link.split('/')[7:])

                    if game_index != self.game_index_new:
                        logger.info('Gamelink changed, refreshing driver')
                        self.open_league_stream()
                        time.sleep(6)
                        self.game_index_ended = self.game_index_new
                        self.game_index_new = game_index
                    
                    if self.game_index_ended != self.game_index_new:
                        stream_btn = games[0].find_element(By.XPATH, self.XPATH_BTN_GAME)
                        stream_btn.click()
                        time.sleep(3)
                        logger.info('btn clicked')

                        if mcf_pillow.is_game_started():
                            logger.info('Game started: (from comparing stream)')
                            self.game_index_ended = game_index
                            try:
                                gametime_element = games[0].find_element(By.CSS_SELECTOR, 'span.dashboard-game-info__item.dashboard-game-info__time')
                                gametime = str(gametime_element.get_attribute('innerText'))
                                minutes = gametime.split(':')[0]
                                if minutes in ('00', '01', '02', '03', '04', '05', '06'):
                            
                                    logger.info('Game started: {gametime}'.format(gametime=gametime))
                                    TGApi.display_gamestart(timer=gametime)
                                # return
                            except:
                                TGApi.display_gamestart(timer=None)
                                pass
                            return
                        else:
                            stream_btn.click()
                            time.sleep(1)
                            stream_btn.click()
                            logger.info('Compare done. Waiting')
                            time.sleep(1)

                    else:
                        logger.info('Waiting for end previos game')
                        self.remove_cancel()
                        time.sleep(1)

            except IndexError:
                self.remove_cancel()
                time.sleep(1)
            except (NoSuchElementException, StaleElementReferenceException):
                self.remove_cancel()
                time.sleep(1)