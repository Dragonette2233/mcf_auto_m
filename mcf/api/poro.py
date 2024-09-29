from static import (
    ALL_CHAMPIONS_IDs,
    REGIONS_TUPLE,
    URL,
    HEADERS
)
import asyncio
import logging
import requests
from bs4 import BeautifulSoup as bs
from aiohttp import ClientSession, ClientTimeout
from aiohttp.client_exceptions import (
    ClientProxyConnectionError,
    ClientConnectionError,
    ContentTypeError
    )

logger = logging.getLogger(__name__)


class PoroAPI:

    @classmethod
    def convert_income_character(cls, inc_character: str):
        
        converted_champion = None
        
        for champion in ALL_CHAMPIONS_IDs.values():
            if champion.capitalize().startswith(inc_character.capitalize()):
                converted_champion = champion.lower()
                break
        else:
            logger.warning("Champion unrecognized | %s", inc_character)
            # input("MCF Bot frozen !")
            
        match converted_champion:
            case 'wukong':
                converted_champion = 'monkeyking'
            case 'violet':
                converted_champion = 'vi'
            case _:
                pass
            
        return converted_champion
    
    @classmethod
    def get_games_from_parse(cls, parse_result: str) -> list:
        
        # parse_result -- result.text
        
        soup: bs = bs(parse_result, "html.parser").find_all('div', class_='cardTeam')
        
        games = {
            'teams': [team.find_all('img') for i, team in enumerate(soup) if i % 2 == 0],
            'champions': [],
            'regions': [team.find('a', class_='liveGameLink').get('href') for i, team in enumerate(soup) if i % 2 == 0],
        }
        
        nicknames_blue = [[ch.text.strip() for ch in team.find_all('div', class_='name')] for i, team in enumerate(soup) if i % 2 == 0]
        nicknames_red = [[ch.text.strip() for ch in team.find_all('div', class_='name')] for i, team in enumerate(soup) if i % 2 != 0]
        
        if len(soup) != 0:
            nicknames = [blue + red for blue, red in zip(nicknames_blue, nicknames_red)]
        else:
            nicknames = []

        for game in games['teams']:
            
            for i, champ in enumerate(game):
                if len(champ.get('class')) == 0:
                    del game[i]

            ids = []

            for info_stroke in game:
                champ_id_wieght = info_stroke.get('class')
                
                if len(champ_id_wieght) > 0:
                    ids.append(int(champ_id_wieght[0].split('-')[1]))
                    
            converted_ids = [ALL_CHAMPIONS_IDs.get(i) for i in ids]
            games['champions'].append(converted_ids)

        featured_games = []
        

        for c, n, r in zip(games['champions'], nicknames, games['regions']): # games['elorank']):
            
            champs = ' | '.join(c)
            names_region = '_|_'.join([f"{name}:{r.split('/')[2].upper()}" for name in n])
            whole_string = f"{champs}-|-{names_region}"
            featured_games.append(whole_string)
        
        return featured_games
    
    @classmethod
    def direct_poro_parsing(cls, red_champion) -> dict:

        """
            returning parsed games from ARAM page on porofessor.gg

        """
        
        mock_dict = {}

        converted_champion = cls.convert_income_character(red_champion)

        url = f'https://porofessor.gg/current-games/{converted_champion}/queue-450'
               
        try:
            result = requests.get(url, headers=HEADERS, timeout=3)
            result.raise_for_status()  # Проверяет, не было ли ошибки при запросе
        except requests.RequestException as e:
            logger.warning("Connection to Poro failed. Error: %s", str(e))
            mock_dict.setdefault("direct", [None, ])
            return mock_dict
        
        parse_result = result.text
        mock_dict['direct'] = cls.get_games_from_parse(parse_result)
        
        return mock_dict
          
    @classmethod
    def async_poro_parsing(cls, champion_name, advance_elo: str | bool = False):

        """
            returning parsed games from ARAM page for all regions on porofessor.gg
        
        """

        featured_games = {}

        async def parsing(champion, region):
            nonlocal missing_regions, featured_games
            # print('inhere')
            if advance_elo:
                url = URL.PORO_ADVANCE.format(region=region, champion=champion, elo=advance_elo.lower())
            else:
                url = URL.PORO_BY_REGIONS.format(region=region, champion=champion)
            
            async with ClientSession() as session:
                
                
                timeout = ClientTimeout(total=3)
                async with session.get(url=url, timeout=timeout, headers=HEADERS) as response:
                    
                    result = await response.text(encoding='utf8')
                    featured_games[region] = cls.get_games_from_parse(parse_result=result)
                
                    
        async def main_aram(champion_name):

            nonlocal missing_regions

            converted_champion = cls.convert_income_character(champion_name)
                
            tasks = []
            for region in REGIONS_TUPLE:
                tasks.append(asyncio.create_task(parsing(champion=converted_champion, region=region[0])))

            for task in tasks:
                try: 
                    await asyncio.gather(task)
                except (asyncio.exceptions.TimeoutError, ContentTypeError):
                    missing_regions += 1
                except (ClientConnectionError, ClientProxyConnectionError):
                    missing_regions = 20
                    
        missing_regions = 0
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main_aram(champion_name))
        return featured_games
