:: Install dependencies for python
py -3 -m pip install -r requirements.txt

:: Build EXE wrapper
py -3 -m PyInstaller %~dp0tk_tetris.py --clean -F --specpath %~dp0\build --log-level ERROR --paths %~dp0\src ^
--add-data "%~dp0\res;res" --windowed