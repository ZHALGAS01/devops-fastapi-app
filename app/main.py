from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import socket
import psutil
import os
import redis # Redis кітапханасы

app = FastAPI()

# Redis-пен байланыс орнатамыз
# "redis" деген сөз - docker-compose ішіндегі сервистің аты
r = redis.Redis(host='redis', port=6379, decode_responses=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Әр кірген сайын санды 1-ге көбейтеміз
    hits = r.incr('page_views')
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "hostname": socket.gethostname(),
        "hits": hits # HTML-ге жібереміз
    })

@app.get("/api/stats")
async def get_stats():
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    net = psutil.net_io_counters()
    sent_mb = round(net.bytes_sent / (1024 * 1024), 2)
    recv_mb = round(net.bytes_recv / (1024 * 1024), 2)

    return {
        "cpu": cpu, "ram": ram, "disk": disk,
        "net_sent": sent_mb, "net_recv": recv_mb
    }