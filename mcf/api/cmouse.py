import ctypes
from time import sleep
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Controller as KeyboardController



# Определяем константы для мыши
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_ABSOLUTE = 0x8000

# Получаем доступ к user32.dll
user32 = ctypes.WinDLL('user32', use_last_error=True)

mouse = MouseController()
keyboard = KeyboardController()

def double_click_left(x, y):
    click_left(x, y)
    sleep(0.1)
    click_left(x, y)

def forward_game():
    double_click_left(x=658, y=828) # flash foward game

def open_score_tab():
    sleep(1)
    click_left(x=271, y=1054)
    click_left(x=271, y=1054)
    sleep(0.25)
    click_left(x=328, y=972)

def click_left(x, y):
    
    mouse.position = (x, y)
    mouse.click(Button.left)
    sleep(0.05)

def click_on_tower(coords: tuple[int]):
    
    """
        Функция принимает 4 координаты в кортеже
            x - башня на миникарте по X
            y - башня на миникарте по Y
            x1 - клик на башню по X
            y2 = клик на башню по Y
        
    """
    
    x, y, x1, y1 = coords
    
    click_left(x, y)
    click_left(x1, y1)
    sleep(0.05)