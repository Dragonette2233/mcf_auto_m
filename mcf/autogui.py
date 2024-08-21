import pyautogui
import time

def _click():
    pyautogui.mouseDown()   # Нажимаем кнопку мыши
    time.sleep(0.1)         # Можно задать задержку, если нужно
    pyautogui.mouseUp()
    time.sleep(0.05)

def click(x, y):
    pyautogui.moveTo(x, y)
    _click()

def doubleClick(x, y):
    pyautogui.moveTo(x, y)
    _click()
    _click()

def close_league_stream():
    click(x=1898, y=900)
    time.sleep(0.5)
    click(x=1898, y=1058)
    time.sleep(1.5)

def open_score_tab():
    time.sleep(1)
    doubleClick(x=271, y=1054)
    time.sleep(0.25)
    click(x=328, y=972)