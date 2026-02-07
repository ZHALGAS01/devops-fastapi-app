@app.get("/api/stats")
async def get_stats():
    # 1. CPU & RAM
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    
    # 2. Disk Usage (C: немесе /)
    disk = psutil.disk_usage('/').percent
    
    # 3. Network (Байтпен келеді, оны МБ-қа айналдырамыз)
    net = psutil.net_io_counters()
    sent_mb = round(net.bytes_sent / (1024 * 1024), 2) # Жіберілген (Upload)
    recv_mb = round(net.bytes_recv / (1024 * 1024), 2) # Қабылданған (Download)

    return {
        "cpu": cpu, 
        "ram": ram, 
        "disk": disk,
        "net_sent": sent_mb,
        "net_recv": recv_mb
    }