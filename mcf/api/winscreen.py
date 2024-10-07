import win32gui
import win32con

def make_league_foreground():
    # Получаем HWND окна по его названию или классу
    hwnd = win32gui.FindWindow(None, "League of Legends (TM)")

    # Делаем окно активным
    if hwnd:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)  # Восстанавливаем свернутое окно
        win32gui.SetForegroundWindow(hwnd)  # Устанавливаем окно как активное
    else:
        print("Окно не найдено.")
