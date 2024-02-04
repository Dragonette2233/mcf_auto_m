from mcf_data import (
    MCF_BOT_PATH,
    ALL_CHAMPIONS_IDs,
    REGIONS_TUPLE,
    FEATURED_GAMES_URL,
    URL_PORO_BY_REGIONS,
    URL_PORO_ADVANCE,
    MCFException,
    poro_headers,
    riot_headers,
)
import asyncio
import logging
import requests
from modules.mcf_storage import MCFStorage
from bs4 import BeautifulSoup as bs
from aiohttp import ClientSession, ClientTimeout
from aiohttp.client_exceptions import (
    ClientProxyConnectionError,
    ClientConnectionError
    )
import os


def delete_scoreboard(self):

    MCFStorage.save_score(stop_tracking=True)
    try:
        # os.remove(os.path.join('images_lib', 'scorecrop.png'))
        os.remove(os.path.join(MCF_BOT_PATH, 'images_lib', 'buildcrop.png'))
    except FileNotFoundError:
        pass

def close_league_of_legends(self):

    list_task = os.popen('tasklist /FI "IMAGENAME eq League of Legends*"').readlines()
    if len(list_task) == 1:
        self.info_view.exception('Game not launched')
        return
    
    list_task[3] = list_task[3].replace(' ', '')
    process_pid = list_task[3].split('exe')[1].split('Console')[0]
    os.popen(f'taskkill /PID {process_pid} /F')
    # app_blueprint.delete_screenscore()
    self.info_view.success('League of Legends closed')

def advance_poro_search():
    ...

def direct_poro_parsing(red_champion):

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
            
    result = requests.get(url, headers=poro_headers, timeout=3)
    soup: bs = bs(result.text, "html.parser").find_all('div', class_='cardTeam')

    if result.status_code != 200:
        raise MCFException(f'Error. Status: {result.status_code}')
    
    games = {
        'teams': [team.find_all('img') for i, team in enumerate(soup) if i % 2 == 0],
        'champions': [],
        # 'nicknames': [team.find('div', class_='name').text.strip() for i, team in enumerate(soup) if i % 2 == 0],
        'regions': [team.find('a', class_='liveGameLink').get('href') for i, team in enumerate(soup) if i % 2 == 0],
        'elorank': [team.find('div', class_='subname').text.strip() for i, team in enumerate(soup) if i % 2 == 0]
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
    
    MCFStorage.write_data(route=('MatchesPoroGlobal', ), value=featured_games)

def async_poro_parsing(champion_name, bronze=False):

    """
        This function parsing games from Riot API Featured Games into
        GameData.json and returning count of missing regions
    
    """

    async def parsing(champion, region):
        nonlocal missing_regions
        # print('inhere')
        if bronze:
            url = URL_PORO_ADVANCE.format(region=region, champion=champion)
        else:
            url = URL_PORO_BY_REGIONS.format(region=region, champion=champion)
        headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                # 'Cookie': '_gcl_au=1.1.1729093274.1699391457; _ga=GA1.1.517303421.1699391458; usprivacy=1---; _li_dcdm_c=.porofessor.gg; _lc2_fpi=5ea9a59474f2--01henszjrqwzy6mvvkm05cjyzz; _lr_env_src_ats=false; _sharedid=f05ae455-e845-4cfa-90da-d546aad91390; _cc_id=71849bb6b721fec560236ae52774fef5; ccuid=3e2a2472-b2b0-442b-a620-fc48f299cf09; languageBanner_ru_count=6; _fbp=fb.1.1699979202409.147133882; gdpr-auditId=214a1b85e17a4d09bbb0ca5d56da790d; _cq_duid=1.1700347977.rxuShp5G4bNKhV8J; _cq_suid=1.1700347977.ssWsTBiYOmfClnhJ; gdpr-config-version=21; euconsent-v2=CP1b_EAP1b_EAADABBRUDQEsAP_AAEPgAAAAIBoF5C5cRCFD4CJgIJIUIAEXwFAAAAAgBgQBA4AASBCAMAwEkAAAEAAAIAAAAAAAIAIAAAAACAkAAAAAAIABAQAAAEAAAAAAIAAAAAAAAAAAAAgAAIAAEAAAAAAAACAAgAAAAAAAQAAAAAAAAQAAAAAAAAAAAAAAAAAAQAAAQAAAAIHyIF5C5cRCFD4CBAIJIUIAERQFAAAAAgAAQBAwAASBCAMAwAkAAAAAAAIAAAAAAAIAAAAAAAAAkAAAAAAIABAQAAAEAAAAAAIAAAAAAAAAAAAAgAAIAAAAAAAAAAACAAgAAAAAAAQAAAAAAAAQAAAAAAAAAAAAAAAAAAQAAAQAAA.YAAAAAAAA4AA; cconsent-v2=CP1b_EAP1b_EAADABBRUDQEgAPgAAAAAAAABixQFgAEgAMAA6AGEAUIAqoBpAGnANoA24BwAHCAOsAeIA9gCKAEWAI0AR0ApQnFxXniz8F7KMWIAAAAA.YAAAAAAAAAA; addtl_consent=1~7.1215.1516.2133.2642; gdpr-last-interaction=1700347980.572; shareinfobanner_closed=1; _pbjs_userid_consent_data=3524755945110770; cto_bundle=1GIz6F9jcTl1RHlRYXpaZno4YmpYbjYlMkJwYll6aWc5WEwyUWh6M0VOTW4lMkZPRDRwbTAyJTJCeXkxck9mSzNCdGVvUFpITU95YndCNlVnbHJRRmV5NGZ0WTZ5QzV1c0hENm5mY0JaVDFTUFlrNUhTNlJVJTJGMkxKaDJjVThPQ3JXUDVLNFR5d0lNT1Q0elc3S2gzcGJQSXZzeTZ3VkcwTnNWeEowcktzNUJmV1VaUkslMkZQeSUyRmslM0Q; cto_bidid=15Uzn18xVyUyQlpEbnpzSG9VNnlvTXQxTDF1N25oN2EybHNvVWtjNk1DN2FVcllnQk4lMkI5OVF5MURzcWZFWW4ydmkyOG8zNU00ZCUyQm1LSjNsMUNFUGZNeFJwcXlwQXdVbHltQXJ2dlFjNVRJZTk0NldmOCUzRA; panoramaId_expiry=1701993276645; panoramaId=1988784382794f8e5a5da242419d16d53938dafff572c28019d78400282f2152; lastSearch=Yamagasumi#1234; searchRegion=th; _ga_JMY38L43YZ=GS1.1.1701634033.102.0.1701634033.60.0.0; ccsid=466c3062-3eac-4259-b39c-af13e214eeb0; _lr_retry_request=true; cto_bundle=bf_kb19jcTl1RHlRYXpaZno4YmpYbjYlMkJwYlZwbW1rclFOeWZyeFR2QUd6WjlYQXdRMUxzQlIyR1VHR05nYUlqQW9xMm1NdU4lMkJvM2hIT2ZKaFp0SFBmcmg5MnJJZGxyeDdHJTJCYnAlMkZZbjhObUtEWmFxVUY3dTdteDhrNWdZUm53UnJBZFM0YVRZdlZxUUFaRGQlMkZtWUlnaVUlMkZocDhKa3NudG9IdGZDalhUQnRhTzNGWDQlM0Q',
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
                    'elorank': [team.find('div', class_='subname').text.strip() for i, team in enumerate(soup) if i % 2 == 0]
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

                featured_games = []
            

                for c, n, r in zip(games['champions'], nicknames, games['regions']): # games['elorank']):
                    
                    champs = ' | '.join(c)
                    names_region = '_|_'.join([f"{name}:{r.split('/')[2].upper()}" for name in n])
                    whole_string = f"{champs}-|-{names_region}"
                    featured_games.append(whole_string)
                
                if bronze:
                    MCFStorage.write_data(route=('MatchesPoroBronze', region,), value=featured_games)
                else:
                    MCFStorage.write_data(route=('MatchesPoroRegions', region,), value=featured_games)
                    
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
            except asyncio.exceptions.TimeoutError:
                missing_regions += 1
            except (ClientConnectionError, ClientProxyConnectionError):
                missing_regions = 20
                
    missing_regions = 0
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main_aram(champion_name))
    
    return missing_regions


def async_riot_parsing():

    """
        This function parsing games from Riot API Featured Games into
        GameData.json and returning count of missing regions
    
    """

    async def parsing(region):
        nonlocal missing_regions
        
        async with ClientSession() as session:
            async with session.get(url=FEATURED_GAMES_URL.format(region=region), 
                                   **riot_headers) as response:
                
                data = await response.json()
                
                try:
                    gameList = data['gameList']
                    if len(gameList) < 1:
                        missing_regions += 1
                        return
                except KeyError:
                    missing_regions += 1
                    return

        
                routelist = []
                for s in range(0, len(gameList)):
                    
                    # Создаем список из id персонажей для дальнейшей конвертации в имени
                    id_names = [int(gameList[s]['participants'][k]['championId']) for k in range(5)]

                    # Создаем список конвертированных id в имена персонажей
                    champ_list = [ALL_CHAMPIONS_IDs.get(id_name) for id_name in id_names]
                    
                    champ_string = ' | '.join([str(item) for item in champ_list])
                    summoners = '_|_'.join([f"{i['summonerName']}:{gameList[s]['platformId']}" for i in gameList[s]['participants']])
                            
                    routelist.append(f"{champ_string}-|-{summoners}")
                MCFStorage.write_data(
                    route=('MatchesAPI', region.upper(), ), 
                    value=routelist
                    )
                    
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
    
    return missing_regions
