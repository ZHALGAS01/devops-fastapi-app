from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import socket
import psutil
import os
import redis
import requests
import time  # <--- Жаңа кітапхана: Уақытты санау үшін

app = FastAPI()

# Айнымалыларды оқып аламыз
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Redis қосу
try:
    r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
except:
    r = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# --- 🧠 БОТТЫҢ ЕСТЕЛІГІ (ЖАҢА) ---
last_alert_time = 0   # Соңғы хабарлама жіберген уақыт
ALERT_COOLDOWN = 60   # Қанша секунд үзіліс алу керек (1 минут)

def send_telegram_alert(message):
    global last_alert_time  # Ғаламдық айнымалыны қолданамыз
    
    current_time = time.time()
    
    # Егер соңғы хабарламадан бері 60 секунд өтпесе -> Жібермейміз!
    if (current_time - last_alert_time) < ALERT_COOLDOWN:
        print(f"⏳ Cooling down... Skipping alert. (Wait {int(ALERT_COOLDOWN - (current_time - last_alert_time))}s)")
        return  # Функция осы жерден тоқтайды

    # Егер уақыт өтіп кетсе -> Жібереміз
    print(f"🚀 SENDING ALERT: {message}")
    
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        try:
            requests.post(url, data=data, timeout=5)
            # Уақытты жаңартамыз: "Мен дәл қазір жібердім"
            last_alert_time = current_time 
        except Exception as e:
            print(f"❌ Telegram Error: {e}")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    hits = "Error"
    if r:
        try:
            hits = r.incr('page_views')
        except:
            hits = "Redis Error"
        
    return templates.TemplateResponse("index.html", {
        "request": request,
        "hostname": socket.gethostname(),
        "hits": hits
    })

@app.get("/api/stats")
async def get_stats():
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    cpu_cores = psutil.cpu_percent(interval=None, percpu=True)
    
    net = psutil.net_io_counters()
    sent_mb = round(net.bytes_sent / (1024 * 1024), 2)
    recv_mb = round(net.bytes_recv / (1024 * 1024), 2)
    
    connections = psutil.net_connections()
    active_conns = len([c for c in connections if c.status == 'ESTABLISHED'])
    listening_ports = [c.laddr.port for c in connections if c.status == 'LISTEN']

    # Логика: Егер CPU 50%-дан асса
    if cpu > 50: 
        send_telegram_alert(f"🚨 ALERT! High CPU Usage: {cpu}% on Server")

    return {
        "cpu": cpu,
        "ram": ram,
        "disk": disk,
        "net_sent": sent_mb,
        "net_recv": recv_mb,
        "cores": cpu_cores,
        "active_conns": active_conns,
        "open_ports": listening_ports[:5]
    }