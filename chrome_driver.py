import time
import copy
import logging
import mcf.autogui as autogui
import mcf.pillow as pillow
from mcf.storage import MCFStorage
# from modules.mcf_tracing import Trace
from mcf.predicts import PR
from mcf.dynamic_data import CF
from tg_api import TGApi
from mcf.static_data import PATH, TRACE_RANGE, TelegramStr, MelCSS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    StaleElementReferenceException,
    WebDriverException,
    )

logger = logging.getLogger(__name__)

class Chrome:

    def __init__(self) -> None:
        self.options = Options()
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
        self.driver = None
        self.game_index_new = ''
        self.game_index_ended = MCFStorage.get_gameid()
        
        self.PASSAGES = 0
        self.RESTART_REQUIRED = False

        self.URL: str = ''
        self.ACTIVE_TOTAL_VALUE = 0
    
    def start(self):
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.maximize_window()
        time.sleep(3)
        autogui.click(x=1896, y=99) #disable infobar
        time.sleep(3)
    
    def force_quit(self):
        try:
            self.PASSAGES = 0
            self.driver.quit()
        except:
            ...
            
        self.RESTART_REQUIRED = True

    def open_mobile_page(self):
        self.driver.get(self.URL + '/' + self.game_index_ended.replace('_', '/') + '?platform_type=mobile')
    
    def open_league_page(self):
        with open(PATH.MIRROR_PAGE, 'r') as ex_url:
            self.URL = ex_url.read().strip()
        
        try:
            self.driver.get(url=self.URL + '?platform_type=desktop')
            time.sleep(5)
            return True
        except (TimeoutException, WebDriverException):
            return False

    def remove_cancel(self):
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, MelCSS.BUTTON_REJECT_LIVE)
            if element is not None:
                element.click()
                
        except (NoSuchElementException, 
                TimeoutException,
                StaleElementReferenceException,
                WebDriverException):
            pass

    def delay(self, second: int):
        time.sleep(second)

    def stream_close(self):
        autogui.close_league_stream()

    def stream_fullscreen(self):
        autogui.click(x=1871, y=361)
        time.sleep(2.5)


    def is_total_coeff_opened(self, end_check=False):

        try:
            game_market_contents = self.driver.find_element(By.CSS_SELECTOR, MelCSS.MARKETS_CONTENT)
            markets = game_market_contents.find_elements(By.CSS_SELECTOR, MelCSS.MARKETS_GROUP)

            if end_check:
                lock_ico = markets[0].find_elements(By.CSS_SELECTOR, MelCSS.LOCK_ICON)
                if len(lock_ico) == 0: return True
            
            else:
                for _, mrk in enumerate(markets):
                    btn = mrk.find_element(By.CSS_SELECTOR, MelCSS.MARKET_BUTTON)
                    mrk_text = btn.text
                    if mrk_text.endswith('Б'):
                        total_value = mrk_text.split()[0]
                        self.ACTIVE_TOTAL_VALUE = total_value
                        # print(total_value)
                        lock_ico = mrk.find_elements(By.CSS_SELECTOR, MelCSS.LOCK_ICON)
                        if len(lock_ico) == 0:
                            return True
        except:
            ...
            
        return False
    
    def predicts_is_accepted(self, message):

        predict_direction = message.split()[1][-1]
        predict_flet = message.split()[-1].split('_')[1].replace(TelegramStr.ARROW_DOWN, '')
        active_total = float(self.ACTIVE_TOTAL_VALUE)

        if predict_direction == 'Б' and active_total < 117.5:
            
            if CF.VAL.tb_approve != 7:
                CF.VAL.tb_approve += 1
                return
            return True

        if predict_direction == 'М' and active_total > 96.5:

            if predict_flet == "0.5" and CF.VAL.tl_approve != 3:
                CF.VAL.tl_approve += 1
                return

            return True
            
    def send_predict(self, message: str, idx: int):

        if self.is_total_coeff_opened():
            if not self.predicts_is_accepted(message=message):
                return
            message: str = message.replace('110.5', self.ACTIVE_TOTAL_VALUE)

            TGApi.post_request(message=message, message_type='predict')
            logger.info(message)

            time.sleep(5)

            if self.is_total_coeff_opened():
                MCFStorage.rgs_predicts_monitor(message=message, idx=idx)
            else:
                CF.VAL.pr_cache = 'closed'
       
    def generate_predict(self, score):

        if score['time'] > 660:
            return
        
        # if score['time'] in TRACE_RANGE and not CF.SW.tracer.is_active():
        #     Trace.add_tracing(score=score)

        if not CF.VAL.pr_cache:
            PR.sc = copy.deepcopy(score)
            PR.prepare_predict_values()
            main_predict = PR.gen_main_predict()
            if main_predict:
                self.send_predict(message=main_predict[0], idx=main_predict[1])

    def awaiting_for_start(self):

        # passages = 0

        while True:

            try:
                games = self.driver.find_elements(By.CSS_SELECTOR, MelCSS.GAMES_DASHBOARD)
                aram_title_outer = games[0].find_element(By.CSS_SELECTOR, MelCSS.ARAM_TITLE_OUTER)
                aram_title_inner: str = aram_title_outer.find_element(By.CSS_SELECTOR, MelCSS.ARAM_TITLE_INNER).get_attribute('innerText')
              
                if aram_title_inner == 'All Random All Mid':
                    game_link = games[0].find_element(By.CSS_SELECTOR, MelCSS.ARAM_GAME_LINK).get_attribute('href')
                    game_index = '_'.join(game_link.split('/')[7:])
                    
                    if game_index != self.game_index_ended:
                        logger.info('Gamelink changed, refreshing driver')
                        self.open_league_page()
                        time.sleep(6)
                        self.game_index_new = game_index
                        self.game_index_ended = game_index
          
                    if game_index == self.game_index_new:
                        stream_btn = games[0].find_element(By.CSS_SELECTOR, MelCSS.SPAN_OPEN_STREAM)
                        stream_btn.find_element(By.CSS_SELECTOR, MelCSS.BUTTON_OPEN_STREAM).click()
                        time.sleep(2)

                        if pillow.is_game_started():
                            logger.info('Game started: (from comparing stream)')
                            self.game_index_new = ''
                            MCFStorage.save_gameid(self.game_index_ended)
                            # self.open_activegame_page()
                            return
                        else:
                            stream_btn.click()
                    else:
                        self.remove_cancel()

            except (AttributeError, IndexError, NoSuchElementException,
                    StaleElementReferenceException) as ex_:
                ...
            except Exception as ex_:
                logger.info(self.game_index_new)
                logger.info(self.game_index_ended)
                logger.warning(ex_)

            time.sleep(1)
            self.remove_cancel()

            # print(self.PASSAGES)
            if self.PASSAGES in (40, 80, 120):
                if not self.open_league_page():
                    self.force_quit()
                    return
                self.PASSAGES += 1
            elif self.PASSAGES == 160:
                self.force_quit()
                return
            else:
                time.sleep(0.75)
                self.PASSAGES += 1
            