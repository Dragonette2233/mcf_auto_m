from PIL import Image, ImageGrab
import numpy as np
from skimage.metrics import structural_similarity as ssim
from mcf.static import (
    PATH,
    GREYSHADE

)

from mcf.pillow import (
    greyshade_array,
    green_fill_percents
)

class CharsRecognition:
    
    
    
    @classmethod    
    def cut_from_screenshot(cls):
        """
        This method cuts characters from left and right side on stream screen, then
        saving it to images lib

        """

        y = [160, 263, 366, 469, 572, 194, 297, 400, 503, 606]
        x = [45, 58, 1858, 1873]
        
        im = ImageGrab.grab()
        
        if im.size != (1920, 1080):
            im = im.resize((1920, 1080))
        
        crops = (
            im.crop((x[0], y[0], x[1], y[5])), 
            im.crop((x[0], y[1], x[1], y[6])),
            im.crop((x[0], y[2], x[1], y[7])), 
            im.crop((x[0], y[3], x[1], y[8])),
            im.crop((x[0], y[4], x[1], y[9])),

            im.crop((x[2], y[0], x[3], y[5])),
            im.crop((x[2], y[1], x[3], y[6])),
            im.crop((x[2], y[2], x[3], y[7])), 
            im.crop((x[2], y[3], x[3], y[8])),
            im.crop((x[2], y[4], x[3], y[9]))
        )

        for a, b in tuple(zip(range(0,5), range(5, 10))):
            crops[a].save(PATH.BLUE_CUT.format(indx=a))
            crops[b].save(PATH.RED_CUT.format(indx=a))
    
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
        main_images_arr = [greyshade_array(img) for img in main_images]

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
    
    @classmethod
    def get_compare(cls, cut_image, type, position, team=None):

        match type, position, team:
            case 'tw_access', pos, None:
                main_image_arr = np.array(Image.open(PATH.TOWER_ACCESS))
                similarity_index = ssim(main_image_arr, cut_image)
                if similarity_index > 0.75:
                    return True
                else:
                    return False
            case 'gold', pos, None:
                main_images = [Image.open(PATH.fGOLD.format(gl=i)) for i in range(10)]
            case 'towers', pos, 'blue':
                main_images = [Image.open(PATH.fBLUE_TOWER.format(tw=i)) for i in range(5)]
            case 'towers', pos, 'red':
                main_images = [Image.open(PATH.fRED_TOWER.format(tw=i)) for i in range(5)]
            case _:
                print(type, team, position)
                raise ValueError('Undefined value in get_compare()') 
                # return
        
        main_images_arr = [np.array(img) for img in main_images]

        for idx, compare_img in enumerate(main_images_arr):
            similarity_index = ssim(compare_img, cut_image, win_size=3)

            # Если найдено более высокое сходство, сохраняем его и путь к изображению
            if similarity_index > 0.75:
                return idx
        else:
            return ''

    @classmethod
    def towers_healh_recognition(cls):
        # 20, 850, 59, 902
        
        image = ImageGrab.grab()
        
        if not cls.get_compare(np.array(image.crop((20, 850, 59, 902)).convert('L')), 'tw_access', 0):
            return False

        rect = image.crop((76, 865, 174, 867))
        result = green_fill_percents(rect)
        
        return result
    
    @classmethod
    def gold_recognition(cls, image: Image.Image):
        
        # print(cls.gold_shift)
        
        blue_gold = (
            cls.get_compare(np.array(image.crop((126 - cls.gold_shift, 12, 134 - cls.gold_shift, 28)).convert('L')), 'gold', 0),
            cls.get_compare(np.array(image.crop((136 - cls.gold_shift, 12, 144 - cls.gold_shift, 28)).convert('L')), 'gold', 1),
            cls.get_compare(np.array(image.crop((151 - cls.gold_shift, 12, 159 - cls.gold_shift, 28)).convert('L')), 'gold', 2),
        )
        red_gold = (
            cls.get_compare(np.array(image.crop((430 - cls.gold_shift, 12, 438 - cls.gold_shift, 28)).convert('L')), 'gold', 0),
            cls.get_compare(np.array(image.crop((440 - cls.gold_shift, 12, 448 - cls.gold_shift, 28)).convert('L')), 'gold', 1),
            cls.get_compare(np.array(image.crop((455 - cls.gold_shift, 12, 463 - cls.gold_shift, 28)).convert('L')), 'gold', 2),
        )
        
        
        return (blue_gold, red_gold)
    
    @classmethod
    def screen_score_recognition(cls, image=None) -> dict[str, int]:

        """

        Returns:
            gold and towers count data
        """
        
        screen = ImageGrab.grab()
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
        
        blue_towers = cls.get_compare(np.array(image.crop((60, 13, 75, 29)).convert('L')), 'towers', 0, 'blue')
        red_towers = cls.get_compare(np.array(image.crop((498, 13, 514, 29)).convert('L')), 'towers', 0, 'red')
        
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