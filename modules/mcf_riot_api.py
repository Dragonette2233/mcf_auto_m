import requests
import logging
from static_data import (
    MCFException,
    Headers,
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
                pass
                # raise MCFException('No connection | Timeout')
            except MCFException as mcf_ex:
                logging.error(mcf_ex, exc_info=True)
            except Exception as exc:
                logging.warning(exc, exc_info=True)
            
        return wrapper

    @connection_handler
    @staticmethod
    def get_summoner_puuid(area: str, name: str, puuid=False) -> dict:
        nickName, tagLine = name.split('#')
        result = requests.get(RiotAPI.__link_summoner_by_riotId.format(area=area, nickName=nickName, tagLine=tagLine), 
                              **Headers.riot)
        # print('im here', result.text)
        status = result.status_code
        if status in (403, 404):
            return status
        
        return result.json()['puuid']
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
