import PyInstaller.__main__
import os

print("Starting the build process...")

# This runs PyInstaller exactly as if you typed it in the terminal
PyInstaller.__main__.run([
    'macro.py',       # Your main script file
    '--onefile',          # Bundle into a single .exe
    '--noconsole',        # Hide the terminal window
    '--clean'             # Clean the cache before building
])

print("\nBuild complete! Check the 'dist' folder for your application.")