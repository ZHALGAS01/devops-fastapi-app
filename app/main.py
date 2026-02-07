from fastapi import FastAPI
import socket

app = FastAPI()

@app.get("/")
def read_root():
    # Показываем ID контейнера (hostname), чтобы видеть балансировку в будущем
    return {
        "message": "Hello from Docker!", 
        "hostname": socket.gethostname(),
        "status": "success"
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}