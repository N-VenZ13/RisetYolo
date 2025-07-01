import socket
import serial
import threading

# ===== Konfigurasi =====
UDP_PORT = 28098
SERIAL_PORT = "COM7"     # Ganti sesuai port Arduino
BAUDRATE = 9600

# ===== Setup Serial dan UDP =====
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind(("0.0.0.0", UDP_PORT))

try:
    arduino = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
    print(f"[Python] Terhubung ke Arduino di {SERIAL_PORT}")
except Exception as e:
    print(f"[ERROR] Tidak bisa terhubung ke Arduino: {e}")
    arduino = None

# ===== Kirim dari VB.NET ke Arduino =====
def udp_receiver():
    while True:
        data, addr = udp_socket.recvfrom(1024)
        msg = data.decode().strip()
        print(f"[VB.NET] >> {msg}")
        if arduino:
            if not msg.endswith(">"):
                msg += ">"
            arduino.write(msg.encode())
            print(f"[Arduino <=] {msg}")

# ===== Baca Serial dari Arduino =====
def baca_serial():
    while True:
        if arduino and arduino.in_waiting:
            balasan = arduino.readline().decode().strip()
            if balasan:
                print(f"[Arduino >>] {balasan}")

# ===== Jalankan thread =====
threading.Thread(target=udp_receiver, daemon=True).start()
threading.Thread(target=baca_serial, daemon=True).start()

print("[Python] Program jalan. Menunggu data dari VB.NET dan Arduino...")
try:
    while True:
        pass
except KeyboardInterrupt:
    if arduino:
        arduino.close()
