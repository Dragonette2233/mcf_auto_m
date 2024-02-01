from PIL import Image, ImageGrab
import numpy as np
import os
from skimage.metrics import structural_similarity as ssim
from modules.mcf_pillow import convert_to_greyshade
from mcf_data import (
    SCREENSHOT_FILE_PATH,
    GTIME_DATA_PATH,
    BLUE_SCORE_PATH,
    RED_SCORE_PATH,
    BLUE_TOWER_PATH,
    RED_TOWER_PATH,
    ALL_CHAMPIONS_IDs,

)

BLUE_CUT_PATH = os.path.join('.', 
                        'images_lib', 
                        'chars',  
                        'blue', 'char_{indx}.png')
RED_CUT_PATH = os.path.join('.', 
                        'images_lib', 
                        'chars', 
                        'red', 'char_{indx}.png')

BLUEPATH_IMAGES_TO_COMPARE = {
    char: os.path.join('.', 
                        'images_lib', 
                        'chars', 
                        'origin', 
                        'blue', f'{char.lower().capitalize()}.png') 
                        for char in ALL_CHAMPIONS_IDs.values()
    }
REDPATH_IMAGES_TO_COMPARE = {
    char: os.path.join('.', 
                        'images_lib', 
                        'chars', 
                        'origin', 
                        'red', f'{char.lower().capitalize()}.png') 
                        for char in ALL_CHAMPIONS_IDs.values()
    }
BLUE_GREYSHADE_COMPARE = {
            char: convert_to_greyshade(img) for char, img in BLUEPATH_IMAGES_TO_COMPARE.items()
}
RED_GREYSHADE_COMPARE = {
            char: convert_to_greyshade(img) for char, img in REDPATH_IMAGES_TO_COMPARE.items()
}
BLUE_ARRIMAGES_COMPARE = {
    char: np.array(img) for char, img in BLUE_GREYSHADE_COMPARE.items()
}
RED_ARRIMAGES_COMPARE = {
    char: np.array(img) for char, img in RED_GREYSHADE_COMPARE.items()
}

class RecognizedCharacters:
    def __init__(self, team_color: str) -> None:
        """
            Team color should be 'blue' or 'red'

        """
        self.characters = []
        self.team_color = team_color
                                
    def screenshot(self):
        screen = ImageGrab.grab()
        screen.save(SCREENSHOT_FILE_PATH)

    def cut_from_screenshot(self):

        y = [160, 263, 366, 469, 572, 194, 297, 400, 503, 606]
        x = [45, 58, 1858, 1873]
        
        im = Image.open(SCREENSHOT_FILE_PATH)
        
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
            crops[a].save(BLUE_CUT_PATH.format(indx=a))
            crops[b].save(RED_CUT_PATH.format(indx=a))
    
    def compare_shorts(self):

        main_images = [os.path.join('.', 
                                'images_lib', 
                                'chars', 
                                self.team_color, 
                                f'char_{i}.png') for i in range(5)] # Путь к основному изображению (35x35)
        main_images_converted = [Image.open(img).convert('L') for img in main_images]

        # Подготовка массива основного изображения для последующего сравнения
        main_images_arr = [np.array(img) for img in main_images_converted]

        best_similarity = 0
        best_character = None

        if self.team_color == 'blue':
            arr_images_compare = BLUE_ARRIMAGES_COMPARE
        else:
            arr_images_compare = RED_ARRIMAGES_COMPARE

        for main_img_arr in main_images_arr:

            for char, arr in arr_images_compare.items():
                similarity_index = ssim(main_img_arr, arr)

                if similarity_index > best_similarity:
                    best_similarity = similarity_index
                    best_character = char

            # if best_similarity > 0.56:
            self.characters.append(best_character)
            
            best_similarity = 0 
            best_character = None
        
        # self.characters = simul_team
        
    def run(self):
        self.screenshot()
        self.cut_from_screenshot()
        self.compare_shorts()
        # return recognized_list

        
class ScoreRecognition:
    @classmethod
    def get_compare(cls, cut_image, type, position, team=None):

        match type, position, team:
            case 'gtime', 0, None:
                main_images = [Image.open(os.path.join(GTIME_DATA_PATH, f'{position}', f'{i}.png')) for i in range(4)]
            case 'gtime', 1 | 3, None:
                main_images = [Image.open(os.path.join(GTIME_DATA_PATH, f'{position}', f'{i}.png')) for i in range(10)]
            case 'gtime', 2, None:
                main_images = [Image.open(os.path.join(GTIME_DATA_PATH, f'{position}', f'{i}.png')) for i in range(6)]
            case 'score', pos, 'blue':
                main_images = [Image.open(os.path.join(BLUE_SCORE_PATH.format(pos=pos), f'{i}.png')) for i in range(10)]
            case 'score', pos, 'red':
                main_images = [Image.open(os.path.join(RED_SCORE_PATH.format(pos=pos), f'{i}.png')) for i in range(10)]
            case 'towers', pos, 'blue':
                main_images = [Image.open(os.path.join(BLUE_TOWER_PATH, f'{i}.png')) for i in range(5)]
            case 'towers', pos, 'red':
                main_images = [Image.open(os.path.join(RED_TOWER_PATH, f'{i}.png')) for i in range(5)]
            case _:
                print(type, team, position)
                raise ValueError('Undefined value in get_compare()') 
                # return
        
        main_images_arr = [np.array(img) for img in main_images]

        for idx, compare_img in enumerate(main_images_arr):
            similarity_index = ssim(compare_img, cut_image)

            # Если найдено более высокое сходство, сохраняем его и путь к изображению
            if similarity_index > 0.75:
                return idx
        else:
            return ''
            
    @classmethod
    def screen_score_recognition(cls, image=None) -> dict[str, int]:

        screen = ImageGrab.grab()
        if not image:
            image = screen.crop((681, 7, 1261, 99))
        
        final_time = [
            cls.get_compare(np.array(image.crop((264, 72, 271, 85)).convert('L')), 'gtime', 0),
            cls.get_compare(np.array(image.crop((273, 72, 280, 85)).convert('L')), 'gtime', 1),
            cls.get_compare(np.array(image.crop((287, 72, 294, 85)).convert('L')), 'gtime', 2),
            cls.get_compare(np.array(image.crop((296, 72, 304, 85)).convert('L')), 'gtime', 3)
        ]
        
        for i, val in enumerate(final_time):
            if val == '':
                final_time[i] = 0
                

        blue_score = [
            cls.get_compare(np.array(image.crop((225, 18, 242, 41)).convert('L')), 'score', 0, 'blue'),
            cls.get_compare(np.array(image.crop((243, 18, 260, 41)).convert('L')), 'score', 1, 'blue')
        ]

        red_score = [
            cls.get_compare(np.array(image.crop((309, 18, 328, 41)).convert('L')), 'score', 0, 'red'),
            cls.get_compare(np.array(image.crop((329, 18, 347, 41)).convert('L')), 'score', 1, 'red')
        ]

        blue_towers = cls.get_compare(np.array(image.crop((60, 13, 75, 29)).convert('L')), 'towers', 0, 'blue')
        red_towers = cls.get_compare(np.array(image.crop((498, 13, 514, 29)).convert('L')), 'towers', 0, 'red')

        str_final_time = f'{final_time[0]}{final_time[1]}:{final_time[2]}{final_time[3]}' # XX:XX
        minutes, seconds = map(int, str_final_time.split(':'))
        blue_kills = ''.join([str(i) for i in blue_score])
        red_kills = ''.join([str(i) for i in red_score])


        total_seconds = minutes * 60 + seconds

        if blue_score[0] == 0:
            blue_score.remove(0)
        
        gamedata = {
            'time': total_seconds,
            'blue_kills': int(blue_kills) if blue_kills !='' else 0,
            'red_kills': int(red_kills) if red_kills !='' else 0,
            'blue_towers': int(blue_towers) if blue_towers != '' else 0,
            'red_towers': int(red_towers) if red_towers != '' else 0,
            'is_active': True
        }

        return gamedata

    @classmethod
    def collecting_ssim_data(cls, **kwargs):

        screen = ImageGrab.grab()
        image = screen.crop((681, 7, 1261, 99))
        image.save('.\\susu.png')


        if 'bl_tw' in kwargs:
            image.crop((60, 13, 75, 29)).convert('L').save(os.path.join('.', 'ssim_score_data', 'team_blue', 'towers', f'{kwargs["bl_tw"]}.png')) # work
        if 'rd_tw' in kwargs:
            image.crop((498, 13, 514, 29)).convert('L').save(os.path.join('.', 'ssim_score_data', 'team_red', 'towers', f'{kwargs["rd_tw"]}.png')) # work

        if 'bl_sc_0' in kwargs:
            image.crop((225, 18, 242, 41)).convert('L').save(os.path.join('.', 'ssim_score_data', 'team_blue', 'score_0', f'{kwargs["bl_sc_0"]}.png')) # work
        if 'bl_sc_1' in kwargs:
            image.crop((243, 18, 260, 41)).convert('L').save(os.path.join('.', 'ssim_score_data', 'team_blue', 'score_1', f'{kwargs["bl_sc_1"]}.png')) # work

        if 'rd_sc_0' in kwargs:
            image.crop((309, 18, 328, 41)).convert('L').save(os.path.join('.', 'ssim_score_data', 'team_red', 'score_0', f'{kwargs["rd_sc_0"]}.png')) # work
        if 'rd_sc_1' in kwargs:
            image.crop((329, 18, 347, 41)).convert('L').save(os.path.join('.', 'ssim_score_data', 'team_red', 'score_1', f'{kwargs["rd_sc_1"]}.png')) # work

        if 'g_0' in kwargs:
            image.crop((264, 72, 271, 85)).convert('L').save(os.path.join('.', 'ssim_score_data', 'gametime', '0', f'{kwargs["g_0"]}.png')) # # 6x13
        if 'g_1' in kwargs:
            image.crop((273, 72, 280, 85)).convert('L').save(os.path.join('.', 'ssim_score_data', 'gametime', '1', f'{kwargs["g_1"]}.png'))
        if 'g_2' in kwargs:
            image.crop((287, 72, 294, 85)).convert('L').save(os.path.join('.', 'ssim_score_data', 'gametime', '2', f'{kwargs["g_2"]}.png'))
        if 'g_3' in kwargs:
            image.crop((296, 72, 304, 85)).convert('L').save(os.path.join('.', 'ssim_score_data', 'gametime', '3', f'{kwargs["g_3"]}.png')) 