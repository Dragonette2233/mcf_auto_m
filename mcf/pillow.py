from PIL import Image, ImageGrab
from mcf.dynamic_data import CF
from mcf import autogui
import os
import logging
import numpy as np
from skimage.metrics import structural_similarity as ssim
from mcf import autogui
# from mcf_data import Validator

logger = logging.getLogger(__name__)
y_shift = 10

def greyshade_array(image_path):
    
    return np.array(Image.open(image_path).convert('L'))

def is_game_started():
    from mcf.static_data import GREYSHADE

    image_ = ImageGrab.grab()

    if not CF.SW.cache_done.is_active():
        np_mcmp_active = np.array(image_.crop((1648, 245, 1722, 331)).convert('L'))
        if ssim(np_mcmp_active, GREYSHADE.mCMP_LOADING) > 0.93:
            from mcf_api import MCFApi
            MCFApi.cache_before_stream()
            CF.SW.cache_done.activate()
    
    cut_cmp_riot = image_.crop((1645, 366 + y_shift, 1683, 380 + y_shift)).convert('L')
    cut_cmp_blue = image_.crop((1689, 243 + y_shift, 1705, 250 + y_shift)).convert('L')
    cut_cmp_red = image_.crop((1832, 243 + y_shift, 1847, 250 + y_shift)).convert('L')
    
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
        autogui.open_score_tab()
        logger.info('Spectator activated')
        return True


def is_green(pixel, threshold=100):
    """Проверка, является ли пиксель зеленым.
    Порог можно настроить для более точного распознавания зеленого цвета."""
    r, g, b = pixel
    return g > threshold and g > r and g > b

def green_fill_percents(cropped_image: Image.Image, green_threshold=100, fill_threshold=0.8) -> int:
    
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