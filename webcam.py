import cv2

# Buka kamera (0 untuk kamera utama, bisa coba 1 untuk kamera eksternal)
cap = cv2.VideoCapture(0)

# Cek apakah kamera berhasil dibuka
if not cap.isOpened():
    print("Error: Kamera tidak bisa dibuka.")
    exit()

while True:
    # Baca frame dari kamera
    ret, frame = cap.read()

    if not ret:
        print("Error: Gagal membaca frame.")
        break

    # Tampilkan frame di jendela
    cv2.imshow("Kamera", frame)

    # Tekan 'q' untuk keluar
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Tutup kamera dan jendela
cap.release()
cv2.destroyAllWindows()
