from mcf.static import RIOT_API_KEY
import logging
import requests

logger = logging.getLogger(__name__)

def is_riot_apikey_valid():
    
    res = requests.get(f"https://euw1.api.riotgames.com/lol/spectator/v5/featured-games?api_key={RIOT_API_KEY}")

    if res.status_code == 403:
        logger.error("Riot API key invalid")
        return False
    
    logger.info('Riot API key is correct!')
    return True
