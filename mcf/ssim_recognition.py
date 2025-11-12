# from mcf import pillow
import os
import numpy as np
from numpy.typing import NDArray
import logging
from typing import Any
from mcf.api import cmouse
from mcf import pillow
from skimage.metrics import structural_similarity as ssim
from static import PATH, CropCoords
from mcf.pillow import (
    greyshade_array,
    green_fill_percents
)

logger = logging.getLogger(__name__)

class GREYSHADE:
    BLUE_ARRAY = {
                char: greyshade_array(img) for char, img in PATH.BLUE_IMAGES_TO_COMPARE.items()
    }
    RED_ARRAY = {
                char: greyshade_array(img) for char, img in PATH.RED_IMAGES_TO_COMPARE.items()
    }


    CMP_RIOT = greyshade_array(os.path.join(PATH.base._comparable, 'ncmp_riot.png'))
    CMP_BLUE = greyshade_array(os.path.join(PATH.base._comparable, 'ncmp_blue.png'))
    CMP_RED = greyshade_array(os.path.join(PATH.base._comparable, 'ncmp_red.png'))
    # mCMP_RIOT = greyshade_array(os.path.join(PATH.base._comparable, 'mcmp_riot.png'))
    # mCMP_BLUE = greyshade_array(os.path.join(PATH.base._comparable, 'mcmp_blue.png'))
    # mCMP_RED = greyshade_array(os.path.join(PATH.base._comparable, 'mcmp_red.png'))
    # mCMP_LOADING = greyshade_array(os.path.join(PATH.base._comparable, 'mcmp_loading.png'))

class CharsRecognition:
    
    @classmethod    
    def cut_from_screenshot(cls):
        """
        This method cuts characters from left and right side on stream screen, then
        saving it to images lib

        """        
        im = pillow.take_screenshot()
        
        blue_crops = pillow.crop_team(im, CropCoords.X[0], CropCoords.X[1], CropCoords.Y)
        red_crops = pillow.crop_team(im, CropCoords.X[2], CropCoords.X[3], CropCoords.Y)
    
        for a in range(5):
            blue_crops[a].save(PATH.BLUE_CUT.format(indx=a))
            red_crops[a].save(PATH.RED_CUT.format(indx=a))
    
    @classmethod
    def get_recognized_characters(cls, team_color) -> list[str]:

        """
            Converts characters from image to str representation
            
            :returns list [str]: of 5 characters of income `team_color`

        """
        
        characters = []

        if team_color == 'blue':
            main_images = [PATH.BLUE_CUT.format(indx=idx) for idx in range(5)]
        else:
            main_images = [PATH.RED_CUT.format(indx=idx) for idx in range(5)]
                
        # Подготовка массива основного изображения для последующего сравнения
        main_images_arr = [greyshade_array(from_path=img) for img in main_images]

        best_similarity = 0
        best_character = None

        if team_color == 'blue':
            arr_images_compare = GREYSHADE.BLUE_ARRAY
        else:
            arr_images_compare = GREYSHADE.RED_ARRAY

        for main_img_arr in main_images_arr:

            for char, arr in arr_images_compare.items():
                similarity_index = ssim(main_img_arr, arr)

                if similarity_index > best_similarity:
                    best_similarity = similarity_index
                    best_character = char

            if best_character == 'Kayn_b':
                best_character = 'Kayn'
            characters.append(best_character)

            best_similarity = 0 
            best_character = None
        
        return characters
        
class ScoreRecognition:
    gold_shift = 1
    y_shift = 12

    # makee Y shift flexible  from 10 to 13
    
    @classmethod
    def is_game_started_spectator(cls, debug=False):

        """
            This script is checking if spectator game is ready
        """
        
        compare_slice_active = pillow.take_screenshot().crop((862, 2, 951, 22)).convert('L')
        compare_slice_main = pillow.open_image(os.path.join('.', 'mcf', 'images_lib', 'spectator_compare.png')).convert('L')
        np_active = np.array(compare_slice_active)
        np_main = np.array(compare_slice_main)

        similarity_index: float | Any = ssim(np_main, np_active)

        if debug:
            logger.info(similarity_index)

        if similarity_index > 0.949:
            # winscreen.make_league_foreground()
            cmouse.open_score_tab()
            logger.info('Spectator activated')
            return True
    
    @classmethod
    def is_game_started_browser(cls) -> bool:
        """
            This script is checking if game is avaliable on stream (map and players displayed)
            
            :returns True: if comparable images matches to cut images from stream
            
        """
        image_ = pillow.take_screenshot()

        # if not CF.SW.cache_done.is_active():
        #     np_mcmp_active = np.array(image_.crop((1648, 245, 1722, 331)).convert('L'))
        #     # if ssim(np_mcmp_active, GREYSHADE.mCMP_LOADING) > 0.93:
        #     #     from mcf.api.overall import MCFApi
        #     #     #MCFApi.cache_before_stream()
        #     #     CF.SW.cache_done.activate()
        
        cut_cmp_riot = image_.crop((1649, 372, 1686, 386)).convert('L')# .save('ncmp_riot.png')
        cut_cmp_blue = image_.crop((1693, 249, 1707, 256)).convert('L')# .save('ncmp_blue.png')
        cut_cmp_red = image_.crop((1836, 249, 1851, 256)).convert('L')# .save('ncmp_red.png')
        
        ssim_cut_riot: float | Any = ssim(np.array(cut_cmp_riot), GREYSHADE.CMP_RIOT)
        ssim_cut_blue: float | Any = ssim(np.array(cut_cmp_blue), GREYSHADE.CMP_BLUE)
        ssim_cut_red: float | Any = ssim(np.array(cut_cmp_red), GREYSHADE.CMP_RED)

        similarity = (
            ssim_cut_riot > 0.95,
            ssim_cut_red > 0.95,
            ssim_cut_blue > 0.95
        )
        
        if any(similarity):
            return True

        return False
    
    @classmethod
    def is_similar(cls, image_arr_1: NDArray, image_arr_2: NDArray, idx=0.75) -> bool:
        
        """
        Checking if one image is similar to another

        Returns:
            bool: if image similarity index is greater than deafult `idx`
        """
        
        similarity_index: float | Any = ssim(image_arr_1, image_arr_2, win_size=3)
        
        return  similarity_index > idx
        
    
    @classmethod
    def get_compare(cls, cut_image: np.ndarray, type, team=None):

        match type, team:
            case 'tw_access', None:
                main_image_arr = np.array(pillow.open_image(PATH.TOWER_ACCESS))
                return cls.is_similar(main_image_arr, cut_image)

            case 'gold', None:
                main_images = [pillow.open_image(PATH.fGOLD.format(gl=i)) for i in range(10)]
            case 'towers', 'blue':
                main_images = [pillow.open_image(PATH.fBLUE_TOWER.format(tw=i)) for i in range(5)]
            case 'towers', 'red':
                main_images = [pillow.open_image(PATH.fRED_TOWER.format(tw=i)) for i in range(5)]
            case _:
                # print(type, team)
                raise ValueError('Undefined value in get_compare()') 
                # return
        
        main_images_arr = [np.array(img) for img in main_images]

        for idx, compare_img in enumerate(main_images_arr):
            if cls.is_similar(compare_img, cut_image):
                return idx
        else:
            return ''

    @classmethod
    def towers_healh_recognition(cls):
        # 20, 850, 59, 902
        
        image = pillow.take_screenshot()
        
        if not cls.get_compare(
            greyshade_array(
                from_crop=(image, 20, 850, 59, 902)
                ), 'tw_access'):
            return False

        rect = pillow.crop_image(image, 76, 853, 175, 855)
        result = green_fill_percents(rect)
        
        return result
    
    @classmethod
    def gold_recognition(cls, image: pillow.ImageType) -> tuple[tuple[str]]:
        
        # print(cls.gold_shift)
        
        blue_gold = (
            cls.get_compare(greyshade_array(from_crop=(image, 126 - cls.gold_shift, 12, 134 - cls.gold_shift, 28)), 'gold'),
            cls.get_compare(greyshade_array(from_crop=(image, 136 - cls.gold_shift, 12, 144 - cls.gold_shift, 28)), 'gold'),
            cls.get_compare(greyshade_array(from_crop=(image, 151 - cls.gold_shift, 12, 159 - cls.gold_shift, 28)), 'gold'),
        )
        red_gold = (
            cls.get_compare(greyshade_array(from_crop=(image, 430 - cls.gold_shift, 12, 438 - cls.gold_shift, 28)), 'gold'),
            cls.get_compare(greyshade_array(from_crop=(image, 440 - cls.gold_shift, 12, 448 - cls.gold_shift, 28)), 'gold'),
            cls.get_compare(greyshade_array(from_crop=(image, 455 - cls.gold_shift, 12, 463 - cls.gold_shift, 28)), 'gold'),
        )
        
        
        return (blue_gold, red_gold)
    
    @classmethod
    def screen_score_recognition(cls, image=None) -> dict[str, int]:

        """

        Returns:
            gold and towers count data
        """
        
        screen = pillow.take_screenshot()
        if not image:
            # screen.width
            image = screen.crop((681, 7, 1261, 99))
        
    
        blue_gold, red_gold = cls.gold_recognition(image=image)
        
        if '' in blue_gold or '' in red_gold:
            if cls.gold_shift == 1:
                cls.gold_shift = 0
                blue_gold, red_gold = cls.gold_recognition(image=image)
            else:
                cls.gold_shift = 1
                blue_gold, red_gold = cls.gold_recognition(image=image)
 
        blue_golds = ''.join([str(i) for i in blue_gold[0:2]]) + '.' + str(blue_gold[2])
        red_golds = ''.join([str(i) for i in red_gold[0:2]]) + '.' + str(red_gold[2])
        
        if blue_golds == '.':#  or '' in blue_golds:
            blue_golds = 10.0
        if red_golds == '.':#  or '' in red_golds:
            red_golds = 10.0
        
        blue_towers = cls.get_compare(greyshade_array(from_crop=(image, 60, 13, 75, 29)), 'towers', 'blue')
        red_towers = cls.get_compare(greyshade_array(from_crop=(image, 503, 13, 519, 29)), 'towers', 'red')
        
        if blue_towers == '':
            blue_towers = 0
        if red_towers == '':
            red_towers = 0
        
        gamedata = {
            'blue_towers': int(blue_towers),
            'red_towers': int(red_towers),
            'blue_gold': float(blue_golds),
            'red_gold': float(red_golds),
            'is_active': True
        }

        return gamedata