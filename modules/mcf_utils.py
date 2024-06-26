from static_data import (
    PATH,
    ALL_CHAMPIONS_IDs,
    REGIONS_TUPLE,
    FEATURED_GAMES_URL,
    URL_PORO_BY_REGIONS,
    URL_PORO_ADVANCE,
    MCFException,
    Headers
)
import asyncio
import logging
import requests
from modules.mcf_storage import MCFStorage
from bs4 import BeautifulSoup as bs
from aiohttp import ClientSession, ClientTimeout
from aiohttp.client_exceptions import (
    ClientProxyConnectionError,
    ClientConnectionError,
    ContentTypeError
    )
import os

logger = logging.getLogger(__name__)

def delete_scoreboard():

    MCFStorage.save_score(stop_tracking=True)
    
def close_league_of_legends():

    list_task = os.popen('tasklist /FI "IMAGENAME eq League of Legends*"').readlines()
    if len(list_task) == 1:
        # self.info_view.exception('Game not launched')
        return
    
    list_task[3] = list_task[3].replace(' ', '')
    process_pid = list_task[3].split('exe')[1].split('Console')[0]
    os.popen(f'taskkill /PID {process_pid} /F')

def advance_poro_search():
    ...

def direct_poro_parsing(red_champion) -> list:

    """
        Avaliable gamemods: aram | ranked-flex | ranked-solo

    """

    if len(red_champion) < 2:
        raise MCFException('Short')

    converted_champion = None
    for champion in ALL_CHAMPIONS_IDs.values():
        if champion.capitalize().startswith(red_champion.capitalize()):
            converted_champion = champion.lower()
            break
    else:
        raise MCFException(f'Who is {red_champion}')
    
    match converted_champion:
        case 'wukong':
            converted_champion = 'monkeyking'
        case 'violet':
            converted_champion = 'vi'
        case _:
            pass

    try:
        url = f'https://porofessor.gg/current-games/{converted_champion}/queue-450'
    except:
        raise MCFException('This gamemod is unaccesible')
            
    result = requests.get(url, headers=Headers.default, timeout=3)
    soup: bs = bs(result.text, "html.parser").find_all('div', class_='cardTeam')

    if result.status_code != 200:
        raise MCFException(f'Error. Status: {result.status_code}')
    
    games = {
        'teams': [team.find_all('img') for i, team in enumerate(soup) if i % 2 == 0],
        'champions': [],
        # 'nicknames': [team.find('div', class_='name').text.strip() for i, team in enumerate(soup) if i % 2 == 0],
        'regions': [team.find('a', class_='liveGameLink').get('href') for i, team in enumerate(soup) if i % 2 == 0],
        # 'elorank': [team.find('div', class_='subname').text.strip() for i, team in enumerate(soup) if i % 2 == 0]
    }


    nicknames_blue = [[ch.text.strip() for ch in team.find_all('div', class_='name')] for i, team in enumerate(soup) if i % 2 == 0]
    nicknames_red = [[ch.text.strip() for ch in team.find_all('div', class_='name')] for i, team in enumerate(soup) if i % 2 != 0]

    if len(soup) != 0:
        nicknames = [blue + red for blue, red in zip(nicknames_blue, nicknames_red)]
        # for i in (range(soup) / 2):
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
    
    # MCFStorage.write_data(route=('MatchesPoroGlobal', ), value=featured_games)
    # print(featured_games)
    return featured_games

def async_poro_parsing(champion_name, advance_elo: str | bool = False):

    """
        This function parsing games from Porofessor.gg into
        GameData.json and returning count of missing regions
    
    """

    featured_games = {}

    async def parsing(champion, region):
        nonlocal missing_regions, featured_games
        # print('inhere')
        if advance_elo:
            url = URL_PORO_ADVANCE.format(region=region, champion=champion, elo=advance_elo.lower())
        else:
            url = URL_PORO_BY_REGIONS.format(region=region, champion=champion)
        headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
            }
        
        async with ClientSession() as session:
            
            
            timeout = ClientTimeout(total=3)
            async with session.get(url=url, timeout=timeout, headers=headers) as response:
                
                result = await response.text(encoding='utf8')
                soup: bs = bs(result, "html.parser").find_all('div', class_='cardTeam')

            
                games = {
                    'teams': [team.find_all('img') for i, team in enumerate(soup) if i % 2 == 0],
                    'champions': [],
                    # 'nicknames': [team.find('div', class_='name').text.strip() for i, team in enumerate(soup) if i % 2 == 0],
                    'regions': [team.find('a', class_='liveGameLink').get('href') for i, team in enumerate(soup) if i % 2 == 0],
                    # 'elorank': [team.find('div', class_='subname').text.strip() for i, team in enumerate(soup) if i % 2 == 0]
                }


                ### TESTS

                # single_game = [game.find_all('div', class_='name') for game in soup]
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

                finded_games = []
            

                for c, n, r in zip(games['champions'], nicknames, games['regions']): # games['elorank']):
                    
                    champs = ' | '.join(c)
                    names_region = '_|_'.join([f"{name}:{r.split('/')[2].upper()}" for name in n])
                    whole_string = f"{champs}-|-{names_region}"
                    finded_games.append(whole_string)
                
                featured_games[region] = finded_games.copy()
                # print(featured_games[region])
                # if advance_elo:
                #     MCFStorage.write_data(route=(f'MatchesPoro{advance_elo}', region,), value=featured_games)
                # else:
                #     MCFStorage.write_data(route=('MatchesPoroRegions', region,), value=featured_games)
                    
    async def main_aram(champion_name):

        nonlocal missing_regions

        if len(champion_name) < 2:
            raise MCFException('Short')

        converted_champion = None
        for champion in ALL_CHAMPIONS_IDs.values():
            if champion.capitalize().startswith(champion_name.capitalize()):
                converted_champion = champion.lower()
                break
        else:
            raise MCFException(f'Who is {champion_name}')
        
        match converted_champion:
            case 'wukong':
                converted_champion = 'monkeyking'
            case 'violet':
                converted_champion = 'vi'
            case _:
                pass
            

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
    # print(featured_games)
    return featured_games


def async_riot_parsing():

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
                
                # logger.info(response.status)
                try:
                    gameList = data['gameList']
                    # print(len(gameList))
                    if len(gameList) < 1:
                        missing_regions += 1
                        return
                except KeyError as key_err:
                    logger.warning(f"{key_err}")
                    missing_regions += 1
                    return

                # from pprint import pprint
                routelist = []
                for s in range(0, len(gameList)):
                    
                    # Создаем список из id персонажей для дальнейшей конвертации в имени
                    id_names = [int(gameList[s]['participants'][k]['championId']) for k in range(5)]

                    # Создаем список конвертированных id в имена персонажей
                    champ_list = [ALL_CHAMPIONS_IDs.get(id_name) for id_name in id_names]
                    
                    champ_string = ' | '.join([str(item) for item in champ_list])
                    # pprint(gameList[s])
                    # exit(0)
                    summoners = '_|_'.join([f"{i['riotId']}:{gameList[s]['platformId']}" for i in gameList[s]['participants']])
                            
                    routelist.append(f"{champ_string}-|-{summoners}")
                # print(routelist)
                # print(routelist)
                featured_games[region] = routelist.copy()
                # print(featured_games[region])
                # MCFStorage.write_data(
                #     route=('MatchesAPI', region.upper(), ), 
                #     value=routelist
                #     )
                    
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
    
    # print(featured_games)
    # print(missing_regions)
    return featured_games
