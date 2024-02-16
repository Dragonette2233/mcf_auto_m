from PIL import Image, ImageChops, ImageGrab
import os
import logging
import numpy as np
from skimage.metrics import structural_similarity as ssim
# from mcf_data import Validator

logger = logging.getLogger(__name__)

def greyshade_array(image_path):
    
    return np.array(Image.open(image_path).convert('L'))

def is_game_started():
    from mcf_data import (
        Validator,
        GREYSHADE_CMP_BLUE,
        GREYSHADE_CMP_RED,
        GREYSHADE_CMP_RIOT,
        GREYSHADE_mCMP_BLUE,
        GREYSHADE_mCMP_RED,
        GREYSHADE_mCMP_RIOT
    )

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
        ssim(np_cut_riot, GREYSHADE_CMP_RIOT) > 0.89,
        ssim(np_cut_blue, GREYSHADE_CMP_BLUE) > 0.89,
        ssim(np_cut_red, GREYSHADE_CMP_RED) > 0.89,
        ssim(np_cut_riot, GREYSHADE_mCMP_RIOT) > 0.89,
        ssim(np_cut_blue, GREYSHADE_mCMP_BLUE) > 0.89,
        ssim(np_cut_red, GREYSHADE_mCMP_RED) > 0.89,
            ]

    print(similarity)
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

def generate_scoreboard():
    from modules.ssim_recognition import ScoreRecognition
    from modules.mcf_storage import MCFStorage
    screen = ImageGrab.grab()
    score = screen.crop((681, 7, 1261, 99))
    scoredata = ScoreRecognition.screen_score_recognition(image=score)
    MCFStorage.save_score(score=scoredata)
    
    items_build = screen.crop((602, 850, 1334, 1078))
    items_build.save(os.path.join('images_lib', 'buildcrop.png'))
    return scoredata