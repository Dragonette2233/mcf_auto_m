@echo off
setlocal enabledelayedexpansion

call .env\Scripts\activate.bat
set BOT_TOKEN=6587599071:AAF_Wb0gAO7Zw_pS5hANgUfOBnVAR_mH60A
set CHAT_ID=-1002035939659
set RIOT_API=RGAPI-d5b7444d-ef2e-4594-aa87-4da267f6c17c
py testfield.py
