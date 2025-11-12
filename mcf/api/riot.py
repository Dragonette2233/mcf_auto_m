import requests
import logging
from typing import Callable, Any
from shared.config import Config
from mcf.api.common import get_session, retry_on_network
# from aiohttp import ClientSession
# from aiohttp.client_exceptions import (
#     ClientProxyConnectionError,
#     ClientConnectionError,
#     ContentTypeError
#     )
from static import (
    URL,
    # ALL_CHAMPIONS_IDs,
    # REGIONS_TUPLE
)

logger = logging.getLogger(__name__)

SESSION = get_session()

class RiotAPI:
    
    @staticmethod
    def _req_kwargs() -> dict:
        return {
            'headers': {"X-Riot-Token": Config.riot_api_key()},
            'timeout': 3,
            'proxies': Config.proxies(),
        }
    
    @staticmethod
    def connection_handler(func: Callable[..., Any]):
        # Backward compatible wrapper around common retry decorator
        return retry_on_network()(func)

    @connection_handler
    @staticmethod
    def get_summoner_puuid(area: str, name: str, puuid=False) -> dict | int:

        if area == 'sea':
            area = 'asia'
        
        nickName, tagLine = name.split('#')
        result = SESSION.get(
            URL.SUMMONER_BY_RIOTID.format(area=area, nickName=nickName, tagLine=tagLine),
            **RiotAPI._req_kwargs()
        )
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
        result = SESSION.get(
            URL.MATCHES_BY_PUUID.format(area=area, puuid=puuid),
            **RiotAPI._req_kwargs()
        )

        return result.json()
    
    @connection_handler
    @staticmethod
    def get_match_by_gameid(area: str, gameid: int, status=False):
        result = SESSION.get(
            URL.MATCH_BY_GAMEID.format(area=area, gameid=gameid),
            **RiotAPI._req_kwargs()
        )
        
        if status:
            return result
        return result.json()
    
    @connection_handler
    @staticmethod
    def get_active_by_summonerid(region: str, summid: int, status=False):
        result = SESSION.get(
            URL.ACTIVEGAME_BY_SUMMID.format(region=region, summid=summid),
            **RiotAPI._req_kwargs()
        )
        if status:
            return result
        return result.json()
    
    # @staticmethod
    # def async_riot_parse():


    #     """
    #         This function parsing games from Riot API Featured Games into
    #         GameData.json and returning count of missing regions
        
    #     """

    #     featured_games = {}

    #     async def parsing(region):
    #         nonlocal missing_regions, featured_games
            
    #         async with ClientSession() as session:
    #             async with session.get(URL.FEATURED_GAMES.format(region=region), 
    #                                 **RiotAPI.AIO_HTTP_HEADERS) as response:
                    
    #                 data = await response.json()
                    
    #                 try:
    #                     gameList = data['gameList']
    #                     if len(gameList) < 1:
    #                         missing_regions += 1
    #                         return
    #                 except KeyError as key_err:
    #                     logger.warning(f"{key_err}")
    #                     missing_regions += 1
    #                     return

    #                 routelist = []
    #                 for s in range(0, len(gameList)):
                        
    #                     # Создаем список из id персонажей для дальнейшей конвертации в имени
    #                     id_names = [int(gameList[s]['participants'][k]['championId']) for k in range(5)]

    #                     # Создаем список конвертированных id в имена персонажей
    #                     champ_list = [ALL_CHAMPIONS_IDs.get(id_name) for id_name in id_names]
                        
    #                     champ_string = ' | '.join([str(item) for item in champ_list])
    #                     summoners = '_|_'.join([f"{i['riotId']}:{gameList[s]['platformId']}" for i in gameList[s]['participants']])
                                
    #                     routelist.append(f"{champ_string}-|-{summoners}")

    #                 featured_games[region] = routelist.copy()
         
    #     async def main_aram():

    #         nonlocal missing_regions

    #         tasks = []
    #         for region in REGIONS_TUPLE:
    #             tasks.append(asyncio.create_task(parsing(region[1])))

    #         for task in tasks:
    #             try: 
    #                 await asyncio.gather(task)
    #             except asyncio.exceptions.TimeoutError:
    #                 missing_regions += 1
    #             except (ClientConnectionError, 
    #                     ClientProxyConnectionError, 
    #                     ContentTypeError):
    #                 missing_regions = 20
                    
    #     missing_regions = 0
    #     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    #     asyncio.run(main_aram())
        
    #     return featured_games
