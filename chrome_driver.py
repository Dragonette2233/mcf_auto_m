import time
import logging
import modules.mcf_autogui as mcf_autogui
import modules.mcf_pillow as mcf_pillow
from modules.mcf_storage import MCFStorage
from modules.mcf_tracing import Trace
from global_data import Validator
from tg_api import TGApi
from mcf_data import Switches, StatsRate, MIRROR_PAGE
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
        self.CSS_BTN_STREAM = 'button.ui-dashboard-game-button.dashboard-game-action-bar__item'
        self.CSS_BTN_REJECT_LIVE = 'button.ui-button.dashboard-redirect-message-timer__btn.ui-button--size-m.ui-button--theme-gray.ui-button--rounded'
        self.CSS_BTN_FOR_BET = 'li.ui-dashboard-champ.dashboard-champ.dashboard__champ.ui-dashboard-champ--theme-gray'
        self.CSS_TABLE_GAMES = 'li.ui-dashboard-champ.dashboard-champ.dashboard__champ.ui-dashboard-champ--theme-gray'
        self.URL_MAIN = 'https://lite.1xbet-new.com/ru/live/cyber-zone/league-of-legends'
        self.options = Options()
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
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
        mcf_autogui.click(x=1896, y=99) #disable infobar
        time.sleep(3)

    def force_quit(self):
        try:
            self.driver.quit()
        except:
            ...
            
        self.RESTART_REQUIRED = True

    def open_activegame_page(self):

        self.driver.get(self.URL + '/' + self.game_index_ended.replace('_', '/') + '?platform_type=mobile')

    def open_league_page(self):
        with open(MIRROR_PAGE, 'r') as ex_url:
            self.URL = ex_url.read().strip()
        
        if self.URL.startswith('https://mel'):
            Validator.active_mel_mirror = True
        else:
            Validator.active_mel_mirror = False
        
        
        try:
            self.driver.get(url=self.URL + '?platform_type=desktop')
            time.sleep(6)
            return True
        except TimeoutException:
            return False
        except WebDriverException:
            return False
        # time.sleep(6)

    def remove_cancel(self):
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, self.CSS_BTN_REJECT_LIVE)
            if element is not None:
                element.click()
        except (NoSuchElementException, TimeoutException, StaleElementReferenceException):
            pass

    def delay(self, second: int):
        time.sleep(second)

    def stream_close(self):
        mcf_autogui.close_league_stream()

    def stream_fullscreen(self):
        if Validator.active_mel_mirror:
            mcf_autogui.click(x=1871, y=361)
        else:
            mcf_autogui.click(x=1871, y=325)
        time.sleep(2.5)

    def is_total_coeff_opened(self, end_check=False):

        try:
            game_market_contents = self.driver.find_element(By.CSS_SELECTOR, 'div.game-markets-content')
            markets = game_market_contents.find_elements(By.CSS_SELECTOR, 'div.ui-accordion.game-markets-group')
        
            for i, mrk in enumerate(markets):
                btn = mrk.find_element(By.CSS_SELECTOR, 'span.ui-market__name')
                mrk_text = btn.text
                if mrk_text.endswith('Б'):
                    total_value = mrk_text.split()[0]
                    # print(total_value)
                    lock_ico = mrk.find_elements(By.CSS_SELECTOR, 'span.ico.ui-market__lock')
                    if len(lock_ico) == 0:
                        if not end_check:
                            self.ACTIVE_TOTAL_VALUE = total_value
                        return True
                    else:
                        return False
        except:
            return

    # def check_if_opened(self):
       
    #     try:
    #         games = self.driver.find_elements(By.CSS_SELECTOR, 'li.ui-dashboard-champ.dashboard-champ.dashboard__champ.ui-dashboard-champ--theme-gray')
    #         aram_title_outer = games[0].find_element(By.CSS_SELECTOR, 'span.caption.ui-dashboard-champ-name__caption.caption--size-m')
    #         aram_title_inner: str = aram_title_outer.find_element(By.CSS_SELECTOR, 'span.caption__label').get_attribute('innerText')
              
    #         if aram_title_inner == 'All Random All Mid':
    #             game_links = games[0].find_elements(By.CSS_SELECTOR, 'a.dashboard-game-block__link.dashboard-game-block-link')# .get_attribute('href')
    #             game_link = game_links[0].get_attribute('href')
    #             # ico ui-market__lock ico--lock
    #             game_index = '_'.join(game_link.split('/')[7:])
    #             if game_index == self.game_index_ended:
    #                 button = games[0].find_element(By.CSS_SELECTOR, 'button.ui-market.ui-market--nameless')
    #                 # button = games[0].find_element(By.XPATH, '//*[@id="app"]/div[3]/div[1]/div/div[2]/main/div[2]/div/div/div[2]/div/ul/li[1]/ul/li/div[2]/span/button[1]')
    #                 try:
    #                     lock_icon = button.find_element(By.CSS_SELECTOR, 'span.ico.ui-market__lock.ico--lock')
    #                     return False
    #                 except:
    #                     Switches.coeff_opened = True
    #                     return True
    #                 # if not button.get_attribute('disabled'):
    #                 #     Switches.coeff_opened = True
    #                 #     return True
    #     except (NoSuchElementException, IndexError, Exception):
    #         pass
            
    #     return False
    
    def send_predict(self, predictions: dict, key: str):

        for message, conditions in predictions.items():
            if any(conditions):
                if self.is_total_coeff_opened():
                    if int(float(self.ACTIVE_TOTAL_VALUE)) not in range(92, 123):
                        break
                    message: str = message.replace('110.5', self.ACTIVE_TOTAL_VALUE)
                    MCFStorage.rgs_predicts_monitor(message=message,
                                                    key=key)
                    TGApi.send_simple_message(message)
                    logger.info(message)
                else:
                    TGApi.send_simple_message(message.replace('🔽', '🔻').replace('🔼', '🔺'))
                    Validator.predict_value_flet[key] = 'closed'
                    logger.info(message)
                break

    def generate_predict(self, score):

        # is_opened = self.check_if_opened()
        gametime = score["time"]
        
        # if not Validator.tracer["300s"] and gametime in range(295, 310):
        #     Trace.add_tracing(timestamp='300s', score=score)
        # if not Validator.tracer["420s"] and gametime in range(417, 425):
        #     Trace.add_tracing(timestamp='420s', score=score)
        # if not Validator.tracer["540s"] and gametime in range(540, 550):
        #     Trace.add_tracing(timestamp='540s', score=score)

        blue_kills = score["blue_kills"] # "blue_kiils": 49,
        red_kills = score["red_kills"] # "red_kills": 43,
        blue_towers = score["blue_towers"] # "blue_towers": 3,
        red_towers = score["red_towers"] # "red_towers": 1,
        blue_gold = score["blue_gold"]
        red_gold = score["red_gold"]
        blue_t1_hp = score["blue_t1_hp"]
        red_t1_hp = score["red_t1_hp"]

        all_kills = blue_kills + red_kills
        module_kills = abs(blue_kills - red_kills)
        module_gold = abs(blue_gold - red_gold)
        gold_equals = module_gold < 0.6

        blue_gold_leader = blue_gold > red_gold and module_gold > 1.65
        red_gold_leader = red_gold > blue_gold and module_gold > 1.65
        blue_gold_winner = blue_gold > red_gold and module_gold > 2.8
        red_gold_winner = red_gold > blue_gold and module_gold > 2.8
        # blue_gold_winner = blu
        
        blue_leader = ( (blue_towers != 0 and red_towers == 0) or (blue_t1_hp > 75 and red_t1_hp < 27) ) and blue_gold_winner
        red_leader = ( (red_towers != 0 and blue_towers == 0) or (red_t1_hp > 75 and blue_t1_hp < 27) ) and red_gold_winner

        # blue_light = blue_kills > red_kills and blue_gold_leader
        # red_light = red_kills > blue_kills and red_gold_leader
        light_leader = blue_gold_leader or red_gold_leader

        straight_leader = blue_leader or red_leader
        two_towers_destroyed = blue_towers + red_towers > 1
        towers_leader = blue_towers > 1 or red_towers > 1
        hard_towers_leader = (red_towers == 0 and blue_towers > 1) or (blue_towers == 0 and red_towers > 1)
        no_towers_destroyed = (blue_towers == 0 and red_towers == 0) and (blue_t1_hp > 65 and red_t1_hp > 65)
        towers_still_healthy = (blue_towers == 0 and red_towers == 0) and (blue_t1_hp > 35 and red_t1_hp > 35)
        full_towers_health = (blue_towers == 0 and red_towers == 0) and (blue_t1_hp > 75 and red_t1_hp > 75)
        some_tower_destroyed = (blue_towers != 0 or red_towers != 0) or (blue_t1_hp < 25 or red_t1_hp < 25)
        some_tower_toched = blue_t1_hp <= 75 or red_t1_hp <= 75
        t1_towers_destroyed = (blue_towers == 1 and red_towers == 1) or (blue_t1_hp < 25 and red_t1_hp < 25)
        
        if not Validator.predict_value_flet['stats']:

            spredictions = {
                '🔽S_PR 110.5М FL_0.5🔽': [
                    (StatsRate.tl_accepted() and all_kills < 30 and some_tower_destroyed and gametime > 400),
                    (StatsRate.tl_accepted() and all_kills < 24 and gametime > 400)
                ],
                '⬆️S_PR 110.5Б FL_0.5⬆️': [
                    (StatsRate.tb_accepted() and all_kills > 45 and module_kills < 7 and gametime < 360),
                    (StatsRate.tb_accepted() and StatsRate.tanks_in_teams())
                ]
            }

            self.send_predict(predictions=spredictions, key='stats')

        if not Validator.predict_value_flet['main']:
            
            predictions = {
                '🔼PR 110.5Б FL_1🔼': [
                    (all_kills >= 50 and module_kills < 4 and no_towers_destroyed and gametime < 480 and gold_equals),

                ],
                '🔼PR 110.5Б FL_0.75🔼': [
                    # (all_kills >= 50 and module_kills < 3 and no_towers_destroyed and gametime < 360 and gold_equals),
                    (all_kills >= 80 and module_kills < 7 and t1_towers_destroyed and gametime < 480 and gold_equals),
                ],
                '🔼PR 110.5Б FL_0.5🔼': [
                    (all_kills >= 50 and module_kills < 6 and no_towers_destroyed and (gametime in range(481, 540)) and gold_equals),
                    (all_kills >= 48 and module_kills < 5 and towers_still_healthy and gametime < 420 and gold_equals),
                    (all_kills >= 40 and module_kills < 5 and full_towers_health and gametime < 420 and StatsRate.tanks_in_teams()),
                ],

                '🔽PR 110.5М FL_1🔽': [

                    (all_kills < 16 and straight_leader and gametime > 240),
                    (all_kills < 22 and straight_leader and gametime > 300),
                    (all_kills < 28 and straight_leader and gametime > 360),
                    (all_kills < 34 and straight_leader and gametime > 420),
                    (all_kills < 40 and straight_leader and gametime > 540),
                    (all_kills < 50 and straight_leader and module_kills > 9 and gametime > 540)
                    
                ],
                '🔽PR 110.5М FL_0.75🔽': [

                    (all_kills < 12 and some_tower_destroyed and gametime > 240),
                    (all_kills < 16 and some_tower_destroyed and gametime > 300),
                    (all_kills < 20 and some_tower_destroyed and gametime > 360),
                    (all_kills < 24 and some_tower_destroyed and gametime > 420),
                    (all_kills < 28 and some_tower_destroyed and gametime > 480),
                    (all_kills < 38 and two_towers_destroyed and gametime > 480),
                    (all_kills < 50 and towers_leader),
                    
                ],
                '🔽PR 110.5М FL_0.5🔽': [
                    
                    (all_kills < 10 and some_tower_toched and gametime > 240),
                    (all_kills < 16 and some_tower_toched and gametime > 300),
                    (all_kills < 22 and some_tower_toched and light_leader and gametime > 360),
                    (all_kills < 22 and gametime > 420),
                    (all_kills < 42 and gametime > 420 and hard_towers_leader),
                    (all_kills < 28 and light_leader and gametime > 480),
                    (all_kills <= 30 and module_kills >= 9 and gametime > 420),
                    (all_kills <= 38 and module_kills >= 15 and gametime > 420)
                ]

            }

            self.send_predict(predictions=predictions, key='main')

    def notify_when_starts(self):

        while True:

            try:
                games = self.driver.find_elements(By.CSS_SELECTOR, 'li.ui-dashboard-champ.dashboard-champ.dashboard__champ.ui-dashboard-champ--theme-gray')
                aram_title_outer = games[0].find_element(By.CSS_SELECTOR, 'span.caption.ui-dashboard-champ-name__caption.caption--size-m')
                aram_title_inner: str = aram_title_outer.find_element(By.CSS_SELECTOR, 'span.caption__label').get_attribute('innerText')
              
                if aram_title_inner == 'All Random All Mid':
                    game_link = games[0].find_element(By.CSS_SELECTOR, 'a.dashboard-game-block__link.dashboard-game-block-link').get_attribute('href')
                    game_index = '_'.join(game_link.split('/')[7:])

                    if game_index != self.game_index_ended:
                        logger.info('Gamelink changed, refreshing driver')
                        self.open_league_page()
                        time.sleep(6)
                        self.game_index_new = game_index
                        self.game_index_ended = game_index

                    if game_index == self.game_index_new:
                        stream_btn = games[0].find_element(By.CSS_SELECTOR, 'span.dashboard-game-action-bar__group')
                        stream_btn.find_element(By.CSS_SELECTOR, self.CSS_BTN_STREAM).click()
                        time.sleep(2)

                        if mcf_pillow.is_game_started():
                            logger.info('Game started: (from comparing stream)')
                            self.game_index_new = ''
                            MCFStorage.save_gameid(self.game_index_ended)
                            # self.open_activegame_page()
                            return
                        else:
                            stream_btn.click()
                            time.sleep(1)
                    else:
                        self.remove_cancel()
                        time.sleep(1)
            except AttributeError as ex_:
                # logger.warning(ex_)
                time.sleep(1)
            except IndexError as ex_:
                # logger.warning(ex_)
                time.sleep(1)
            except (NoSuchElementException, StaleElementReferenceException) as ex_:
                # logger.warning(ex_)
                time.sleep(1)
            except Exception as ex_:
                logger.info(self.game_index_new)
                logger.info(self.game_index_ended)
                logger.warning(ex_)
                # logger.warning(exc_info=True)
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
            