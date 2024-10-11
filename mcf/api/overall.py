import os
import time
import logging
import itertools

from mcf import utils
from mcf.dynamic import CF
from mcf.api.telegram import TGApi
from static import (
    ALL_CHAMPIONS_IDs,
    SPECTATOR_MODE,
    Snippet
)


from mcf.ssim_recognition import CharsRecognition as ChRec
from mcf.api.chrome import Chrome
from mcf.api.storage import uStorage
from mcf.api.riot import RiotAPI
from mcf.api.poro import PoroAPI
logger = logging.getLogger(__name__)

class MCFApi:
    
    PARSED = {
        "RIOT_API_CACHE": {},
        "RIOT_API": {},
        "PORO_REGIONS": {},
        "PORO_DIRECT": {},
        "PORO_BRONZE": {},
        "PORO_SILVER": {}
    }

    @classmethod
    def get_characters(cls) -> dict[str, list]:

        ChRec.cut_from_screenshot()
        logger.info('Comparing icons...')
        team_blue = ChRec.get_recognized_characters(team_color='blue')
        team_red = ChRec.get_recognized_characters(team_color='red')
            
            
        logger.info(team_blue)
        logger.info(team_red)
        
        # Рассчитываем статиску по винрейту и тоталрейту
        CF.SR.calculate(
                team_blue=team_blue,
                team_red=team_red
            )
        
        if len(set(team_blue)) != 5:
            return

        return {
            'blue': team_blue,
            'red': team_red
        }
            
    @classmethod
    def spectate_active_game(cls):
        # import os
        import subprocess
        
        cls.close_league_of_legends()
        time.sleep(0.5)
        # list_task = os.popen('tasklist /FI "IMAGENAME eq League of Legends*"').readlines()
        
        # if len(list_task) != 1:
        #     logger.info('Game already running')
        #     return
        
        logger.info('Launching spectator...')

        enc_key = CF.ACT.encryptionKey
        spectator = SPECTATOR_MODE.format(reg=CF.ACT.region)
        args = spectator, enc_key, str(CF.ACT.match_id.split('_')[1]), CF.ACT.region.upper()
        
        # MCFStorage.write_data(route=("0", ), value=str(args))

        subprocess.call([Snippet.SPECTATOR, *args])
    
    @classmethod   
    def close_league_of_legends(cls):

        list_task = os.popen('tasklist /FI "IMAGENAME eq League of Legends*"').readlines()
        if len(list_task) == 1:
            logger.info('Game not launched')
            return
        
        list_task[3] = list_task[3].replace(' ', '')
        process_pid = list_task[3].split('exe')[1].split('Console')[0]
        os.popen(f'taskkill /PID {process_pid} /F')
        logger.info('League of Legends closed')

    @classmethod
    def get_games_by_character(cls, character: str):

        all_matches = []

        for key in cls.PARSED.keys():
            all_matches += [item for sublist in cls.PARSED[key].values() for item in sublist]
        
        for match in cls.PARSED.keys():
            matches_len = sum([len(cls.PARSED[match][i]) for i in cls.PARSED[match].keys()])
            logger.info(f"{match} len: {matches_len}")

        finded_games = set()

        for match in all_matches:
            if match is not None:
                if character in match:
                    finded_games.add(match)

        return list(finded_games)
    
    @classmethod
    def parse_from_all_sources(cls, char_r):
        
        while True:
            try:
                logger.info('Parsing from RiotAPI and Poro...')
                
                cls.PARSED['PORO_REGIONS'] = PoroAPI.async_poro_parsing(champion_name=char_r) # Parse full PoroARAM by region
                cls.PARSED['PORO_BRONZE'] = PoroAPI.async_poro_parsing(champion_name=char_r, advance_elo='Bronze') # Parse for Bronze+
                cls.PARSED['PORO_SILVER'] = PoroAPI.async_poro_parsing(champion_name=char_r, advance_elo='Silver') # Parse for Silver+
                cls.PARSED['PORO_DIRECT'] = PoroAPI.direct_poro_parsing(red_champion=char_r) # Parse only main page PoroARAM
                cls.PARSED['RIOT_API'] = RiotAPI.async_riot_parse() # Parse featured games from Riot API

                logger.info('Games parsed succesfully.')
                break
            except Exception as ex:
                logger.warning(str(ex))
                time.sleep(4)
                continue
    
    @classmethod
    def count_of_common(cls, sequence_1: list[str], sequence_2: list[str]) -> int:

         set_1 = set([i.lower().capitalize() for i in sequence_1])
         set_2 = set([i.lower().capitalize() for i in sequence_2])
        
         # Нахождение пересечения множеств
         return len(set_1 & set_2)

    @classmethod
    def cache_before_stream(cls):
        cls.PARSED['RIOT_API_CACHE'] = RiotAPI.async_riot_parse() # Parse featured games from Riot API
        logger.info('Games cached successfull!')

    @classmethod
    def get_activegame_by_teams(cls, teams: dict, from_cache=False) -> list:

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
    def cache_ended_game(cls):
        
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
        timestamp = divmod(lastgame['info']['gameDuration'], 60)

        end_game_data = (
            champions_names[0:5].copy(), # blue team
            champions_names[5:].copy(), # red team
            sum(lastgame['info']['participants'][k]['kills'] for k in range(10)), # kills
            'blue' if teams_info[0]['win'] else 'red', # winner
            f"{timestamp[0]:02}:{timestamp[1]:02}" # time
        )
        
        CF.END.save(end_game_data)

    @classmethod
    def get_aram_statistic(cls, blue: list, red: list):
        from mcf import stats_by_roles

        return stats_by_roles.get_aram_statistic(
                blue_entry=blue,
                red_entry=red,
            )
    
    @classmethod
    def search_game(cls, nick_region: str):
       
        summoner_name = nick_region.split(':')
        
        CF.ACT.region, CF.ACT.area = utils.extract_code_and_area(summoner_name)
        
        logger.info('Searching...')
        logger.info(summoner_name[0].split('#')[0])

        summoner_data = RiotAPI.get_summoner_puuid(area=CF.ACT.area, 
                                                   name=summoner_name[0])

        if summoner_data == 404:
            logger.warning('Summoner not found')
            return
        elif summoner_data == 403:
            logger.error('API key wrong or exipred')
        
        CF.ACT.puuid = summoner_data
        response_activegame = RiotAPI.get_active_by_summonerid(region=CF.ACT.region,
                                                               summid=CF.ACT.puuid,
                                                               status=True)
            
        if response_activegame.status_code != 200:
            logger.info(response_activegame.status_code)
            logger.info('Loading last game')
            cls.cache_ended_game()
        else:
            
            '''Запрос активной игры'''

            response = response_activegame.json()
            if response['gameMode'] != 'ARAM':
                return False
            
            game_id = str(response['gameId']) # 1237890
            CF.ACT.match_id = CF.ACT.region.upper() + '_' + game_id # EUW_12378912
            champions_ids = [response['participants'][p]['championId'] for p in range(10)]
            champions_names = [ALL_CHAMPIONS_IDs.get(champions_ids[i]) for i in range(10)]

            activegame_data = (
                champions_names[0:5], # blue_chars
                champions_names[5:], # red_chars
                nick_region, # nick_region
                response['observers']['encryptionKey'], # encryptionKey
                True, # is_game_founded
                
            )
            
            CF.ACT.save(activegame_data)
            
            common_check = cls.count_of_common(
                sequence_1=CF.ACT.blue_chars,
                sequence_2=CF.ACT.finded_chars
            )

            if common_check != 5:
                logger.info(f'Active game characters: {CF.ACT.blue_chars}')
                logger.info(f'Finded game characters: {CF.ACT.finded_chars}')
                return False
            
        return True
    
    @classmethod
    def is_game_active(cls, nicknames: list) -> bool:

        for nick in nicknames:
            try:
                cls.search_game(nick_region=nick)

                if CF.END.is_ended():
                    
                    common_elements = cls.count_of_common(
                        sequence_1=CF.END.blue_chars,
                        sequence_2=CF.ACT.finded_chars
                    )
                    
                    if common_elements == 5:
                        CF.SW.quick_end.activate()
                        return False


                if CF.ACT.is_game_founded:
                    # Trace.create_new_trace(gameid=CF.ACT.match_id)
                    return True
                    
            except Exception as ex:
                logger.error('{ex}'.format(ex=ex), exc_info=True)
    
    @classmethod
    def awaiting_game_end(cls, chrome: None | Chrome = None):
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
                time_stamp = divmod(response['info']['gameDuration'], 60)
                
            
                if chrome is not None:
                    is_opened = chrome.is_total_coeff_opened(end_check=True)
                    if is_opened:
                        CF.SW.coeff_opened.activate()
                else:
                    is_opened = False

                winner = 'blue' if response['info']['teams'][0]['win'] else 'red'
                
                timestamp = f"[{time_stamp[0]:02}:{time_stamp[1]:02}]"
                TGApi.winner_is(winner=winner, kills=kills, timestamp=timestamp, opened=is_opened)
                uStorage.upd_current_game_status("Окончена")
                # Trace.complete_trace(team=winner, kills=kills, timestamp=timestamp)
                pr_result = uStorage.save_predict_result(kills=kills, pr_cache=CF.VAL.pr_cache)
                if pr_result:
                    TGApi.update_predict_result(state=pr_result)
                CF.SW.request.deactivate()

                finished_game.close()
                break
            
            time.sleep(1.25)