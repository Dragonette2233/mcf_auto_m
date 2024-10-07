# Импортируем виртуальные коды клавиш из модуля win32con
import win32con
import win32api
import win32gui
from time import sleep

class KController:
    def __init__(self, hwnd=0) -> None:
        # Словарь для специальных клавиш
        self.hwnd = hwnd
        self.SPECIAL_KEYS = {
            'ctrl': win32con.VK_CONTROL,
            'alt': win32con.VK_MENU,
            'shift': win32con.VK_SHIFT,
            'enter': win32con.VK_RETURN,
            'esc': win32con.VK_ESCAPE,
            'tab': win32con.VK_TAB,
            'space': win32con.VK_SPACE,
            '[': 0xDB,  # Клавиша '['
            ']': 0xDD,  # Клавиша ']'
            '.': 0xBE,  # Клавиша '.'
            ',': 0xBC,  # Клавиша ','
            '/': 0xBF,  # Клавиша '/'
        }
        self.KEY = self.symbol_to_keycode
    
    def init_league_hwnd(self, hwnd):
        while True:
            self.hwnd = win32gui.FindWindow(None, "League of Legends (TM) Client")
            if self.hwnd != 0:
                print("League win located!")
                break
            sleep(1)
    
    def symbol_to_keycode(self, symbol: str):
        # Преобразуем в нижний регистр для удобства поиска
        symbol = symbol.lower()
        
        # Проверяем, является ли символ специальной клавишей
        if symbol in self.SPECIAL_KEYS:
            return self.SPECIAL_KEYS[symbol]
        
        # Если это обычная буквенно-цифровая клавиша
        if len(symbol) == 1:
            # Используем ASCII-код символа для букв и цифр
            return ord(symbol.upper())
        
        raise ValueError(f"Unknown symbol: {symbol}")

    def _press(self, symbol):
        
        hex_key = self.symbol_to_keycode(symbol)
        win32api.PostMessage(self.hwnd, win32con.WM_KEYDOWN, hex_key, 0)
        
    def _release(self, symbol):
        hex_key = self.symbol_to_keycode(symbol)
        win32api.PostMessage(self.hwnd, win32con.WM_KEYUP, hex_key, 0)
    
    def press_button(self, key: str, delay=0.09):
        # Маппинг строковых значений на объекты Key
        

        # Разделяем комбинацию на части
        keys = key.split('+')
        pressed_keys = []

        try:
            # Нажимаем модификаторы (если есть)
            for part in keys:
                part = part.lower().strip()
                
                self._press(part)
                pressed_keys.append(part)

            # Задержка после нажатия всех клавиш
            sleep(delay)
        
        finally:
            # Отпускаем все клавиши
            for k in pressed_keys:
                self._release(k)
