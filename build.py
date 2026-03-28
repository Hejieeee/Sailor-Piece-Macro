import PyInstaller.__main__
import os

PyInstaller.__main__.run([
    'macro.py',
    '--onefile',
    '--windowed',
    '--name=SailorPieceMacro',
    '--icon=NONE',
    '--add-data', f'{os.path.dirname(__import__("customtkinter").__file__)};customtkinter/',
    '--hidden-import=pynput.keyboard._win32',
    '--hidden-import=pynput.mouse._win32',
    '--hidden-import=keyboard'
])