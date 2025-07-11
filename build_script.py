import subprocess
import os
import shutil
import sys
import time
import ctypes
import win32gui
import win32con
import win32process
import threading

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

def animate_progress(stop_event, description):
    animation = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    idx = 0
    while not stop_event.is_set():
        text = f"\r\033[96m{animation[idx]}\033[0m {description}"
        sys.stdout.write(text)
        sys.stdout.flush()
        idx = (idx + 1) % len(animation)
        time.sleep(0.1)
    sys.stdout.write("\r" + " " * (len(description) + 2) + "\r")
    sys.stdout.flush()

def show_progress(description, duration):
    stop_event = threading.Event()
    progress_thread = threading.Thread(target=animate_progress, args=(stop_event, description))
    progress_thread.start()
    time.sleep(duration)
    stop_event.set()
    progress_thread.join()
    print(f"\033[92m✓\033[0m {description}")

def get_user_input():
    """Get Telegram token and user ID from user input"""
    print("\n\033[96m╔════════════════════════════════════════╗")
    print("║         Bot Configuration Setup        ║")
    print("╚════════════════════════════════════════╝\033[0m\n")
    
    # Get Telegram Bot Token
    print("\033[93m1. Get your Telegram Bot Token:\033[0m")
    print("   • Open Telegram and search for @BotFather")
    print("   • Send /newbot and follow instructions")
    print("   • Copy the token (looks like: 123456789:ABC-DEF1234ghIkl-zyx57W2v1u123ew11)\n")
    
    while True:
        token = input("\033[96mEnter your Telegram Bot Token: \033[0m").strip()
        if token and ":" in token and len(token.split(":")[0]) >= 8:
            break
        print("\033[91m❌ Invalid token format! Please try again.\033[0m")
    
    # Get Authorized User ID
    print("\n\033[93m2. Get your Telegram User ID:\033[0m")
    print("   • Open Telegram and search for @userinfobot")
    print("   • Send /start to get your User ID")
    print("   • Copy the number (looks like: 123456789)\n")
    
    while True:
        try:
            user_id = input("\033[96mEnter your Telegram User ID: \033[0m").strip()
            user_id = int(user_id)
            if user_id > 0:
                break
            else:
                print("\033[91m❌ User ID must be a positive number!\033[0m")
        except ValueError:
            print("\033[91m❌ Invalid User ID! Please enter numbers only.\033[0m")
    
    return token, user_id

def create_env_file(token, user_id):
    """Create .env file with the provided credentials"""
    env_content = f"""# Telegram Bot Configuration
TELEGRAM_TOKEN={token}
AUTHORIZED_USER_ID={user_id}
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("\n\033[92m✓ .env file created successfully!\033[0m")
        return True
    except Exception as e:
        print(f"\n\033[91m❌ Failed to create .env file: {str(e)}\033[0m")
        return False

def build():
    try:
        # If not running in show-console mode, start new process
        if "--show-console" not in sys.argv:
            return run_in_new_console()

        # Clear screen
        os.system('cls')
        
        # Get user credentials first
        token, user_id = get_user_input()
        
        # Create .env file
        if not create_env_file(token, user_id):
            print("\n\033[91m❌ Failed to create configuration file!\033[0m")
            time.sleep(10)
            return False

        # Updated console banner with version
        print("\n\033[96m╔═══════════════════════════════════════════╗")
        print("║         Building Telegram Bot             ║")
        print("║              Version 1.2 beta             ║")
        print("╚═══════════════════════════════════════════╝\033[0m")
        print("\n")


        # Animated build steps
        show_progress("Initializing build environment", 2)
        show_progress("Cleaning old files", 1.5)
        show_progress("Compiling source code", 3)


         # Luffy ASCII art in cyan first
        print("\033[96m")
        print("⠀⠀⠀⣠⠞⢠⠖⠉⠉⠉⢭⣭⣀⡉⣍⠉⠉⠒⠭⣑⠤⡀⠀⠀⠀⠀")
        print("⠀⠀⡞⠁⡰⠳⢦⣼⣿⡿⣿⣿⣿⣿⣿⣶⣤⡀⠈⠓⣌⢢⡀⠀⠀")
        print("⠀⣸⠁⣰⣵⣾⣿⣿⡿⠹⣿⣿⢿⣟⣿⣿⣿⣿⣦⡀⠈⢣⠱⡀⠀")
        print("⠀⢯⢠⣿⠟⣿⣿⣿⡇⠀⣿⠛⣷⢙⣻⢌⣻⠟⣿⣿⣿⣆⠀⢧⢳⠀")
        print("⠀⠘⡞⢡⣼⣿⣿⣯⣧⠀⠘⠆⢨⠋⢠⡤⢘⣆⢻⣿⣿⣿⠇⢸⠀⡇")
        print("⠀⠀⢱⡼⢟⣿⣿⣿⠋⢑⣄⠀⠈⠢⠤⠔⣺⣏⠀⣿⣿⡏⠀⡼⠀⡇")
        print("⠀⠀⠁⠘⢺⣿⣿⣿⣦⣈⣽⠀⠀⢀⡤⠊⢡⣾⠀⠸⣿⢃⡴⠁⡜⠁")
        print("⠀⠀⠀⠀⠀⠻⠙⠟⣿⡀⢨⠭⠊⡡⠔⠀⢠⠃⡜⣿⡋⣁⡠⠊⠀⠀")
        print("⠀⠀⠀⠀⡰⠉⢓⠀⠈⠳⢌⡳⢄⣀⠤⠒⢁⠞⡼⢹⡄⠀⠀⠀⠀⠀")
        print("⠀⠀⣀⠤⣣⣄⢸⠀⠀⠀⠀⠉⠑⠒⠤⢲⣥⠼⣤⣤⣹⡱⡀⠀⠀⠀")
        print("⣠⠊⠁⠀⠀⠈⣞⣆⠀⠀⠀⠀⠀⠀⣴⠏⠀⠀⠀⠙⢿⣿⣯⣢⠀⠀")
        print("⠄⠈⠉⠉⠙⢦⢻⠚⣄⠀⠀⠀⠀⣼⠃⠀⠀⠀⠀⠀⢸⣿⣿⣧⠓⠀\033[0m")

        
        print("\n\033[93mBuilding executable...\033[0m")
        result = subprocess.run([
            'python', '-m', 'PyInstaller',
            '--onefile',
            '--noconsole',
            'flashDVbot.py'
        ], capture_output=True, text=True)

        if result.returncode != 0:
            print("\n\033[91m✘ Build Failed!\033[0m")
            print(result.stderr)
            time.sleep(10)
            return False

        show_progress("Moving files to destination", 1.5)
        shutil.move('dist/flashDVbot.exe', 'TelegramBot.exe')

        show_progress("Cleaning up build artifacts", 2)
        for d in ['build', 'dist']:
            shutil.rmtree(d, ignore_errors=True)
        if os.path.exists('flashDVbot.spec'):
            os.remove('flashDVbot.spec')

        print("\n\033[92m╔════════════════════════════╗")
        print("║       Build Completed       ║")
        print("╚════════════════════════════╝\033[0m")
        
        print("\n\033[94mMade with ❤️ by flash\033[0m")
        print("\nClosing in 10 seconds...")
        time.sleep(10)
        return True

    except Exception as e:
        print(f"\n\033[91m✘ Build Failed: {str(e)}\033[0m")
        time.sleep(10)
        return False

if __name__ == "__main__":
    build()
