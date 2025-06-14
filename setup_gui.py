import tkinter as tk
from tkinter import ttk
import os
import subprocess
import shutil
import time
from dotenv import load_dotenv
import sys
from build_script import build

BOT_TEMPLATE = '''import os
import sys
import platform
import psutil
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
from colorama import init, Fore, Style
from PIL import ImageGrab, Image
import pygetwindow as gw
import mss
import mss.tools

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
🤖 Available Commands:
➖➖➖➖➖➖➖➖
/start - Start the bot
/help - Show this help message
/status - Check PC status & resources
/apps - List running applications
/screenshot - Take a screenshot
/shutdown - Turn off the PC
"""

async def shutdown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_user.id == AUTHORIZED_USER_ID:
            await update.message.reply_text("Shutting down the system...")
            os.system("shutdown /s /t 0")
        else:
            await update.message.reply_text("❌ Not authorized.")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is running! Here are the available commands:\\n" + HELP_MESSAGE)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_MESSAGE)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_user.id != AUTHORIZED_USER_ID:
            await update.message.reply_text("❌ Not authorized.")
            return
            
        # Get system info
        boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        cpu_usage = psutil.cpu_percent()
        ram = psutil.virtual_memory()
        ram_used = f"{ram.used / (1024 * 1024 * 1024):.1f}GB"
        ram_total = f"{ram.total / (1024 * 1024 * 1024):.1f}GB"
        
        # Check battery status safely
        battery = psutil.sensors_battery()
        power_status = "Connected" if battery and battery.power_plugged else "On Battery" if battery else "No Battery"
        
        status_msg = f"""
🖥️ PC Status:
➖➖➖➖➖➖➖➖
✅ System: {platform.system()} {platform.release()}
⏰ Uptime since: {boot_time}
💻 CPU Usage: {cpu_usage}%
💾 RAM: {ram_used}/{ram_total} ({ram.percent}%)
🔋 Power: {power_status}
🟢 Ready for shutdown
"""
        await update.message.reply_text(status_msg)
    except Exception as e:
        await update.message.reply_text(f"Error getting status: {str(e)}")

async def apps_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
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
        
        msg = ("📱 Running Applications:\\n"
               "➖➖➖➖➖➖➖➖\\n")
        for i, proc in enumerate(processes[:10], 1):
            msg += f"{i}. {proc['name']}\\n"
            msg += f"   CPU: {proc['cpu_percent']}% | RAM: {proc['memory_percent']:.1f}%\\n"
        
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"Error listing apps: {str(e)}")

async def screenshot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
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

def main():
    try:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("shutdown", shutdown_command))
        app.add_handler(CommandHandler("status", status_command))
        app.add_handler(CommandHandler("apps", apps_command))
        app.add_handler(CommandHandler("screenshot", screenshot_command))
        print("Bot starting...")
        app.run_polling()
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    main()
'''

class CustomButton(ttk.Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure(style=kwargs.get('style', 'Custom.TButton'))

class SetupGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Flash Telegram Bot v1.0")
        self.root.geometry("500x280")
        self.root.minsize(400, 250)  # Set minimum size
        
        # Center window on screen
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - 500) // 2
        y = (screen_height - 280) // 2
        self.root.geometry(f"+{x}+{y}")

        # Configure grid weights for resizing
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Modern dark theme
        self.root.configure(bg='#1e1e1e')  # Darker background
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Custom.TEntry", 
                       fieldbackground="#2d2d2d",
                       foreground="white",
                       padding=8)
        style.configure("TLabel", 
                       background="#1e1e1e",
                       foreground="white")
        style.configure("TFrame", 
                       background="#1e1e1e")
        
        # Override button styles completely
        style.configure("Build.TButton",
            background="#007acc",
            foreground="white",
            relief="raised",
            font=('Segoe UI', 11, 'bold'))
        
        style.configure("Cancel.TButton",
            background="#666666",
            foreground="white",
            relief="raised",
            font=('Segoe UI', 11))

        style.map('Build.TButton',
            background=[('active', '#005999')],
            relief=[('pressed', 'sunken')])
        
        style.map('Cancel.TButton',
            background=[('active', '#444444')],
            relief=[('pressed', 'sunken')])

        # Create main frame
        main_frame = ttk.Frame(root, padding="20", style="TFrame")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Title with version (centered)
        title = ttk.Label(main_frame, 
                         text="🤖 Flash Telegram Bot",
                         font=('Segoe UI', 18, 'bold'),
                         style="TLabel")
        title.grid(row=0, column=0, pady=(0, 5))
        
        version = ttk.Label(main_frame,
                          text="Version 1.0",
                          font=('Segoe UI', 9),
                          foreground="#888888",
                          style="TLabel")
        version.grid(row=1, column=0, pady=(0, 20))
        
        # Input fields frame
        input_frame = ttk.Frame(main_frame, style="TFrame")
        input_frame.grid(row=2, column=0, sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)
        
        ttk.Label(input_frame, text="Bot Token:", style="TLabel", font=('Segoe UI', 10)).grid(row=0, column=0, sticky="w")
        self.token_entry = ttk.Entry(input_frame, style="Custom.TEntry")
        self.token_entry.grid(row=1, column=0, sticky="ew", pady=(2, 10))
        
        ttk.Label(input_frame, text="User ID:", style="TLabel", font=('Segoe UI', 10)).grid(row=2, column=0, sticky="w")
        self.user_id_entry = ttk.Entry(input_frame, style="Custom.TEntry")
        self.user_id_entry.grid(row=3, column=0, sticky="ew", pady=2)
        
        # Buttons frame
        btn_frame = ttk.Frame(main_frame, style="TFrame")
        btn_frame.grid(row=3, column=0, pady=20)
        
        CustomButton(btn_frame,
                  text="🚀 Build Bot",
                  width=15,
                  style="Build.TButton",
                  command=self.build_bot).pack(side=tk.LEFT, padx=10)
        
        CustomButton(btn_frame,
                  text="❌ Cancel",
                  width=15,
                  style="Cancel.TButton", 
                  command=root.quit).pack(side=tk.LEFT, padx=10)
        
        # Signature at bottom
        signature = ttk.Label(main_frame,
                            text="Made with ❤️ by Flash",
                            font=('Segoe UI', 8),
                            foreground="#888888",
                            style="TLabel")
        signature.grid(row=4, column=0, sticky="s", pady=10)
        
        self.load_existing_values()

    def load_existing_values(self):
        load_dotenv()
        if os.getenv('TELEGRAM_TOKEN'):
            self.token_entry.insert(0, os.getenv('TELEGRAM_TOKEN'))
        if os.getenv('AUTHORIZED_USER_ID'):
            self.user_id_entry.insert(0, os.getenv('AUTHORIZED_USER_ID'))

    def build_bot(self):
        token = self.token_entry.get().strip()
        user_id = self.user_id_entry.get().strip()
        
        if not token or not user_id:
            print("\033[91mError: Both fields are required!\033[0m")
            return
            
        try:
            # Save credentials with UTF-8 encoding
            with open('.env', 'w', encoding='utf-8') as f:
                f.write(f'TELEGRAM_TOKEN={token}\n')
                f.write(f'AUTHORIZED_USER_ID={user_id}\n')
            
            # Generate bot file with UTF-8 encoding
            with open('flashDVbot.py', 'w', encoding='utf-8') as f:
                f.write(BOT_TEMPLATE)
            
            # Build executable
            self.build_exe()
                
        except Exception as e:
            print(f"\033[91mBuild error: {str(e)}\033[0m")

    def build_exe(self):
        try:
            return build()
        except Exception as e:
            print(f"\033[91mBuild error: {str(e)}\033[0m")
            return False

if __name__ == "__main__":
    root = tk.Tk()
    app = SetupGUI(root)
    root.mainloop()