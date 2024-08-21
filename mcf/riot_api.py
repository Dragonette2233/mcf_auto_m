import requests
import logging
import asyncio
from aiohttp import ClientSession, ClientTimeout
from aiohttp.client_exceptions import (
    ClientProxyConnectionError,
    ClientConnectionError,
    ContentTypeError
    )
from mcf.static_data import (
    MCFException,
    Headers,
    ALL_CHAMPIONS_IDs,
    FEATURED_GAMES_URL,
    REGIONS_TUPLE
)

logger = logging.getLogger(__name__)

class RiotAPI:
    # __headers_timeout = riot_headers
    __link_summoner_by_name = "https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{name}"
    __link_summoner_by_riotId = "https://{area}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{nickName}/{tagLine}"
    __link_matches_by_puuid = "https://{area}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=2"
    __link_match_by_gameid = "https://{area}.api.riotgames.com/lol/match/v5/matches/{gameid}"
    __link_active_by_summid = "https://{region}.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{summid}"
    
    @staticmethod
    def connection_handler(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
            except (requests.exceptions.ConnectTimeout, 
                    requests.exceptions.ConnectionError,
                    requests.exceptions.ReadTimeout):
                logger.warning("No connection | Timeout")
            except Exception as exc:
                logger.warning(exc, exc_info=True)
            
        return wrapper

    @connection_handler
    @staticmethod
    def get_summoner_puuid(area: str, name: str, puuid=False) -> dict:

        if area == 'sea':
            area = 'asia'

        nickName, tagLine = name.split('#')
        result = requests.get(RiotAPI.__link_summoner_by_riotId.format(area=area, nickName=nickName, tagLine=tagLine), 
                              **Headers.riot)
        # print('im here', result.text)
        
        status = result.status_code
        body = result.json()
        
        if status != 200:
            logger.warning(body)
            return status
        else:
            return body['puuid']
        
    @connection_handler
    @staticmethod
    def get_matches_by_puuid(area: str, puuid: int):
        result = requests.get(RiotAPI.__link_matches_by_puuid.format(area=area, puuid=puuid), 
                              **Headers.riot)

        return result.json()
    
    @connection_handler
    @staticmethod
    def get_match_by_gameid(area: str, gameid: int, status=False):
        result = requests.get(RiotAPI.__link_match_by_gameid.format(area=area, gameid=gameid), 
                              **Headers.riot)
        
        if status:
            return result
        return result.json()
    
    @connection_handler
    @staticmethod
    def get_active_by_summonerid(region: str, summid: int, status=False):
        result = requests.get(RiotAPI.__link_active_by_summid.format(region=region, summid=summid), 
                              **Headers.riot)
        if status:
            return result
        return result.json()
    
    @staticmethod
    def async_riot_parse():


        """
            This function parsing games from Riot API Featured Games into
            GameData.json and returning count of missing regions
        
        """

        featured_games = {}

        async def parsing(region):
            nonlocal missing_regions, featured_games
            
            async with ClientSession() as session:
                async with session.get(url=FEATURED_GAMES_URL.format(region=region), 
                                    **Headers.riot) as response:
                    
                    data = await response.json()
                    
                    try:
                        gameList = data['gameList']
                        if len(gameList) < 1:
                            missing_regions += 1
                            return
                    except KeyError as key_err:
                        logger.warning(f"{key_err}")
                        missing_regions += 1
                        return

                    routelist = []
                    for s in range(0, len(gameList)):
                        
                        # Создаем список из id персонажей для дальнейшей конвертации в имени
                        id_names = [int(gameList[s]['participants'][k]['championId']) for k in range(5)]

                        # Создаем список конвертированных id в имена персонажей
                        champ_list = [ALL_CHAMPIONS_IDs.get(id_name) for id_name in id_names]
                        
                        champ_string = ' | '.join([str(item) for item in champ_list])
                        summoners = '_|_'.join([f"{i['riotId']}:{gameList[s]['platformId']}" for i in gameList[s]['participants']])
                                
                        routelist.append(f"{champ_string}-|-{summoners}")

                    featured_games[region] = routelist.copy()
         
        async def main_aram():

            nonlocal missing_regions

            tasks = []
            for region in REGIONS_TUPLE:
                tasks.append(asyncio.create_task(parsing(region[1])))

            for task in tasks:
                try: 
                    await asyncio.gather(task)
                except asyncio.exceptions.TimeoutError:
                    missing_regions += 1
                except (ClientConnectionError, ClientProxyConnectionError):
                    missing_regions = 20
                    
        missing_regions = 0
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main_aram())
        
        return featured_games
