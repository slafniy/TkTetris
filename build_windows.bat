:: Install dependencies for python
pip install -r requirements.txt

:: Build EXE wrapper
pyinstaller %~dp0tk_tetris.py --clean -F --specpath %~dp0\build --log-level ERROR --paths %~dp0\src ^
--add-data "%~dp0\res;res" --windowed