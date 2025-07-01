# ============ Program Utama Python Robot KRSBI-B Created By Noven 2025 ================
# Program ini berisi komunikasi basestation dan Image Processing 
# Image Processing dipanggil dari detect_module.py 
# Bismillah KRI 2026

"""
Library yang digunakan
"""

import threading
import socket
import serial
import time
from detect_module import Detector

# === Konfigurasi Serial dan UDP ===
UDP_PORT = 28098
SERIAL_PORT = "COM7"
BAUDRATE = 115200

# Inisialisasi socket UDP
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind(("0.0.0.0", UDP_PORT))  # Dengarkan semua alamat IP

# Inisialisasi Serial untuk komunikasi dengan Arduino
try:
    arduino = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
    print(f"[Python] Terhubung ke Arduino di {SERIAL_PORT}")
except Exception as e:
    print(f"[ERROR] Tidak bisa terhubung ke Arduino: {e}")
    arduino = None

# === Thread untuk menerima data dari VB.NET via UDP dan kirim ke Arduino ===
def udp_receiver():
    while True:
        data, addr = udp_socket.recvfrom(1024)
        msg = data.decode().strip()
        print(f"[VB.NET =>] {msg}")

        if arduino:
            if not msg.endswith(">"):
                msg += ">"
            arduino.write(msg.encode())
            print(f"[Arduino <=] {msg}")

# === Thread untuk membaca respon serial dari Arduino ===
def baca_serial():
    while True:
        if arduino and arduino.in_waiting:
            balasan = arduino.readline().decode().strip()
            if balasan:
                print(f"[Arduino =>] {balasan}")

# === Thread untuk menjalankan deteksi kamera berbasis YOLOv8 ===
def kamera_detection():
    detector = Detector(arduino=arduino)
    detector.run()

# === Jalankan semua fungsi di thread terpisah ===
threading.Thread(target=udp_receiver, daemon=True).start()
threading.Thread(target=baca_serial, daemon=True).start()
threading.Thread(target=kamera_detection, daemon=True).start()

print("[Python] Semua sistem aktif. Tekan Ctrl+C untuk keluar.")

# Loop utama (idle loop) agar program tetap hidup dan ringan
try:
    while True:
        time.sleep(0.1)  # CPU-friendly idle loop
except KeyboardInterrupt:
    print("Program dihentikan.")
    if arduino:
        arduino.close()
