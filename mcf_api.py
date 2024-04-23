import logging
import time
from dynamic_data import CF
from tg_api import TGApi
from static_data import (
    REGIONS_TUPLE,
    ALL_CHAMPIONS_IDs,
    SPECTATOR_MODE,
    PATH,
)
import os
import itertools
from chrome_driver import Chrome
from modules.ssim_recognition import RecognizedCharacters as SsimReco
from modules.mcf_storage import MCFStorage
from modules.mcf_tracing import Trace
from modules.mcf_riot_api import RiotAPI
from modules import mcf_utils
logger = logging.getLogger(__name__)

class MCFApi:
    
    CACHE_RIOT_API = {}
    CACHED_RIOT_REGIONS = {}

    PARSED_RIOT_API = {}
    PARSED_PORO_REGIONS = {}
    PARSED_PORO_DIRECT = []
    PARSED_PORO_BRONZE = {}
    PARSED_PORO_SILVER = {}

    @classmethod
    def get_characters(cls):

        while True:
            if not CF.ACT.nick_region:
                logger.info('Comparing icons...')
                team_blue = SsimReco(team_color='blue')
                team_red = SsimReco(team_color='red')
                team_blue.run()
                team_red.run()

            logger.info(team_blue.characters)
            logger.info(team_red.characters)
            
            if len(set(team_blue.characters)) != 5:
                return

            CF.SR.calculate(
                team_blue=team_blue.characters,
                team_red=team_red.characters
            )

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

        all_matches += [item for sublist in cls.PARSED_RIOT_API.values() for item in sublist]
        logger.info(f'RiotAPI len matches: {len(all_matches)}')
        all_matches += [item for sublist in cls.PARSED_PORO_REGIONS.values() for item in sublist]
        all_matches += [item for sublist in cls.PARSED_PORO_BRONZE.values() for item in sublist]
        all_matches += [item for sublist in cls.PARSED_PORO_SILVER.values() for item in sublist]
        all_matches += [item for sublist in cls.CACHE_RIOT_API.values() for item in sublist]
        all_matches += cls.PARSED_PORO_DIRECT
        logger.info(f'Total len matches: {len(all_matches)}')
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
                cls.PARSED_PORO_REGIONS = mcf_utils.async_poro_parsing(champion_name=char_r) # Parse full PoroARAM by region
                cls.PARSED_PORO_BRONZE = mcf_utils.async_poro_parsing(champion_name=char_r, advance_elo='Bronze') # Parse for Bronze+
                cls.PARSED_PORO_SILVER = mcf_utils.async_poro_parsing(champion_name=char_r, advance_elo='Silver') # Parse for Silver+
                cls.PARSED_PORO_DIRECT = mcf_utils.direct_poro_parsing(red_champion=char_r) # Parse only main page PoroARAM
                cls.PARSED_RIOT_API = mcf_utils.async_riot_parsing() # Parse featured games from Riot API
                # print(cls.PARSED_PORO_BRONZE)
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
    def cache_before_stream(cls):
        cls.CACHE_RIOT_API = mcf_utils.async_riot_parsing() # Parse featured games from Riot API
        logger.info('Games cached successfull!')

    @classmethod
    def finded_game(cls, teams: dict, from_cache=False):

        team_cycle = itertools.cycle(zip(teams['blue'], teams['red']))

        CF.ACT.finded_chars = teams['blue'].copy()

        for char_b, char_r in team_cycle:
            
            cls.parse_from_all_sources(char_r=char_r)
            games_by_character: list[str] = cls.get_games_by_character(character=char_b)

            for charlist in games_by_character:
                nicknames = charlist.split('-|-')[1].split('_|_')
                characters = charlist.split('-|-')[0].split(' | ')
                common_elements = cls.count_of_common(sequence_1=characters, sequence_2=CF.ACT.finded_chars)

                if common_elements >= 4:
                    return nicknames
            else:
                logger.warning('No games for {char_r} -- {char_b}. CD 3s'.format(char_r=char_r, char_b=char_b))
                CF.VAL.findgame += 1

                if CF.VAL.findgame == 15:
                    CF.VAL.findgame = 0
                    return None
                time.sleep(2)
    
    @classmethod
    def show_lastgame_info(cls):
        
        games_list = RiotAPI.get_matches_by_puuid(area=CF.ACT.area, 
                                                  puuid=CF.ACT.puuid)
        
        if len(games_list) == 0:

            logger.warning('No games for this summoner')
            return

        lastgame = RiotAPI.get_match_by_gameid(area=CF.ACT.area, gameid=games_list[0])
        
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
        CF.END.blue_chars = champions_names[0:5].copy()
        CF.END.red_chars = champions_names[5:].copy()
        CF.END.kills = sum(lastgame['info']['participants'][k]['kills'] for k in range(10))
        CF.END.winner = 'blue' if teams_info[0]['win'] else 'red'
        CF.END.time = f"{timestamp[0]}:{timestamp[1]}"

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
                CF.ACT.region = code
                CF.ACT.area = area
                break

    
        logger.info('Searching...')

        logger.info(summoner_name[0].split('#')[0])

        summoner_data = RiotAPI.get_summoner_puuid(area=CF.ACT.area, 
                                                   name=summoner_name[0])

        # print(summoner_data)
        # input('AWAITING...')
        if summoner_data == 404:
            logger.warning('Summoner not found')
            return
        elif summoner_data == 403:
            logger.error('API key wrong or exipred')
        
        # logger.info(summoner_data)

        CF.ACT.puuid = summoner_data
        response_activegame = RiotAPI.get_active_by_summonerid(region=CF.ACT.region,
                                                               summid=CF.ACT.puuid,
                                                               status=True)
            
        if response_activegame.status_code != 200:
            logger.info(response_activegame.status_code)
            logger.info('Loading last game')
            cls.show_lastgame_info()
        else:
            
            '''Запрос активной игры'''

            response = response_activegame.json()
            if response['gameMode'] != 'ARAM':
                return False
            
            game_id = str(response['gameId']) # 1237890
            CF.ACT.match_id = CF.ACT.region.upper() + '_' + game_id # EUW_12378912
            champions_ids = [response['participants'][p]['championId'] for p in 
                                             range(10)]
            
            champions_names = [ALL_CHAMPIONS_IDs.get(champions_ids[i]) for i in range(10)]

            CF.ACT.encryptionKey = response['observers']['encryptionKey']
            CF.ACT.blue_team = champions_names[0:5]
            CF.ACT.red_team = champions_names[5:]
            CF.ACT.is_game_founded = True
            CF.ACT.nick_region = nick_region

            common_check = cls.count_of_common(
                sequence_1=CF.ACT.blue_team,
                sequence_2=CF.ACT.finded_chars
            )

            if common_check != 5:
                logger.info(f'Active game characters: {CF.ACT.blue_team}')
                logger.info(f'Finded game characters: {CF.ACT.finded_chars}')
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

        enc_key = CF.ACT.encryptionKey
        spectator = SPECTATOR_MODE.format(reg=CF.ACT.region)
        args = spectator, enc_key, str(CF.ACT.match_id.split('_')[1]), CF.ACT.region.upper()

        MCFStorage.write_data(route=("0", ), value=str(args))

        subprocess.call([PATH.SPECTATOR_FILE, *args])

    @classmethod
    def get_activegame_parametres(cls, nicknames: list) -> bool:

        for nick in nicknames:
            try:
                cls.search_game(nick_region=nick)

                if CF.END.blue_chars is not None:
                    
                    common_elements = cls.count_of_common(
                        sequence_1=CF.END.blue_chars,
                        sequence_2=CF.ACT.finded_chars
                    )
                    
                    if common_elements == 5:
                        CF.SW.quick_end.activate()
                        return False


                if CF.ACT.is_game_founded:
                    Trace.create_new_trace(gameid=CF.ACT.match_id)
                    return True
                    
            except Exception as ex:
                logger.error('{ex}'.format(ex=ex), exc_info=True)
    
    @classmethod
    def awaiting_game_end(cls, chrome: Chrome = None):
        CF.SW.request.activate()

        while CF.SW.request.is_active():
            

            try:
                finished_game = RiotAPI.get_match_by_gameid(area=CF.ACT.area, 
                                                    gameid=CF.ACT.match_id, 
                                                    status=True)
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
                    is_opened = chrome.is_total_coeff_opened(end_check=True)
                    if is_opened:
                        CF.SW.coeff_opened.activate()
                else:
                    is_opened = False

                if response['info']['teams'][0]['win']:
                    winner = 'blue'
                else:
                    winner = 'red'
                
                timestamp = f"[{time_stamp[0]}:{time_stamp[1]}]"
                TGApi.winner_is(team=winner, kills=kills, timestamp=timestamp, opened=is_opened)
                Trace.complete_trace(team=winner, kills=kills, timestamp=timestamp)
                MCFStorage.predicts_monitor(kills=kills, key='main')
                MCFStorage.predicts_monitor(kills=kills, key='stats')
                MCFStorage.predicts_monitor(kills=kills, key='main', daily=True)
                MCFStorage.predicts_monitor(kills=kills, key='stats', daily=True)
                # Validator.predict_value_flet['main'] = None
                # Validator.predict_value_flet['stats'] = None
                # chrome.ACTIVE_TOTAL_VALUE = 0
                # CF.ACT.is_game_founded = False
                CF.SW.request.deactivate()

                finished_game.close()
                break
            
            time.sleep(1.25)