from static import REGIONS_TUPLE
from shared.config import Config
import logging
import requests

logger = logging.getLogger(__name__)
PROXIES = Config.proxies()


def is_riot_apikey_valid():
    try:
        res = requests.get(
            f"https://euw1.api.riotgames.com/lol/spectator/v5/featured-games?api_key={Config.riot_api_key()}",
            verify=False,
            proxies=PROXIES,
        )

        if res.status_code == 403:
            logger.error("Riot API key invalid")
            return False
        
        logger.info('Riot API key is correct!')
        return True
    except OSError:
        logger.warning("Connection failed. Skipping")
    except Exception as e:
        logger.warning(e)

def extract_code_and_area(summoner_name: str) -> tuple:
    
    """
        Extracting code and area from nickname and region string.
        Example - SomeNick223:BR -> ('br1', 'americas')
    """
        
    for short, code, area in REGIONS_TUPLE:
        if summoner_name[1].lower() == short or summoner_name[1].lower() == code:
            return (code, area)
