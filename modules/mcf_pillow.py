from PIL import Image, ImageChops, ImageGrab
from global_data import TowersHealth
import os
import logging
import time
import numpy as np
from skimage.metrics import structural_similarity as ssim
# from mcf_data import Validator

logger = logging.getLogger(__name__)

def greyshade_array(image_path):
    
    return np.array(Image.open(image_path).convert('L'))

def is_game_started():
    from global_data import Validator
    from mcf_data import (
        # Validator,
        GREYSHADE_CMP_BLUE,
        GREYSHADE_CMP_RED,
        GREYSHADE_CMP_RIOT,
        GREYSHADE_mCMP_BLUE,
        GREYSHADE_mCMP_RED,
        GREYSHADE_mCMP_RIOT
    )
    # print(bozya)
    image_ = ImageGrab.grab()
    
    # cut_cmp_map = image_.crop((1855, 310, 1872, 320)).convert('L')
    if Validator.active_mel_mirror:
        cut_cmp_riot = image_.crop((1645, 366, 1683, 380)).convert('L')
        cut_cmp_blue = image_.crop((1689, 243, 1705, 250)).convert('L')
        cut_cmp_red = image_.crop((1832, 243, 1847, 250)).convert('L')
    else:
        cut_cmp_riot = image_.crop((1645, 330, 1683, 344)).convert('L')
        cut_cmp_blue = image_.crop((1689, 207, 1705, 214)).convert('L')
        cut_cmp_red = image_.crop((1832, 207, 1847, 214)).convert('L')
    # np_cut_map = np.array(cut_cmp_map)
    np_cut_riot = np.array(cut_cmp_riot)
    np_cut_blue = np.array(cut_cmp_blue)
    np_cut_red = np.array(cut_cmp_red)

    # diff_1 = ssim(np_cut_map, GREYSHADE_CMP_MAP)
    similarity = [
        ssim(np_cut_riot, GREYSHADE_CMP_RIOT) > 0.93,
        ssim(np_cut_blue, GREYSHADE_CMP_BLUE) > 0.93,
        ssim(np_cut_red, GREYSHADE_CMP_RED) > 0.93,
        ssim(np_cut_riot, GREYSHADE_mCMP_RIOT) > 0.93,
        ssim(np_cut_blue, GREYSHADE_mCMP_BLUE) > 0.93,
        ssim(np_cut_red, GREYSHADE_mCMP_RED) > 0.93,
            ]

    if any(similarity):
        return True

def is_league_stream_active(debug=False):

    compare_slice_active = ImageGrab.grab().crop((862, 2, 951, 22)).convert('L')
    compare_slice_main = Image.open(os.path.join('.', 'images_lib', 'spectator_compare.png')).convert('L')
    np_active = np.array(compare_slice_active)
    np_main = np.array(compare_slice_main)

    similarity_index = ssim(np_main, np_active)

    if debug:
        logger.info(similarity_index)

    if similarity_index > 0.949:
        return True

def reset_towers_backup():
    TowersHealth.reset()
    
def generate_scoreboard():

    from modules.ssim_recognition import ScoreRecognition
    from modules.mcf_storage import MCFStorage
    from modules import mcf_autogui

    blue_shot = None
    red_shot = None
   
    score = ScoreRecognition.screen_score_recognition()

    if score['red_towers'] == 0:
        mcf_autogui.click(1752, 970)
        time.sleep(0.05)
        mcf_autogui.doubleClick(936, 620)
        time.sleep(0.05)
        blue_shot = ImageGrab.grab()
        blue_t1_health = ScoreRecognition.towers_healh_recognition(image=blue_shot)
        if not blue_t1_health:
            blue_t1_health = TowersHealth.blue_backup
        else:
            TowersHealth.blue_backup = blue_t1_health
    else:
        blue_t1_health = 0

    if score['blue_towers'] == 0:
        mcf_autogui.click(1811, 919)
        time.sleep(0.05)
        mcf_autogui.doubleClick(951, 490)
        time.sleep(0.05)
        red_shot = ImageGrab.grab()
        red_t1_health = ScoreRecognition.towers_healh_recognition(image=red_shot)
        if not red_t1_health:
            red_t1_health = TowersHealth.red_backup
        else:
            TowersHealth.red_backup = red_t1_health
    else:
        red_t1_health = 0
    
    # screen = ImageGrab.grab()
    # score = blue_shot.crop((681, 7, 1261, 99))
    # scoredata = ScoreRecognition.screen_score_recognition(image=score)
    score['blue_t1_hp'] = blue_t1_health
    score['red_t1_hp'] = red_t1_health

    MCFStorage.save_score(score=score)
    
    # items_build = blue_shot.crop((602, 850, 1334, 1078))
    # items_build.save(os.path.join('images_lib', 'buildcrop.png'))

    

    return score