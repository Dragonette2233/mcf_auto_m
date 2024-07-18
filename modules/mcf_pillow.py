from PIL import Image, ImageGrab
from dynamic_data import CF
from modules import mcf_autogui
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
    from static_data import GREYSHADE

    image_ = ImageGrab.grab()

    if not CF.SW.cache_done.is_active():
        np_mcmp_active = np.array(image_.crop((1648, 245, 1722, 331)).convert('L'))
        if ssim(np_mcmp_active, GREYSHADE.mCMP_LOADING) > 0.93:
            from mcf_api import MCFApi
            MCFApi.cache_before_stream()
            CF.SW.cache_done.activate()
    
    cut_cmp_riot = image_.crop((1645, 366, 1683, 380)).convert('L')
    cut_cmp_blue = image_.crop((1689, 243, 1705, 250)).convert('L')
    cut_cmp_red = image_.crop((1832, 243, 1847, 250)).convert('L')
    
    np_cut_riot = np.array(cut_cmp_riot)
    np_cut_blue = np.array(cut_cmp_blue)
    np_cut_red = np.array(cut_cmp_red)

    similarity = [
        ssim(np_cut_riot, GREYSHADE.CMP_RIOT) > 0.93,
        ssim(np_cut_blue, GREYSHADE.CMP_BLUE) > 0.93,
        ssim(np_cut_red, GREYSHADE.CMP_RED) > 0.93,
        ssim(np_cut_riot, GREYSHADE.mCMP_RIOT) > 0.93,
        ssim(np_cut_blue, GREYSHADE.mCMP_BLUE) > 0.93,
        ssim(np_cut_red, GREYSHADE.mCMP_RED) > 0.93,
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
        mcf_autogui.open_score_tab()
        logger.info('Spectator activated')
        return True

def generate_scoreboard():

    from modules.ssim_recognition import ScoreRecognition
    # from modules.mcf_storage import MCFStorage
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
        if not blue_t1_health or blue_t1_health > CF.TW_HP.blue_backup:
            blue_t1_health = CF.TW_HP.blue_backup
        else:
            CF.TW_HP.blue_backup = blue_t1_health
    else:
        blue_t1_health = 0

    if score['blue_towers'] == 0:
        mcf_autogui.click(1811, 919)
        time.sleep(0.05)
        mcf_autogui.doubleClick(951, 490)
        time.sleep(0.05)
        red_shot = ImageGrab.grab()
        red_t1_health = ScoreRecognition.towers_healh_recognition(image=red_shot)
        if not red_t1_health or red_t1_health > CF.TW_HP.red_backup:
            red_t1_health = CF.TW_HP.red_backup
        else:
            CF.TW_HP.red_backup = red_t1_health
    else:
        red_t1_health = 0
    
    score['blue_t1_hp'] = blue_t1_health
    score['red_t1_hp'] = red_t1_health

    # MCFStorage.save_score(score=score)

    return score


def is_green(pixel, threshold=100):
    """Проверка, является ли пиксель зеленым.
    Порог можно настроить для более точного распознавания зеленого цвета."""
    r, g, b = pixel
    return g > threshold and g > r and g > b

def green_fill_percents(cropped_image, green_threshold=100, fill_threshold=0.8) -> int:
    
    # Возвращает int от 0 до 100 (проценты башни)
    
    """
    Проверить заполненность прямоугольника зелеными оттенками.
    
    :param cropped_image: обрезанное изображение (прямоугольник).
    :param green_threshold: порог для компоненты G, чтобы пиксель считался зеленым.
    :param fill_threshold: доля зеленых пикселей для определения заполненности.
    """
    pixels = cropped_image.load()
    width, height = cropped_image.size
    
    green_pixels = 0
    total_pixels = width * height
    
    for x in range(width):
        for y in range(height):
            if is_green(pixels[x, y], green_threshold):
                green_pixels += 1
    
    green_fill_ratio = green_pixels / total_pixels
    return int(green_fill_ratio * 100)