import os
from .ids import ALL_CHAMPIONS_IDs


class BasePATH:
    
    MCF_BOT: str = os.environ.get('MCF_BOT')
    BETCASTER: str = os.environ.get('BETCASTER')
    _mcf_tg_storage = os.path.join(MCF_BOT, 'mcf_telegram', 'storage')
    _untracking = os.path.join(MCF_BOT, 'untracking')
    _snips = os.path.join(MCF_BOT, 'mcf', 'snips')
    _ssim = os.path.join(MCF_BOT, 'ssim_score_data')
    _images = os.path.join(MCF_BOT, 'mcf', 'images_lib')
    _comparable = os.path.join(_images, 'comparable')
    _chars_cut = os.path.join(_images, 'chars')


class PATH():
    
    base = BasePATH
    
    """
        All pathes for app images
    """

    SCREEN_GAMESCORE = os.path.join(base._images, 'gamescore_PIL.png')
    STATISTICS = os.path.join(base.MCF_BOT, 'mcf', 'stats_lib', 'stats_59.txt')

    """
        Untracking pathes
    """
    UPARAMS = os.path.join(base.MCF_BOT, 'untracking', 'uparams.json')
    PR_TRACE = os.path.join(base._untracking, 'pr_trace.json')
    PR_TRACK = os.path.join(base._untracking, 'pr_tracking.txt')
    CASTER_PROFILES_BASE = os.path.join(base.BETCASTER,'betcaster', 'caster-profiles', 'caster_profiles_base.json')
    CASTER_PROFILES_LOGS = os.path.join(base.BETCASTER,'betcaster', 'caster-logs')

    """
        Data for screen score recognizing (Time, kills, towers)
    """

    fBLUE_TOWER = os.path.join(base._ssim, 'blue_towers', '{tw}.png')
    fRED_TOWER = os.path.join(base._ssim, 'red_towers', '{tw}.png')
    fGOLD = os.path.join(base._ssim, 'gold', '{gl}.png')
    TOWER_ACCESS = os.path.join(base._ssim, 'tw_access', 'access.png')
    
    BLUE_CUT = os.path.join(base._chars_cut, 'blue', 'char_{indx}.png')
    RED_CUT = os.path.join(base._chars_cut, 'red', 'char_{indx}.png')
    
    BLUE_IMAGES_TO_COMPARE = {
        char: os.path.join(BasePATH._chars_cut, 'origin', 'blue', f'{char.lower().capitalize()}.png') 
        for char in ALL_CHAMPIONS_IDs.values()
    }
    RED_IMAGES_TO_COMPARE = {
        char: os.path.join(BasePATH._chars_cut, 'origin', 'red', f'{char.lower().capitalize()}.png') 
        for char in ALL_CHAMPIONS_IDs.values()
    }


class Snippet:
    
    SPECTATOR = os.path.join(PATH.base._snips, 'spectate.bat')
    SCORE = os.path.join(PATH.base._snips, 'score.txt')
    GAMESTART = os.path.join(PATH.base._snips, 'gamestart.txt')
    ONLYPREDICT = os.path.join(PATH.base._snips, 'onlypredict.txt')


class TGSMP:
    """
        Telegram messages for responsing /commands
    """

    GREET_MESSAGE = open(os.path.join(PATH.base._snips, 'greet_message.txt'), 'r', encoding='utf-8').read()
    PR_CHANNEL_MESSAGE = open(os.path.join(PATH.base._snips, 'pr_channel_message.txt'), 'r', encoding='utf-8').read()
    MAIN_INFO = open(os.path.join(PATH.base._snips, 'bot_info_message.txt'), 'r', encoding='utf-8').read()
    BETS_INFO = open(os.path.join(PATH.base._snips, 'bets_start_message.txt'), 'r', encoding='utf-8').read()
    PREDICTS_ANSWER = open(os.path.join(PATH.base._snips, 'predicts_answer_sample.txt'), 'r', encoding='utf-8').read()

