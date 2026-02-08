from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import socket
import psutil
import os
import redis
import requests  # Жаңа кітапхана

app = FastAPI()

# Айнымалыларды оқып аламыз
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Redis қосу
r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Хабарлама жіберетін функция
def send_telegram_alert(message):
    # Терминалға жазамыз: "Жіберіп жатырмын..."
    print(f"🚀 ATTEMPTING TO SEND ALERT: {message}")
    
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        try:
            response = requests.post(url, data=data, timeout=5)
            # Telegram жауабын шығарамыз
            print(f"✅ Telegram Response: {response.status_code} - {response.text}")
        except Exception as e:
            # Қате болса, оны көрсетеміз
            print(f"❌ Telegram Error: {e}")
    else:
        print("⚠️ Token or Chat ID missing in code!")
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
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
    # Деректерді жинау
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

    # --- ТЕКСЕРУ ЖӘНЕ ДАБЫЛ ҚАҒУ ---
    # Егер CPU 80%-дан асса (тексеру үшін 10% қойсаң да болады)
    if cpu > 50: 
        send_telegram_alert(f"🚨 ALERT! High CPU Usage: {cpu}% on Server")

    if ram > 80:
        send_telegram_alert(f"⚠️ Warning! RAM is getting full: {ram}%")
    # -------------------------------

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