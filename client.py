import socket
import json
import time
import os

NAMING_SERVER = ("127.0.0.1", 5000)
REFRESH_INTERVAL = 5

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def send_request(msg):
    s = socket.socket()
    s.connect(NAMING_SERVER)
    s.send(json.dumps(msg).encode())
    data = s.recv(4096)
    s.close()
    return data

def get_service_data(ip, port):
    try:
        s = socket.socket()
        s.connect((ip, port))
        s.send(b"request")
        data = s.recv(4096).decode()
        s.close()
        return data
    except:
        return "UNREACHABLE"

while True:
    print("\n=== MONITORING CLIENT ===")
    print("1. List semua service")
    print("2. Ambil data dari service")
    print("3. Dashboard monitoring")
    print("0. Keluar")

    choice = input("Pilih menu: ")

    # fucntion untuk setiap pilihan menu
    if choice == "1":
        data = send_request({"type": "list"})
        services = json.loads(data.decode())

        if not services:
            print("Tidak ada service aktif")
        else:
            print("\nService Aktif:")
            for name, info in services.items():
                print(f"- {name} ({info['ip']}:{info['port']})")

    #user ambil data dari service
    elif choice == "2":
        name = input("Nama service: ")
        data = send_request({"type": "lookup", "name": name})

        if data == b"NOT_FOUND":
            print("Service tidak ditemukan")
        else:
            info = json.loads(data.decode())
            s = socket.socket()
            s.connect((info["ip"], info["port"]))
            s.send(b"request")
            print("Response:", s.recv(4096).decode())
            s.close()

    # tampilan dashboard monitoring semuaserviceyang register
    elif choice == "3":
        try:
            while True:
                clear_screen()
                print("SMART GREENHOUSE DASHBOARD")
                print("=" * 45)

                data = send_request({"type": "list"})
                services = json.loads(data.decode())

                if not services:
                    print("Tidak ada service aktif")
                else:
                    for name, info in services.items():
                        result = get_service_data(info["ip"], info["port"])
                        print(f"Service : {name}")
                        print(f"IP      : {info['ip']}:{info['port']}")
                        print(f"Data    : {result}")
                        print("-" * 45)

                print(f"Refresh setiap {REFRESH_INTERVAL} detik")
                print("CTRL + C untuk kembali ke menu")
                time.sleep(REFRESH_INTERVAL)

        except KeyboardInterrupt:
            clear_screen()
            print("Kembali ke menu utama...")

    elif choice == "0":
        break
