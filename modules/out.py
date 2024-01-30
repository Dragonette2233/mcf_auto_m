
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium import webdriver
from modules import mcf_styles

from mcf_riot_api import (
    TGApi,
    RiotAPI,  
    MCFException,
)
from mcf_data import (
    REGIONS_TUPLE,
    currentGameData,
    ALL_CHAMPIONS_IDs,
    SPECTATOR_FILE_PATH,
    SPECTATOR_MODE,
    Switches,
    Validator
)


class MCF_Gamechecker:
    def __init__(self, master: MCFWindow) -> None:
        self.parent = master
        self.entry = mcf_styles.Entry(width=19)
        self.endtime = mcf_styles.Label(fsize=9)
        self.win = mcf_styles.Label(fsize=26, height=3, width=14, hlb='#370d3d')
        self.lastgame = mcf_styles.Label(fsize=9, hlb='#370d3d', width=8)
        self.run_button = mcf_styles.Button(display=master.button_images['Run'],
                                            command=lambda: MCFThread(
                                                    func=self.awaiting_game_end
                                            ).start())
        self.spectate_button = mcf_styles.Button(display=master.button_images['Spec'],
                                                 command=self.spectate_active_game)
        self.search_button = mcf_styles.Button(display=master.button_images['Search'],
                                               command=lambda: MCFThread(
                                                    func=self.search_for_game
                                               ).start())
        self.arrow_button = mcf_styles.Button(display=master.button_images['Arrow'],
                                              command=self.restore_nickname_for_search)

        self.entry.place(in_=master, x=11, y=343)
        self.search_button.place(in_=master, x=11, y=370)
        self.arrow_button.place(in_=master, x=120, y=370)

    # Decorator for handling connection in methods
    def connection_handler(func):
        def wrapper(self: "MCF_Gamechecker", *args, **kwargs):
            
            while True:
                try:
                    func(self, *args, **kwargs)
                    break
                except MCFException as ex:
                    self.parent.info_view.exception(str(ex) + ' | Press refresh to stop')
                    time.sleep(2.5)
            
        return wrapper
                
    def _refresh(self):

        for widget in self.spectate_button, self.run_button, \
                       self.endtime, self.win, self.lastgame:
            widget.place_forget()
        
        self.entry.delete(0, 'end')

    def restore_nickname_for_search(self):

        stored_nickname = MCFStorage.get_selective_data(route=('CheckerLast',))
        self.entry.insert(0, stored_nickname)

    @connection_handler
    @disable_button_while_running(object_='obj_gamechecker', 
                                  buttons=('search_button', 'run_button', 'arrow_button'))
    def search_for_game(self):

        currentGameData.region, currentGameData.area = None, None
        summoner_name = self.entry.get().split(':')
        self.endtime.place_forget()
        self.lastgame.place_forget()
        
        if len(summoner_name) != 2:
            self.parent.info_view.exception('Use ":"')
            return
        
        for short, code, area in REGIONS_TUPLE:
            if summoner_name[1].lower() == short or summoner_name[1].lower() == code:
                currentGameData.region = code
                currentGameData.area = area
                break

        if currentGameData.region is None:
            self.parent.info_view.exception('Wrong region')
            return
        
        self.parent.info_view.notification('Searching...')

        summoner_data = RiotAPI.get_summoner_puuid(region=currentGameData.region, name=summoner_name[0])

       
        if summoner_data == 404:
            self.parent.info_view.exception('Summoner not found')
            return
        
        currentGameData.summoner_puuid = summoner_data['puuid']
        response_activegame = RiotAPI.get_active_by_summonerid(region=currentGameData.region, 
                                                               summid=summoner_data['id'],
                                                               status=True)
            
        # Writing nick and region to json
        MCFStorage.write_data(route=('CheckerLast',), value=self.entry.get())
        
        # print(response_activegame)
        if response_activegame.status_code != 200:
            self.parent.info_view.notification('Loading last game')
            self.show_lastgame_info()
        else:
            
            '''Запрос активной игры'''

            currentGameData.response = response_activegame.json()
            currentGameData.game_id = str(currentGameData.response['gameId']) # 1237890
            currentGameData.match_id = currentGameData.region.upper() + '_' + currentGameData.game_id # EUW_12378912
            currentGameData.champions_ids = [currentGameData.response['participants'][p]['championId'] for p in 
                                             range(10)]
            
            champions_names = [ALL_CHAMPIONS_IDs.get(currentGameData.champions_ids[i]) for i in range(10)]

            self.parent.place_character_icons(champions_names)
            
            self.spectate_button.place(x=427, y=342)
            self.run_button.place(x=427, y=296)
            self.parent.info_view.hide_info()

            self.parent.obj_aram.global_stats_values = stats_by_roles.get_aram_statistic(
                blue_entry=champions_names[0:5],
                red_entry=champions_names[5:10]
            )

            # if Switches.bot_activity:
            TGApi.gamestart_notification(
                nickname=self.entry.get(),
                champions=champions_names,
                statsrate=self.parent.obj_aram.global_stats_values
            )

        return 0
        # canvas.info_manager(forget=True)
    
    def spectate_active_game(self):
        import os
        import subprocess
        list_task = os.popen('tasklist /FI "IMAGENAME eq League of Legends*"').readlines()
        
        if len(list_task) != 1:
            self.parent.info_view.exception('Game already running')
            return
        
        self.parent.info_view.success('Launching spectator...')

        enc_key = currentGameData.response['observers']['encryptionKey']
        spectator = SPECTATOR_MODE.format(reg=currentGameData.region)
        args = spectator, enc_key, str(currentGameData.game_id), currentGameData.region.upper()

        MCFStorage.write_data(route=("0", ), value=str(args))

        subprocess.call([SPECTATOR_FILE_PATH, *args])

    @disable_button_while_running(object_='obj_gamechecker', 
                                  buttons=('search_button', 'run_button', 'arrow_button'))
    def awaiting_game_end(self, driver: webdriver.Chrome = None):
    
        Switches.request = True
        self.parent.canvas.start_circle()
        self.parent.info_view.success('Matcher checker started')

        while Switches.request:
            
            while True and Switches.request:
                try:
                    finished_game = RiotAPI.get_match_by_gameid(area=currentGameData.area, 
                                                        gameid=currentGameData.match_id, 
                                                        status=True)
                    break
                except MCFException as ex:
                    self.parent.info_view.exception(str(ex) + ' | Press refresh to stop')
                    time.sleep(2.5)
                
            if finished_game.status_code == 200:

                response = finished_game.json()
                kills = sum(response['info']['participants'][k]['kills'] for k in range(10))
                time_stamp = list(divmod(response['info']['gameDuration'], 60))
                
                if time_stamp[1] < 10: 
                    time_stamp[1] = f"0{time_stamp[1]}"


                # Coeff closed check
                is_disabled = True

                if driver is not None:
                    try:
                        games = driver.find_elements(By.CSS_SELECTOR, 'li.ui-dashboard-champ.dashboard-champ.dashboard__champ.ui-dashboard-champ--theme-gray')
                    except Exception as ex_:
                        games = []
                        # print(ex_)
                        
                    try:
                        button = games[0].find_element(By.CSS_SELECTOR, 'button.ui-market.ui-market--nameless')
                        if not button.get_attribute('disabled'):
                            is_disabled = False
                            Switches.coeff_opened = True
                    except NoSuchElementException:
                        pass
                    except IndexError:
                        pass

                if response['info']['teams'][0]['win']: 
                    team = ('blue', '1')
                    TGApi.winner_is(team='blue', kills=kills, timestamp=f"[{time_stamp[0]}:{time_stamp[1]}]", disabled=is_disabled)
                else: 
                    team = ('red', '2')
                    TGApi.winner_is(team='red', kills=kills, timestamp=f"[{time_stamp[0]}:{time_stamp[1]}]", disabled=is_disabled)

                # Validator.stats_register['W1_res'] = 1 if team[0] == 'blue' else 0
                # Validator.stats_register['W2_res'] = 1 if team[0] == 'red' else 0
                Validator.total_register['W1_res'] = 1 if kills > 110 else 0
                Validator.total_register['W2_res'] = 1 if kills < 110 else 0

                # MCFStorage.stats_monitor(validor=Validator.stats_register)
                MCFStorage.stats_monitor(validor=Validator.total_register)

                for key in Validator.stats_register:
                    Validator.stats_register[key] = 0
                    Validator.total_register[key] = 0

                self.win['text'] = f"{team[0].upper()} SIDE (П{team[1]})\n|  {kills}  |"
                self.win['bg'] = team[0]
                self.endtime['text'] = f" {time_stamp[0]}:{time_stamp[1]} "
                self.endtime['highlightbackground'] = team[0]
                self.endtime.place(x=223, y=275)
                self.win.place(x=92, y=143)
                self.spectate_button.place_forget()
                self.run_button.place_forget()
                Switches.request = False
                # playsound(PAPICH_SONG_PATH)
                finished_game.close()
                break
            
            time.sleep(1.25)

    @connection_handler
    def show_lastgame_info(self):
        
        games_list = RiotAPI.get_matches_by_puuid(area=currentGameData.area, 
                                                  puuid=currentGameData.summoner_puuid)
        
        if len(games_list) == 0:

            self.parent.info_view.exception('No games for this summoner')
            return

        lastgame = RiotAPI.get_match_by_gameid(area=currentGameData.area, gameid=games_list[0])
        
        # currentGameData.players_count = lastgame['info']['participants'] # [0] {}, [1] {}, 2 {}, ... [10] {}
        
        try:
            if len(lastgame['info']['participants']) < 10:
                self.parent.info_view.exception('Summoner data corrupted')
                return
        except:
            self.parent.info_view.exception('Summoner data corrupted')
            return
        
        currentGameData.teams_info = lastgame['info']['teams'] # [0] {}, [1] .
        currentGameData.champions_ids = [lastgame['info']['participants'][p]['championId'] for p in 
                                             range(10)]
        
        
        champions_names = [ALL_CHAMPIONS_IDs.get(currentGameData.champions_ids[i]) for i in range(10)]
        Validator.ended_game_characters = champions_names[0:5].copy()

        self.parent.place_character_icons(champions_names, place=3, activegame=False)
        kills = sum(lastgame['info']['participants'][k]['kills'] for k in range(10))
        
        if currentGameData.teams_info[0]['win']:
            text, color = f' W1 | {kills} ', 'blue'
        else:
            text, color = f' W2 | {kills} ', 'red'
            
        timestamp = list(divmod(lastgame['info']['gameDuration'], 60))
        if timestamp[1] < 10:
            timestamp[1] = f"0{timestamp[1]}"
        
        self.endtime.configure(
                text=f"  {timestamp[0]}:{timestamp[1]}  ",
                highlightbackground=color
            )
        
        self.lastgame.configure(
                text=text, # bg=color
                highlightbackground=color
            )

        self.lastgame.place(x=183, y=342)
        self.endtime.place(x=309, y=342)
        self.parent.info_view.hide_info()