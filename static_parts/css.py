class CropCoords:
    Y = (160, 263, 366, 469, 572, 194, 297, 400, 503, 606)
    X = (45, 58, 1858, 1873)


class MelCSS:
    MARKETS_CONTENT = 'div.game-markets-content'
    MARKETS_GROUP = 'div.ui-accordion.game-markets-group'
    LOCK_ICON = 'span.ico.ui-market__lock'
    LOCK_ICON_SVG = 'svg.ui-ico--lock.ui-ico.ui-market__lock'
    MARKET_BUTTON = 'span.ui-market__name'
    
    GAMES_DASHBOARD_XPATH = '/html/body/div[1]/div/div/div[3]/div[2]/div/div[1]/div/div[2]/div/div/div[2]/main/div[2]/div/div/div/div[2]/div/ul/li[1]'
    SPAN_OPEN_STREAM_XPATH = '//*[@id="__BETTING_APP__"]/div[2]/div/div/div[2]/main/div[2]/div/div/div/div[2]/div/ul/li[1]/ul/li/div[1]/span[2]/span[2]/div/button/span'
    
    GAMES_DASHBOARD = 'li.ui-dashboard-champ.dashboard-champ.dashboard__champ.ui-dashboard-champ--theme-gray'
    GAMES_DASHBOARD_alt = 'li.dashboard-champ-body.dashboard-champ dashboard__champ'
    ARAM_TITLE_OUTER = 'span.caption.ui-dashboard-champ-name__caption.caption--size-m'
    ARAM_TITLE_OUTER_alt = 'div ui-dashboard-champ-name dashboard-champ__name ui-dashboard-cell ui-dashboard-champ-name dashboard-champ__name'.replace(' ', '.')
    ARAM_TITLE_OUTER_alt_s = 'div.dashboard-champ-name'
    ARAM_TITLE_OUTER_alt_s2 = 'span.ui-caption--size-m.ui-caption--color-clr-strong-alt.ui-caption--no-wrap.ui-caption.dashboard-champ-name__caption'

    ARAM_TITLE_INNER = 'span.caption__label'
    ARAM_TITLE_INNER_alt = 'span ui-caption--size-m ui-caption--color-clr-strong-alt ui-caption--no-wrap ui-caption ui-dashboard-champ-name__caption'.replace(' ', '.')
    ARAM_TITLE_INNER_alt_s = 'span ui-caption--size-m ui-caption--color-clr-strong-alt ui-caption--no-wrap ui-caption dashboard-champ-name__caption'.replace(' ', '.')
    ARAM_GAME_LINK = 'a.dashboard-game-block__link.dashboard-game-block-link'

    
    # SPAN_OPEN_STREAM = 'span.dashboard-game-action-bar__group'
    # SPAN_OPEN_STREAM_ALT = 'span.ico--play-circle.ico--size-xxs.ico.dashboard-game-action-bar__ico'
    
    
    BUTTON_OPEN_STREAM = 'button.dashboard-game-action-bar__item.has-tooltip'
    BUTTON_OPEN_STREAM_ALT = 'button.dashboard-game-action-bar__item.has-tooltip'
    BUTTON_REJECT_LIVE = 'button.ui-button.dashboard-redirect-message-timer__btn.ui-button--size-m.ui-button--theme-gray.ui-button--rounded'
    
    VIDEO_CONTAINER = 'section.media-container.media-container--theme-primary.media-side__item'
    VIDEO_PLAYER = "video.video"

