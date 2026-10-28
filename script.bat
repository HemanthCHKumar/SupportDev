
@echo off
cd /d "C:\Users\Hemanth\Desktop\AZURE_Automation\SupportDev"

:loop
git pull --ff-only origin main
timeout /t 10 /nobreak >nul
goto loop
