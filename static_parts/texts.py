from .paths import Snippet


class TelegramStr:
    FAILURE = '❌'
    SUCCESS = '✅'
    SHARK = '🐳'
    OCTUPUS = '🐙'
    GREEN_CIRCLE = '🟢'
    BLUE_CIRCLE = '🔵'
    RED_CIRCLE = '🔴'
    EXCLAM_RED = '❗️'
    EXCLAM_WHITE = '❕'
    ARROW_UP = '🔼'
    ARROW_DOWN = '🔽'
    CLOCK = '⏳'

    # Predict notifications
    ttb_predict_half = '{0}PR 110.5Б FL_0.5{0}'.format(ARROW_UP)
    tb_predict_full = '{0}PR 110.5Б FL_1{0}'.format(ARROW_UP)
    
    tl_predict_half = '{0}PR 110.5М FL_0.5{0}'.format(ARROW_DOWN)
    tl_predict_middle = '{0}PR 110.5М FL_0.75{0}'.format(ARROW_DOWN)
    tl_predict_full = '{0}PR 110.5М FL_1{0}'.format(ARROW_DOWN)

    # Ended game notifications
    winner = {
        'blue': BLUE_CIRCLE + ' П1 -- {0} -- {1}',
        'red': RED_CIRCLE + ' П2 -- {0} -- {1}'
    }

    winner_opened = {
        'blue': GREEN_CIRCLE + BLUE_CIRCLE + ' П1 -- {0} -- {1}',
        'red': GREEN_CIRCLE + RED_CIRCLE + ' П2 -- {0} -- {1}'
    }

    # Started game
    SNIPPET_SCORE = open(Snippet.SCORE, 'r', encoding='utf-8').read()
    SNIPPET_GAMESTART = open(Snippet.GAMESTART, 'r', encoding='utf-8').read()

    game_founded = SUCCESS + ' {0}'
    game_not_founded = FAILURE + ' Игра не найдена'
    game_remake = FAILURE + ' Remake'

    events_opened = '\n\nTotal event {total_value}: ' + EXCLAM_WHITE + 'Opened'
    events_closed = '\n\nTotal event: ' + EXCLAM_RED + 'Closed'

    # Only predicts message
    only_pr_message = open(Snippet.ONLYPREDICT, 'r', encoding='utf-8').read()

