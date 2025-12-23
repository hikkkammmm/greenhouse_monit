# client.py
# Client Fetcher dengan Upload, Download, dan Progress Download

import socket
import json
import sys
import os

NAMING_IP = "127.0.0.1"
NAMING_PORT = 6000
BUFFER = 4096


# ------------------ UTIL ------------------

def recv_all(sock, size):
    data = b""
    while len(data) < size:
        chunk = sock.recv(min(BUFFER, size - len(data)))
        if not chunk:
            break
        data += chunk
    return data


def recv_with_progress(sock, total_size):
    received = 0
    data = b""

    while received < total_size:
        chunk = sock.recv(min(BUFFER, total_size - received))
        if not chunk:
            break
        data += chunk
        received += len(chunk)

        percent = (received / total_size) * 100
        print(
            f"\rDownloading: {percent:6.2f}% "
            f"({received}/{total_size} bytes)",
            end=""
        )

    print()  # newline
    return data


# ------------------ LOOKUP ------------------

def lookup(service_name):
    s = socket.socket()
    s.connect((NAMING_IP, NAMING_PORT))
    s.sendall(f"LOOKUP|{service_name}".encode())
    resp = s.recv(1024)
    s.close()

    if resp == b"NOT_FOUND":
        print("[ERROR] Service tidak ditemukan di Naming Server")
        return None

    return json.loads(resp)


# ------------------ DOWNLOAD ------------------

def download(service_name, filename):
    info = lookup(service_name)
    if not info:
        return

    s = socket.socket()
    s.connect((info["ip"], info["port"]))
    s.sendall(f"GET|{filename}\n".encode())

    header = s.recv(32)
    if header == b"FILE_NOT_FOUND":
        print("[ERROR] File tidak ditemukan di FileNode")
        s.close()
        return

    size = int(header.decode())
    print(f"[INFO] Ukuran file: {size} bytes")

    data = recv_with_progress(s, size)
    s.close()

    out = "DOWNLOADED_" + filename
    with open(out, "wb") as f:
        f.write(data)

    print(f"[OK] Download selesai → {out}")


# ------------------ UPLOAD ------------------

def upload(service_name, filepath):
    if not os.path.exists(filepath):
        print("[ERROR] File tidak ditemukan")
        return

    filename = os.path.basename(filepath)
    size = os.path.getsize(filepath)

    info = lookup(service_name)
    if not info:
        return

    with open(filepath, "rb") as f:
        data = f.read()

    s = socket.socket()
    s.connect((info["ip"], info["port"]))
    s.sendall(f"PUT|{filename}\n".encode())
    s.sendall(f"{size:032d}".encode())
    s.sendall(data)

    resp = s.recv(1024)
    s.close()

    if resp == b"OK":
        print(f"[OK] Upload berhasil → {filename} ({size} bytes)")
    else:
        print("[ERROR] Upload gagal")


# ------------------ CLI ------------------

if len(sys.argv) != 4:
    print("Cara pakai:")
    print(" Upload   : python client.py filenodeA upload report.pdf")
    print(" Download : python client.py filenodeA download report.pdf")
    sys.exit()

SERVICE = sys.argv[1]
MODE = sys.argv[2]
TARGET = sys.argv[3]

if MODE == "upload":
    upload(SERVICE, TARGET)
elif MODE == "download":
    download(SERVICE, TARGET)
else:
    print("[ERROR] Mode tidak dikenal (gunakan upload / download)")
