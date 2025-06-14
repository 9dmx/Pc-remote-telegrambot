import subprocess
import os
import shutil
import sys
import time
import ctypes
import win32gui
import win32con
import win32process

def run_in_new_console():
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags = subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = win32con.SW_SHOW

    # Launch build process in new visible console
    process = subprocess.Popen(
        [sys.executable, __file__, "--show-console"],
        creationflags=subprocess.CREATE_NEW_CONSOLE,
        startupinfo=startupinfo
    )
    return process.wait()

def build():
    try:
        # If not running in show-console mode, start new process
        if "--show-console" not in sys.argv:
            return run_in_new_console()

        # Clear screen
        os.system('cls')
        
        # Updated console banner with version
        print("\033[96m")  # Cyan color
        print("╔══════════════════════════════════════╗")
        print("║         Building Telegram Bot        ║")
        print("║            Version 1.0               ║")
        print("╚══════════════════════════════════════╝\033[0m")
        
        # Build steps with progress
        print("\n\033[93m[1/4]\033[0m Cleaning old files...")
        time.sleep(1)
        
        print("\033[93m[2/4]\033[0m Building executable...")
        result = subprocess.run([
            'python', '-m', 'PyInstaller',
            '--onefile',
            '--noconsole',
            '--icon=icon/icon.ico',  # Updated icon path
            'flashDVbot.py'
        ], capture_output=True, text=True)

        if result.returncode != 0:
            print("\n\033[91mBuild Failed!\033[0m")
            print(result.stderr)
            time.sleep(10)
            return False

        print("\033[93m[3/4]\033[0m Moving files...")
        shutil.move('dist/flashDVbot.exe', 'TelegramBot.exe')

        print("\033[93m[4/4]\033[0m Cleaning up...")
        for d in ['build', 'dist']:
            shutil.rmtree(d, ignore_errors=True)
        if os.path.exists('flashDVbot.spec'):
            os.remove('flashDVbot.spec')

        print("\n\033[92m✓ Build completed successfully!\033[0m")
        
        # Luffy ASCII art in cyan
        print("\n\033[96m")  # Cyan color
        print("⠀⠀⠀⣠⠞⢠⠖⠉⠉⠉⢭⣭⣀⡉⣍⠉⠉⠒⠭⣑⠤⡀⠀⠀⠀⠀")
        print("⠀⠀⡞⠁⡰⠳⢦⣼⣿⡿⣿⣿⣿⣿⣿⣿⣶⣤⡀⠈⠓⣌⢢⡀⠀⠀")
        print("⠀⣸⠁⣰⣵⣾⣿⣿⡿⠹⣿⣿⢿⣟⣿⣿⣿⣿⣿⣦⡀⠈⢣⠱⡀⠀")
        print("⠀⢯⢠⣿⠟⣿⣿⣿⡇⠀⣿⠛⣷⢙⣻⢌⣻⠟⣿⣿⣿⣆⠀⢧⢳⠀")
        print("⠀⠘⡞⢡⣼⣿⣿⣯⣧⠀⠘⠆⢨⠋⢠⡤⢘⣆⢻⣿⣿⣿⠇⢸⠀⡇")
        print("⠀⠀⢱⡼⢟⣿⣿⣿⠋⢑⣄⠀⠈⠢⠤⠔⣺⣏⠀⣿⣿⡏⠀⡼⠀⡇")
        print("⠀⠀⠁⠘⢺⣿⣿⣿⣦⣈⣽⠀⠀⢀⡤⠊⢡⣾⠀⠸⣿⢃⡴⠁⡜⠁")
        print("⠀⠀⠀⠀⠀⠻⠙⠟⣿⡀⢨⠭⠊⡡⠔⠀⢠⠃⡜⣿⡋⣁⡠⠊⠀⠀")
        print("⠀⠀⠀⠀⡰⠉⢓⠀⠈⠳⢌⡳⢄⣀⠤⠒⢁⠞⡼⢹⡄⠀⠀⠀⠀⠀")
        print("⠀⠀⣀⠤⣣⣄⢸⠀⠀⠀⠀⠉⠑⠒⠤⢲⣥⠼⣤⣤⣹⡱⡀⠀⠀⠀")
        print("⣠⠊⠁⠀⠀⠈⣞⣆⠀⠀⠀⠀⠀⠀⣴⠏⠀⠀⠀⠙⢿⣿⣯⣢⠀⠀")
        print("⠄⠈⠉⠉⠙⢦⢻⠚⣄⠀⠀⠀⠀⣼⠃⠀⠀⠀⠀⠀⢸⣿⣿⣧⠓⠀\033[0m")
        
        print("\n\033[94mMade with ❤️ by Flash\033[0m")
        print("\nClosing in 10 seconds...")
        time.sleep(10)
        return True

    except Exception as e:
        print(f"\n\033[91mBuild Failed: {str(e)}\033[0m")
        time.sleep(10)
        return False

if __name__ == "__main__":
    build()
