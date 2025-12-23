# filenode.py
import socket, threading, time, os, sys

if len(sys.argv) != 4:
    print("python filenode.py filenodeA 7001 labA")
    exit()

SERVICE_NAME = sys.argv[1]
PORT = int(sys.argv[2])
FOLDER = sys.argv[3]

NAMING_IP = "127.0.0.1"
NAMING_PORT = 6000
IP = "127.0.0.1"

os.makedirs(FOLDER, exist_ok=True)

def heartbeat():
    while True:
        try:
            s = socket.socket()
            s.connect((NAMING_IP, NAMING_PORT))
            s.sendall(f"HEARTBEAT|{SERVICE_NAME}|{IP}|{PORT}".encode())
            s.recv(10)
            s.close()
        except:
            pass
        time.sleep(5)

def recv_line(conn):
    data = b""
    while not data.endswith(b"\n"):
        part = conn.recv(1)
        if not part:
            break
        data += part
    return data.decode().strip()

def recv_all(conn, size):
    data = b""
    while len(data) < size:
        part = conn.recv(min(4096, size - len(data)))
        if not part:
            break
        data += part
    return data

def handle(conn):
    try:
        header = recv_line(conn)
        if not header:
            return

        cmd, filename = header.split("|", 1)

        if cmd == "PUT":
            size = int(conn.recv(32).decode())
            data = recv_all(conn, size)
            open(os.path.join(FOLDER, filename), "wb").write(data)
            conn.sendall(b"OK")
            print(f"[UPLOAD] {filename} ({size} bytes)")

        elif cmd == "GET":
            path = os.path.join(FOLDER, filename)
            if os.path.exists(path):
                data = open(path, "rb").read()
                conn.sendall(f"{len(data):032d}".encode())
                conn.sendall(data)
            else:
                conn.sendall(b"FILE_NOT_FOUND")

    except Exception as e:
        print("[FileNode ERROR]", e)
    finally:
        conn.close()

threading.Thread(target=heartbeat, daemon=True).start()

s = socket.socket()
s.bind(("0.0.0.0", PORT))
s.listen()
print(f"[{SERVICE_NAME}] aktif di {IP}:{PORT} | folder={FOLDER}")

while True:
    c, _ = s.accept()
    threading.Thread(target=handle, args=(c,), daemon=True).start()
