from PIL import Image, ImageChops, ImageGrab
from .mcf_storage import MCFStorage
import os
import logging
import numpy as np
from skimage.metrics import structural_similarity as ssim
from mcf_data import GREYSHADE_CLOCKS_CUT

logger = logging.getLogger(__name__)

def convert_to_greyshade(img):
    return Image.open(img).convert('L')

def is_game_started():

    screen_cut = ImageGrab.grab().crop((1855, 310, 1872, 320)).convert('L')
    np_cut = np.array(screen_cut)

    diff = ssim(np_cut, GREYSHADE_CLOCKS_CUT)

    if diff > 0.93:
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
    screen = ImageGrab.grab()
    score = screen.crop((681, 7, 1261, 99))
    scoredata = ScoreRecognition.screen_score_recognition(image=score)
    MCFStorage.save_score(score=scoredata)
    
    items_build = screen.crop((602, 850, 1334, 1078))
    items_build.save(os.path.join('images_lib', 'buildcrop.png'))
    return scoredata