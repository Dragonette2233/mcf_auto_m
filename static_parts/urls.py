class URL:
    
    # poro links
    FEATURED_GAMES = "https://{region}.api.riotgames.com/lol/spectator/v5/featured-games"
    PORO_BY_REGIONS = "https://porofessor.gg/current-games/{champion}/{region}/queue-450"
    PORO_ADVANCE = "https://porofessor.gg/current-games/{champion}/{region}/{elo}/queue-450"
    
    # riot links
    SUMMONER_BY_RIOTID = "https://{area}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{nickName}/{tagLine}"
    MATCHES_BY_PUUID = "https://{area}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=2"
    MATCH_BY_GAMEID = "https://{area}.api.riotgames.com/lol/match/v5/matches/{gameid}"
    ACTIVEGAME_BY_SUMMID = "https://{region}.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{summid}"
    
    FEATURED_GAMES = "https://{region}.api.riotgames.com/lol/spectator/v5/featured-games"

