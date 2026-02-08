from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import socket
import psutil
import os

# Ең маңызды жері осы! (Сенде осы жоқ болып тұр)
app = FastAPI()

# Папканың жолын нақты көрсетеміз
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "hostname": socket.gethostname()
    })

@app.get("/api/stats")
async def get_stats():
    # 1. CPU & RAM
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    
    # 2. Disk Usage (Disk қосамыз)
    disk = psutil.disk_usage('/').percent
    
    # 3. Network (Интернет трафигі)
    net = psutil.net_io_counters()
    sent_mb = round(net.bytes_sent / (1024 * 1024), 2)
    recv_mb = round(net.bytes_recv / (1024 * 1024), 2)

    return {
        "cpu": cpu, 
        "ram": ram, 
        "disk": disk,
        "net_sent": sent_mb,
        "net_recv": recv_mb
    }
