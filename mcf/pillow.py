from PIL import Image, ImageGrab
from mcf.dynamic import CF
from mcf import autogui
import os
import logging
import numpy as np
from skimage.metrics import structural_similarity as ssim
from mcf import autogui

ImageType = Image.Image
logger = logging.getLogger(__name__)
y_shift = 10


def crop_team(image: ImageType, x_start, x_end, y_positions):
    crops = [crop_image(image, x_start, y_positions[i], x_end, y_positions[i + 5]) for i in range(5)]
    return crops

def crop_image(image: ImageType, x_start, y_start, x_end, y_end):
    return image.crop((x_start, y_start, x_end, y_end))

def take_screenshot() -> ImageType:
    
    im = ImageGrab.grab()
    if im.size != (1920, 1080):
        im = im.resize((1920, 1080))
    
    return im

def open_image(path: str):
    return Image.open(path)

def greyshade_array(from_path: str = None, from_crop: tuple[ImageType | int] = None) -> np.ndarray:
    
    """
        Converting image to numpy array with shades of grey\n
        `from_path` - string repr of image PATH\n
        `from_crop` - tuple of (ImageType, x1, x2, y1, y2)

    """
    
    if from_path:
        image = Image.open(from_path)
    elif from_crop:
        img, *coords = from_crop
        if len(coords) == 4 and isinstance(img, Image.Image):
            image = img.crop(coords)
        else:
            raise ValueError("from_crop must contain an image and 4 integer coordinates")
    
    return np.array(image.convert('L'))

def is_game_started() -> bool:
    """
        This script is checking if game is avaliable on stream (map and players displayed)
        
        :returns True: if comparable images matches to cut images from stream
        
    """
    
    
    from mcf.static import GREYSHADE

    image_ = ImageGrab.grab()

    if not CF.SW.cache_done.is_active():
        np_mcmp_active = np.array(image_.crop((1648, 245, 1722, 331)).convert('L'))
        if ssim(np_mcmp_active, GREYSHADE.mCMP_LOADING) > 0.93:
            from mcf.api.overall import MCFApi
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

    return False

def is_league_stream_active(debug=False):

    """
        This script is checking if game is prepared for streaming (displayed League of Legends logo)
    """
    
    compare_slice_active = ImageGrab.grab().crop((862, 2, 951, 22)).convert('L')
    compare_slice_main = Image.open(os.path.join('.', 'mcf', 'images_lib', 'spectator_compare.png')).convert('L')
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
    """
        Checking if income `pixel` is green with default threshold
    """
    r, g, b = pixel
    return g > threshold and g > r and g > b

def green_fill_percents(cropped_image: Image.Image, green_threshold=100, fill_threshold=0.8) -> int:
    
    """
        Checking fill of rectangle with green color.
        
        :param cropped_image: cropped image (recatngle).
        :param green_threshold: threshold for the G component for a pixel to be considered green.
        :param fill_threshold: proportion of green pixels to determine occupancy.
        :returns int: from 0 to 100 (percantage of turret health)
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

