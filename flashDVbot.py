import os
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
    await update.message.reply_text("Bot is running! Here are the available commands:\n" + HELP_MESSAGE)

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
        
        msg = ("📱 Running Applications:\n"
               "➖➖➖➖➖➖➖➖\n")
        for i, proc in enumerate(processes[:10], 1):
            msg += f"{i}. {proc['name']}\n"
            msg += f"   CPU: {proc['cpu_percent']}% | RAM: {proc['memory_percent']:.1f}%\n"
        
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
