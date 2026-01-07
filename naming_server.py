import socket
import threading
import time
import json

HOST = "0.0.0.0"
PORT = 5000
TTL = 20  # waktu dalam detik sebelum service dianggap mati

services = {}
lock = threading.Lock()

def handle_client(conn, addr):
    try:
        data = conn.recv(1024).decode()
        msg = json.loads(data)

        # ===== CLIENT ACTION LOG =====
        if msg["type"] == "list":
            print(f"[CLIENT] {addr[0]} requested SERVICE LIST")

        elif msg["type"] == "lookup":
            print(f"[CLIENT] {addr[0]} lookup service '{msg['name']}'")

        # ===== SERVICE ACTION =====
        if msg["type"] == "register":
            services[msg["name"]] = {
                "ip": msg["ip"],
                "port": msg["port"],
                "last_seen": time.time()
            }
            print(f"[SERVICE UP] {msg['name']} registered "
                  f"({msg['ip']}:{msg['port']})")
            conn.send(b"REGISTERED")

        elif msg["type"] == "heartbeat":
            if msg["name"] in services:
                services[msg["name"]]["last_seen"] = time.time()
            conn.send(b"OK")

        elif msg["type"] == "lookup":
            name = msg["name"]
            if name in services:
                conn.send(json.dumps(services[name]).encode())
            else:
                conn.send(b"NOT_FOUND")

        elif msg["type"] == "list":
            result = {
                name: {"ip": info["ip"], "port": info["port"]}
                for name, info in services.items()
            }
            conn.send(json.dumps(result).encode())

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

print("Naming Server running guickly...")
while True:
    conn, addr = s.accept()
    threading.Thread(target=handle_client, args=(conn, addr)).start()
