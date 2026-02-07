from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import socket
import psutil
import os

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
    cpu_usage = psutil.cpu_percent(interval=None)
    ram_usage = psutil.virtual_memory().percent
    return {"cpu": cpu_usage, "ram": ram_usage}

# Force update 1