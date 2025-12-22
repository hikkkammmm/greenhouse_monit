import socket
import threading
import time
import json

HOST = "0.0.0.0"
PORT = 5000
TTL = 20  # detik

services = {}
lock = threading.Lock()

def handle_client(conn, addr):
    try:
        data = conn.recv(1024).decode()
        msg = json.loads(data)

        with lock:
            # 🔔 REGISTER (HANYA SEKALI)
            if msg["type"] == "register":
                services[msg["name"]] = {
                    "ip": msg["ip"],
                    "port": msg["port"],
                    "last_seen": time.time()
                }
                print(f"[REGISTERED] {msg['name']} "
                      f"({msg['ip']}:{msg['port']})")
                conn.send(b"REGISTERED")

            # ❤️ HEARTBEAT (TANPA LOG)
            elif msg["type"] == "heartbeat":
                if msg["name"] in services:
                    services[msg["name"]]["last_seen"] = time.time()
                conn.send(b"OK")
            
            elif msg["type"] == "list":
                service_list = {}
                for name, info in services.items():
                    service_list[name] = {
                        "ip": info["ip"],
                        "port": info["port"]
                    }
                conn.send(json.dumps(service_list).encode())

            

            # 🔍 LOOKUP
            elif msg["type"] == "lookup":
                name = msg["name"]
                if name in services:
                    conn.send(json.dumps(services[name]).encode())
                else:
                    conn.send(b"NOT_FOUND")
    except Exception as e:
        print("[ERROR]", e)

    conn.close()

def ttl_checker():
    while True:
        with lock:
            now = time.time()
            for name in list(services.keys()):
                if now - services[name]["last_seen"] > TTL:
                    print(f"[SERVICE DOWN] {name} (TTL expired)")
                    del services[name]
        time.sleep(5)

threading.Thread(target=ttl_checker, daemon=True).start()

s = socket.socket()
s.bind((HOST, PORT))
s.listen()

print("🚀 Naming Server running...")
while True:
    conn, addr = s.accept()
    threading.Thread(target=handle_client, args=(conn, addr)).start()
