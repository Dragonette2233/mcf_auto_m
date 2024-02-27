import logging
import time
from global_data import (
    ActiveGame,
    Validator,
)
from tg_api import TGApi
from mcf_riot_api import RiotAPI
from mcf_data import (
    REGIONS_TUPLE,
    ALL_CHAMPIONS_IDs,
    SPECTATOR_MODE,
    SPECTATOR_FILE_PATH,
    Switches,
    StatsRate,
)
import os
import itertools
import modules.mcf_autogui as mcf_autogui
from chrome_driver import Chrome
from modules.ssim_recognition import RecognizedCharacters as SsimReco
from modules.mcf_storage import MCFStorage
from modules.mcf_tracing import Trace
from modules import mcf_utils
logger = logging.getLogger(__name__)


class MCFApi:
    
    @classmethod
    def get_characters(cls):

        while True:
            if not ActiveGame.nick_region:
                logger.info('Comparing icons...')
                team_blue = SsimReco(team_color='blue')
                team_red = SsimReco(team_color='red')
                team_blue.run()
                team_red.run()

            logger.info(team_blue.characters)
            logger.info(team_red.characters)
            if len(team_blue.characters) < 5 and len(team_red.characters) < 5:
                if Validator.recognition == 40:
                    Validator.recognition = 0
                    return None
                
                Validator.recognition += 1
                logger.warning('Recognizing Failed. Continue...')
                time.sleep(2)
                continue
            else:
                StatsRate.calculate(
                    team_blue=team_blue.characters,
                    team_red=team_red.characters
                )

                # TGApi.gamestart_notification(
                #     team_blue=' '.join(team_blue.characters),
                #     team_red=' '.join(team_red.characters)
                # )
                # logger.info('Team BLUE: {team_blue}'.format(team_blue=' '.join(team_blue.characters)))
                # logger.info('Team RED: {team_red}'.format(team_red=' '.join(team_red.characters)))
                return {
                    'blue': team_blue.characters,
                    'red': team_red.characters
                }

    @classmethod   
    def close_league_of_legends(cls):

        list_task = os.popen('tasklist /FI "IMAGENAME eq League of Legends*"').readlines()
        if len(list_task) == 1:
            logger.info('Game not launched')
            return
        
        list_task[3] = list_task[3].replace(' ', '')
        process_pid = list_task[3].split('exe')[1].split('Console')[0]
        os.popen(f'taskkill /PID {process_pid} /F')
        # app_blueprint.delete_screenscore()
        logger.info('League of Legends closed')

    @classmethod
    def delete_scoreboard(cls):

        MCFStorage.save_score(stop_tracking=True)
        try:
            # os.remove(os.path.join('images_lib', 'scorecrop.png'))
            os.remove(os.path.join('.', 'images_lib', 'buildcrop.png'))
        except FileNotFoundError:
            pass


    @classmethod
    def get_games_by_character(cls, character: str):

        all_matches = []

        matches_by_regions_api = MCFStorage.get_selective_data(route=('MatchesAPI', ))
        matches_by_regions_poro = MCFStorage.get_selective_data(route=('MatchesPoroRegions', ))
        matches_by_regions_poro_bronze = MCFStorage.get_selective_data(route=('MatchesPoroBronze', ))

        all_matches += [item for sublist in matches_by_regions_api.values() for item in sublist]
        all_matches += [item for sublist in matches_by_regions_poro.values() for item in sublist]
        all_matches += [item for sublist in matches_by_regions_poro_bronze.values() for item in sublist]
        all_matches += MCFStorage.get_selective_data(route=('MatchesPoroGlobal', ))
            
        finded_games = set()

        for match in all_matches:
            if character in match:
                finded_games.add(match)

        return list(finded_games)
    
    @classmethod
    def parse_from_all_sources(cls, char_r):
        
        while True:
            try:
                logger.info('Parsing from RiotAPI and Poro...')
                mcf_utils.async_poro_parsing(champion_name=char_r) # Parse full PoroARAM by region
                mcf_utils.async_poro_parsing(champion_name=char_r, bronze=True) # Parse for Bronze+
                mcf_utils.direct_poro_parsing(red_champion=char_r) # Parse only main page PoroARAM
                mcf_utils.async_riot_parsing() # Parse featured games from Riot API
                logger.info('Games parsed succesfully.')
                break
            except Exception as ex:
                logger.warning(str(ex))
                time.sleep(4)
                continue
    
    @classmethod
    def count_of_common(cls, sequence_1, sequence_2) -> int:

         set_1 = set([i.lower().capitalize() for i in sequence_1])
         set_2 = set([i.lower().capitalize() for i in sequence_2])
        
         # Нахождение пересечения множеств
         common_elements = set_1.intersection(set_2)
         return len(common_elements)

    @classmethod
    def finded_game(cls, teams: dict):

        team_cycle = itertools.cycle(zip(teams['blue'], teams['red']))

        Validator.finded_game_characerts = teams['blue'].copy()

        for char_b, char_r in team_cycle:

            cls.parse_from_all_sources(char_r=char_r)
            games_by_character: list[str] = cls.get_games_by_character(character=char_b)

            for charlist in games_by_character:
                nicknames = charlist.split('-|-')[1].split('_|_')
                characters = charlist.split('-|-')[0].split(' | ')
                common_elements = cls.count_of_common(sequence_1=characters, sequence_2=Validator.finded_game_characerts)

                if common_elements >= 4:
                    return nicknames
            else:
                logger.warning('No games for {char_r} -- {char_b}. CD 3s'.format(char_r=char_r, char_b=char_b))
                Validator.findgame += 1

                if Validator.findgame == 15:
                    Validator.findgame = 0
                    return None
                time.sleep(2)
    
    @classmethod
    def show_lastgame_info(cls):
        
        games_list = RiotAPI.get_matches_by_puuid(area=ActiveGame.area, 
                                                  puuid=ActiveGame.puuid)
        
        if len(games_list) == 0:

            logger.warning('No games for this summoner')
            return

        lastgame = RiotAPI.get_match_by_gameid(area=ActiveGame.area, gameid=games_list[0])
        
        # currentGameData.players_count = lastgame['info']['participants'] # [0] {}, [1] {}, 2 {}, ... [10] {}
        
        try:
            if len(lastgame['info']['participants']) < 10:
                logger.warning('Summoner data corrupted')
                return
        except:
            logger.warning('Summoner data corrupted')
            return
        
        teams_info = lastgame['info']['teams'] # [0] {}, [1] .
        champions_ids = [lastgame['info']['participants'][p]['championId'] for p in 
                                             range(10)]
        
        
        champions_names = [ALL_CHAMPIONS_IDs.get(champions_ids[i]) for i in range(10)]
        timestamp = list(divmod(lastgame['info']['gameDuration'], 60))
        if timestamp[1] < 10: 
            timestamp[1] = f"0{timestamp[1]}"
        Validator.ended_blue_characters = champions_names[0:5].copy()
        Validator.ended_red_characters = champions_names[5:].copy()
        Validator.ended_kills = sum(lastgame['info']['participants'][k]['kills'] for k in range(10))
        Validator.ended_winner = 'blue' if teams_info[0]['win'] else 'red'
        Validator.ended_time = f"{timestamp[0]}:{timestamp[1]}"

    @classmethod
    def get_aram_statistic(cls, blue: list, red: list):
        from modules import stats_by_roles

        return stats_by_roles.get_aram_statistic(
                blue_entry=blue,
                red_entry=red,
            )

    @classmethod
    def search_game(cls, nick_region: str):
       
        summoner_name = nick_region.split(':')
        
        for short, code, area in REGIONS_TUPLE:
            if summoner_name[1].lower() == short or summoner_name[1].lower() == code:
                ActiveGame.region = code
                ActiveGame.area = area
                break

    
        logger.info('Searching...')

        print(summoner_name[0].split('#')[0])

        summoner_data = RiotAPI.get_summoner_puuid(region=ActiveGame.region, name=summoner_name[0].split('#')[0])

       
        if summoner_data == 404:
            logger.warning('Summoner not found')
            return
        elif summoner_data == 403:
            logger.error('API key wrong or exipred')
        
        ActiveGame.puuid = summoner_data['puuid']
        response_activegame = RiotAPI.get_active_by_summonerid(region=ActiveGame.region, 
                                                               summid=summoner_data['id'],
                                                               status=True)
            
    
        if response_activegame.status_code != 200:
            logger.info('Loading last game')
            cls.show_lastgame_info()
        else:
            
            '''Запрос активной игры'''

            response = response_activegame.json()
            if response['gameMode'] != 'ARAM':
                return False
            
            game_id = str(response['gameId']) # 1237890
            ActiveGame.match_id = ActiveGame.region.upper() + '_' + game_id # EUW_12378912
            champions_ids = [response['participants'][p]['championId'] for p in 
                                             range(10)]
            
            champions_names = [ALL_CHAMPIONS_IDs.get(champions_ids[i]) for i in range(10)]

            ActiveGame.encryptionKey = response['observers']['encryptionKey']
            ActiveGame.blue_team = champions_names[0:5]
            ActiveGame.red_team = champions_names[5:]
            ActiveGame.is_game_founded = True
            ActiveGame.nick_region = summoner_name[0]

            common_check = cls.count_of_common(
                sequence_1=ActiveGame.blue_team,
                sequence_2=Validator.finded_game_characerts
            )

            if common_check != 5:
                logger.info(f'Active game characters: {ActiveGame.blue_team}')
                logger.info(f'Finded game characters: {Validator.finded_game_characerts}')
                return False
            
        return True
    
    @classmethod
    def spectate_active_game(cls):
        import os
        import subprocess
        list_task = os.popen('tasklist /FI "IMAGENAME eq League of Legends*"').readlines()
        
        if len(list_task) != 1:
            logger.info('Game already running')
            return
        
        logger.info('Launching spectator...')

        enc_key = ActiveGame.encryptionKey
        spectator = SPECTATOR_MODE.format(reg=ActiveGame.region)
        args = spectator, enc_key, str(ActiveGame.match_id.split('_')[1]), ActiveGame.region.upper()

        MCFStorage.write_data(route=("0", ), value=str(args))

        subprocess.call([SPECTATOR_FILE_PATH, *args])

    @classmethod
    def get_activegame_parametres(cls, nicknames):

        for nick in nicknames:
            try:
                cls.search_game(nick_region=nick)

                if Validator.ended_blue_characters is not None:
                    
                    common_elements = cls.count_of_common(
                        sequence_1=Validator.ended_blue_characters,
                        sequence_2=Validator.finded_game_characerts
                    )
                    
                    if common_elements == 5:
                        logger.info('Game ended! Restarting bot in 120s')
                        Validator.ended_blue_characters = None
                        Validator.finded_game_characerts = None
                        TGApi.winner_is(
                            team=Validator.ended_winner, 
                            kills=Validator.ended_kills,
                            timestamp=Validator.ended_time
                        )
                        Validator.quick_end = True


                if ActiveGame.is_game_founded:
                    # TGApi.send_simple_message('✅ Игра найдена: {nick}'.format(nick=nick))
                    Trace.create_new_trace(gameid=ActiveGame.match_id)
                    # mcf_autogui.close_league_stream()
                    return True
                    
            except Exception as ex:
                logger.error('{ex}'.format(ex=ex), exc_info=True)
    
    @classmethod
    def awaiting_game_end(cls, chrome: Chrome = None):
        # from mcf_data import Switches
        Switches.request = True
        while Switches.request:
            
            # while True:
            try:
                finished_game = RiotAPI.get_match_by_gameid(area=ActiveGame.area, 
                                                    gameid=ActiveGame.match_id, 
                                                    status=True)
                # break
            except Exception:
                logger.warning('Connection lose, reconnection..')
                time.sleep(1.5)
            
            if finished_game and finished_game.status_code == 200:

                response = finished_game.json()
                kills = sum(response['info']['participants'][k]['kills'] for k in range(10))
                time_stamp = list(divmod(response['info']['gameDuration'], 60))
                
                if time_stamp[1] < 10: 
                    time_stamp[1] = f"0{time_stamp[1]}"
                
            
                if chrome is not None:
                    is_opened = chrome.check_if_opened()
                else:
                    is_opened = False

                # if is_opened:
                #     Switches.coeff_opened = True

                if response['info']['teams'][0]['win']:
                    winner = 'blue'
                else:
                    winner = 'red'
                
                timestamp = f"[{time_stamp[0]}:{time_stamp[1]}]"
                TGApi.winner_is(team=winner, kills=kills, timestamp=timestamp, opened=is_opened)
                Trace.complete_trace(team=winner, kills=kills, timestamp=timestamp)
                MCFStorage.predicts_monitor(kills=kills)
                ActiveGame.is_game_founded = False
                Switches.request = False

                # if Validator.predict_value_flet is not None:
                #     ...

                finished_game.close()
                break
            
            time.sleep(1.25)