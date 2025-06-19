from ultralytics import YOLO
import cv2

# Load model (ganti 'best.pt' dengan path file kamu jika perlu)
model = YOLO("best.pt")

# Buka kamera (0 = default webcam)
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Jalankan deteksi
    results = model.predict(source=frame,  verbose=False, imgsz=640)

    # Ambil hasil frame dengan anotasi (bounding boxes, label, dsb)
    annotated_frame = results[0].plot()

    # Tampilkan frame
    cv2.imshow("YOLOv8 Detection", annotated_frame)

    # Tekan 'q' untuk keluar
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Bersihkan
cap.release()
cv2.destroyAllWindows()
