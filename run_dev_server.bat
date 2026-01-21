@echo off
REM Quick script to run the development server
echo Starting Django development server...
echo.
echo Make sure you are on the development branch!
echo.
cd /d "%~dp0"
call venv\Scripts\activate.bat
python manage.py runserver
pause
