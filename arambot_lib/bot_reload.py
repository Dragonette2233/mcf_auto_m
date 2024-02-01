def close_mcf_and_chrome():
    import pygetwindow as gw
    import os
    # Указать заголовок окна, которое вы хотите закрыть
    wins_to_close = [
        'MCF_dev',
        'mcf_development',
        'Ставки на спорт',
        'Матчи онлайн',
        'C:\Windows'
        # 'C:\\Windows\\System32\\cmd.exe'
    ]

    # Получение списка всех активных окон
    active_windows = gw.getAllTitles()

    # Вывод списка активных окон
    for window_title in active_windows:
        for w in wins_to_close:
            if str(window_title).startswith(w):
                gw.getWindowsWithTitle(window_title)[0].close()

def status_mcf():
    from PIL import ImageGrab
    import os

    status_path = os.path.join('.', 'arambot_lib', 'mcf_status.png')
    screen = ImageGrab.grab()
    screen.save(status_path)
    return status_path

def start_mcf():
    import os
    import ctypes

    mcf_root_path = os.environ.get('MCF_ROOT')
    bat_file_path = os.path.join(mcf_root_path, 'MCF_dev.bat')

    # Функция для запуска файла в свернутом режиме
    SW_SHOWMINIMIZED = 2
    try:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", bat_file_path, None, None, SW_SHOWMINIMIZED)
        print(f"Файл {mcf_root_path} успешно запущен в свернутом режиме.")
    except Exception as e:
        print(f"Произошла ошибка при запуске {bat_file_path} в свернутом режиме: {e}")
    # Запуск файла в свернутом режиме
    # start_minimized(bat_file_path)




            

