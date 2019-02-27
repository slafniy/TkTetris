pyinstaller %~dp0tk_tetris.py --clean -F --specpath %~dp0\build --log-level ERROR --paths %~dp0\src ^
--add-data "%~dp0\res;res" --windowed