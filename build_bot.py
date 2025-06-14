import os
import subprocess
import shutil
from tkinter import messagebox

def build_exe():
    try:
        # PyInstaller command with hidden window
        cmd = [
            'pyinstaller',
            '--noconfirm',
            '--onefile',
            '--windowed',  # This hides the console window
            '--icon=bot.ico',  # Optional: Add your icon here
            '--name=TelegramBot',
            '--add-data=.env;.',  # Include .env file
            'flashDVbot.py'
        ]
        
        subprocess.run(cmd, check=True)
        
        # Move the executable to current directory
        shutil.move(os.path.join('dist', 'TelegramBot.exe'), 'TelegramBot.exe')
        
        # Cleanup build files
        for dir_name in ['build', 'dist', '__pycache__']:
            if os.path.exists(dir_name):
                shutil.rmtree(dir_name)
        if os.path.exists('TelegramBot.spec'):
            os.remove('TelegramBot.spec')
            
        return True
    except Exception as e:
        print(f"Build error: {str(e)}")
        return False
