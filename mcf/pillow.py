import logging
import numpy as np
from PIL import Image, ImageGrab

ImageType = Image.Image
logger = logging.getLogger(__name__)

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

