import socket, json, time, threading, requests

NAMING_SERVER = ("127.0.0.1", 5000)
SERVICE_NAME = "temperature_service"
SERVICE_PORT = 6000
CITY = "Yogyakarta"

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

def get_real_temperature():
    url = f"https://wttr.in/{CITY}?format=j1"
    data = requests.get(url, timeout=5).json()
    return data["current_condition"][0]["temp_C"]

def register():
    ip = get_local_ip()
    s = socket.socket()
    s.connect(NAMING_SERVER)
    s.send(json.dumps({
        "type": "register",
        "name": SERVICE_NAME,
        "ip": ip,
        "port": SERVICE_PORT
    }).encode())
    s.close()
    print(f"[REGISTER] {SERVICE_NAME} ({ip}:{SERVICE_PORT})")

def heartbeat():
    while True:
        s = socket.socket()
        s.connect(NAMING_SERVER)
        s.send(json.dumps({
            "type": "heartbeat",
            "name": SERVICE_NAME
        }).encode())
        s.close()
        time.sleep(5)

def server():
    s = socket.socket()
    s.bind(("0.0.0.0", SERVICE_PORT))
    s.listen()
    print("Temperature Service running...")

    while True:
        conn, addr = s.accept()
        print(f"[CLIENT REQUEST] from {addr[0]}")

        temp = get_real_temperature()
        conn.send(f"Temperature: {temp} °C".encode())
        conn.close()


register()
threading.Thread(target=heartbeat, daemon=True).start()
server()
