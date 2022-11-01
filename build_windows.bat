:: Install dependencies for python
py -3 -m pip install -r requirements.txt

:: Build EXE wrapper
py -3 -m PyInstaller %~dp0app\tk_app.py --clean -F --specpath %~dp0\build --log-level ERROR --paths %~dp0app ^
--add-data "%~dp0\app;app" --windowed