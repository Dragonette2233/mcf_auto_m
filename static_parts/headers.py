from .paths import PATH

HEADERS = {
    'authority': 'lite.1xbet-new.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
}

STATS_BASE_ITERATOR = open(PATH.STATISTICS, 'r').readlines().__iter__()

COOKIES = {
    'auid': 'LY0LGGVJT9xF3cMHBakaAg==',
    'SESSION': '22fdb02ab99445348a011c35f47c6452',
    'lng': 'ru',
    '_cfvwab': '-1',
    'cookies_agree_type': '3',
    'tzo': '3',
    'is12h': '0',
    'che_g': '3c2afae5-894d-df7a-91d5-ba2642fb4db5',
    'sh.session.id': '798cfbe4-33cb-434c-affa-b0862a224c4f',
    '_ga': 'GA1.1.368426760.1699302170',
    '_ym_uid': '1699731283765603681',
    '_ym_d': '1699731283',
    '_ym_isad': '1',
    '_ga_7JGWL9SV66': 'GS1.1.1699729869.10.1.1699731302.34.0.0',
    'ggru': '188',
    'platform_type': 'mobile',
    '_ga_0NQW4X2MPH': 'GS1.1.1699731283.1.1.1699737050.59.0.0',
    'window_width': '802',
}

