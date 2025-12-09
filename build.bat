@echo off

echo Installing PyInstaller...
pip install pyinstaller

echo Building executable...
pyinstaller --onefile main.py

echo Creating Textures folder in dist and copying assets...
if not exist dist\Textures mkdir dist\Textures
copy textures\ dist\Textures\
copy config.ini dist\config.ini

echo Creating ZIP archive...
powershell Compress-Archive -Path dist\main.exe, dist\Textures, dist\config.ini -DestinationPath BP-Edit.zip

echo Build and archive complete. Check BP-Edit.zip
pause
