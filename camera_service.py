import socket, json, time, threading

NAMING_SERVER = ("127.0.0.1", 5000)
SERVICE_NAME = "camera_service"
SERVICE_PORT = 6002

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

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
    print("Camera Service running...")

    while True:
        conn, addr = s.accept()
        print(f"[CLIENT REQUEST] from {addr[0]}")
        conn.send(b"Camera Snapshot Taken")
        conn.close()

register()
threading.Thread(target=heartbeat, daemon=True).start()
server()
