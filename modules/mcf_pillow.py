from PIL import Image, ImageChops, ImageGrab
import os
import logging
import numpy as np
from skimage.metrics import structural_similarity as ssim

logger = logging.getLogger(__name__)

def greyshade_array(image_path):
    
    return np.array(Image.open(image_path).convert('L'))

def is_game_started():
    from mcf_data import GREYSHADE_CLOCKS_CUT, GREYSHADE_EMBL_CUT

    image_ = ImageGrab.grab()

    cut_map = image_.crop((1855, 310, 1872, 320)).convert('L')
    cut_riot_embleme = image_.crop((1645, 330, 1683, 344)).convert('L')
    np_cut_map = np.array(cut_map)
    np_cut_riot = np.array(cut_riot_embleme)

    diff_1 = ssim(np_cut_map, GREYSHADE_CLOCKS_CUT)
    diff_2 = ssim(np_cut_riot, GREYSHADE_EMBL_CUT)

    if diff_1 > 0.93 or diff_2 > 0.93:
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