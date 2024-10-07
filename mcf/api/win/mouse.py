import win32api, win32con, win32gui
import time

class MController():
    def __init__(self, hwnd=0) -> None:
        self.hwnd = hwnd
        self.cx = 0
        self.cy = 0
        self.hwnd = 0

    def init_league_hwnd(self):
        while True:
            self.hwnd = win32gui.FindWindow(None, "League of Legends (TM) Client")
            if self.hwnd != 0:
                print("League win located!")
                break
            time.sleep(1)

    def click(self, x, y):
        print(self.hwnd)
        lParam = win32api.MAKELONG(x, y)
        win32api.PostMessage(self.hwnd, win32con.WM_MOUSEMOVE, 0, lParam)
        win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
        # time.sleep(0.01)
        win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, lParam)
    
    def click_on_tower(self, coords: tuple[int]):
    
        """
            Функция принимает 4 координаты в кортеже
                x - башня на миникарте по X
                y - башня на миникарте по Y
                x1 - клик на башню по X
                y2 = клик на башню по Y
            
        """
        
        x, y, x1, y1 = coords
        
        self.click(x, y)
        # time.sleep(0.05)
        self.click(x1, y1)
        time.sleep(0.05)
    
    # Функция для симуляции нажатия и отпускания кнопки мыши
    def click_loot(self, x: int, y: int):
        lParam = win32api.MAKELONG(x, y)
        win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONDOWN, 1, lParam)
        # time.sleep(0.01)
        win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONUP, 1, lParam)
        
    def click_mouse(self, hold=False):
        lParam = win32api.MAKELONG(self.cx, self.cy)
        
        # Перемещение мыши в указанное положение
        win32api.PostMessage(self.hwnd, win32con.WM_MOUSEMOVE, 0, lParam)

        # Нажатие левой кнопки мыши
        win32api.PostMessage(self.hwnd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, lParam)
        
        if not hold:
            # Отпускание левой кнопки мыши, если не нужно удерживать
            win32api.PostMessage(self.hwnd, win32con.WM_RBUTTONUP, win32con.MK_RBUTTON, lParam)

    def move_mouse(self, rel_x):

        lParam = win32api.MAKELONG(self.cx + rel_x, self.cy)
        # Отправляем сообщение о перемещении мыши
        win32api.PostMessage(self.hwnd, win32con.WM_MOUSEMOVE, 0, lParam)

    def release_mouse(self, rel_x):
        lParam = win32api.MAKELONG(self.cx + rel_x, self.cy)
        # Отпускание левой кнопки мыши
        win32api.PostMessage(self.hwnd, win32con.WM_RBUTTONUP, win32con.MK_RBUTTON, lParam)
