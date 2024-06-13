from PIL import Image, ImageGrab
import numpy as np
import os
from skimage.metrics import structural_similarity as ssim
from modules.mcf_pillow import greyshade_array
from static_data import (
    PATH,
    GREYSHADE

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
    def get_recognized_characters(cls, team_color):

        characters = []

        main_images = [os.path.join('.', 
                                'images_lib', 
                                'chars', 
                                team_color, 
                                f'char_{i}.png') for i in range(5)] # Путь к основному изображению (35x35)
        
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
    @classmethod
    def get_compare(cls, cut_image, type, position, team=None):

        match type, position, team:
            case 'tw_access', pos, None:
                main_image_arr = np.array(Image.open(os.path.join('.', 'ssim_score_data', 'tw_health', 'access.png')))
                similarity_index = ssim(main_image_arr, cut_image)
                if similarity_index > 0.75:
                    return True
                else:
                    return False
            case 'thp', pos, team:
                main_images = [Image.open(os.path.join('.', 'ssim_score_data', 'tw_health_n', f'{pos}', f'{i}.png')) for i in range(10)]
            case 'gold', pos, None:
                main_images = [Image.open(os.path.join('.', 'ssim_score_data', 'gold', f'{i}.png')) for i in range(10)]
            case 'gtime', 0, None:
                main_images = [Image.open(os.path.join(PATH.GTIME_DATA, f'{position}', f'{i}.png')) for i in range(4)]
            case 'gtime', 1 | 3, None:
                main_images = [Image.open(os.path.join(PATH.GTIME_DATA, f'{position}', f'{i}.png')) for i in range(10)]
            case 'gtime', 2, None:
                main_images = [Image.open(os.path.join(PATH.GTIME_DATA, f'{position}', f'{i}.png')) for i in range(6)]
            case 'score', pos, 'blue':
                main_images = [Image.open(os.path.join(PATH.BLUE_SCORE.format(pos=pos), f'{i}.png')) for i in range(10)]
            case 'score', pos, 'red':
                main_images = [Image.open(os.path.join(PATH.RED_SCORE.format(pos=pos), f'{i}.png')) for i in range(10)]
            case 'towers', pos, 'blue':
                main_images = [Image.open(os.path.join(PATH.BLUE_TOWER, f'{i}.png')) for i in range(5)]
            case 'towers', pos, 'red':
                main_images = [Image.open(os.path.join(PATH.RED_TOWER, f'{i}.png')) for i in range(5)]
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
    def towers_healh_recognition(cls, image):
        # 20, 850, 59, 902
        if not cls.get_compare(np.array(image.crop((20, 850, 59, 902)).convert('L')), 'tw_access', 0):
            return False


        t1_health = [
            cls.get_compare(np.array(image.crop((104, 857, 108, 864)).convert('L')), 'thp', 0),
            cls.get_compare(np.array(image.crop((110, 857, 114, 864)).convert('L')), 'thp', 1),
            cls.get_compare(np.array(image.crop((115, 857, 119, 864)).convert('L')), 'thp', 2)
        ]

        print(t1_health)
        

        round_value = 295
        
        if t1_health[0] == '':
            round_value = 2950
       
        t1 = ''.join([str(i) for i in t1_health])

        t1_res = int(t1) if t1 !='' else 0

        f_result = int((t1_res / round_value) * 100)
        if f_result > 100:
            return int(f_result / 10)
        return f_result

    @classmethod
    def screen_score_recognition(cls, image=None) -> dict[str, int]:

        if not image:
            image = ImageGrab.grab().crop((681, 7, 1261, 99))
        
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

        blue_gold = [
            cls.get_compare(np.array(image.crop((126, 12, 134, 28)).convert('L')), 'gold', 0),
            cls.get_compare(np.array(image.crop((136, 12, 144, 28)).convert('L')), 'gold', 1),
            cls.get_compare(np.array(image.crop((151, 12, 159, 28)).convert('L')), 'gold', 2),
        ]
        red_gold = [
            cls.get_compare(np.array(image.crop((430, 12, 438, 28)).convert('L')), 'gold', 0),
            cls.get_compare(np.array(image.crop((440, 12, 448, 28)).convert('L')), 'gold', 1),
            cls.get_compare(np.array(image.crop((455, 12, 463, 28)).convert('L')), 'gold', 2),
        ]

        blue_towers = cls.get_compare(np.array(image.crop((60, 13, 75, 29)).convert('L')), 'towers', 0, 'blue')
        red_towers = cls.get_compare(np.array(image.crop((498, 13, 514, 29)).convert('L')), 'towers', 0, 'red')

        blue_golds = ''.join([str(i) for i in blue_gold[0:2]]) + '.' + str(blue_gold[2]) if '' not in blue_gold else "10.0"
        red_golds = ''.join([str(i) for i in red_gold[0:2]]) + '.' + str(red_gold[2]) if '' not in red_gold else "10.0"

        str_final_time = f'{final_time[0]}{final_time[1]}:{final_time[2]}{final_time[3]}' # XX:XX
        minutes, seconds = map(int, str_final_time.split(':'))
        blue_kills = ''.join([str(i) for i in blue_score])
        red_kills = ''.join([str(i) for i in red_score])


        total_seconds = minutes * 60 + seconds

        if blue_score[0] == 0:
            blue_score.remove(0)
        
        gamedata = {
            'time': int(total_seconds),
            'blue_kills': int(blue_kills) if blue_kills !='' else 0,
            'red_kills': int(red_kills) if red_kills !='' else 0,
            'blue_towers': int(blue_towers) if blue_towers != '' else 0,
            'red_towers': int(red_towers) if red_towers != '' else 0,
            'blue_gold': float(blue_golds),
            'red_gold': float(red_golds),
            'is_active': 1
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