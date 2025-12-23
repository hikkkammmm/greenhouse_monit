# naming_server.py
import socket, threading, time, json

HOST = "0.0.0.0"
PORT = 6000
TTL = 20

services = {}   # service_name -> {ip, port, last_seen}
lock = threading.Lock()

def monitor():
    while True:
        time.sleep(5)
        now = time.time()
        with lock:
            for name in list(services.keys()):
                if now - services[name]["last_seen"] > TTL:
                    print(f"[TIMEOUT] {name} dihapus")
                    del services[name]

def handle(conn):
    try:
        msg = conn.recv(1024).decode()
        parts = msg.split("|")

        # HEARTBEAT|filenodeA|ip|port
        if parts[0] == "HEARTBEAT":
            name, ip, port = parts[1], parts[2], int(parts[3])
            with lock:
                services[name] = {
                    "ip": ip,
                    "port": port,
                    "last_seen": time.time()
                }
            conn.send(b"OK")

        # LOOKUP|filenodeA
        elif parts[0] == "LOOKUP":
            name = parts[1]
            if name in services:
                conn.send(json.dumps(services[name]).encode())
            else:
                conn.send(b"NOT_FOUND")

    except Exception as e:
        print("ERROR:", e)
    finally:
        conn.close()

threading.Thread(target=monitor, daemon=True).start()

s = socket.socket()
s.bind((HOST, PORT))
s.listen()
print("[NAMING SERVER] running...")

while True:
    c, _ = s.accept()
    threading.Thread(target=handle, args=(c,), daemon=True).start()