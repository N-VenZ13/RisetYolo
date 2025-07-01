# ============ Module Program Python Created By Noven ================
# Program ini berisi tentang pengolahan data kamera dengan model YOLO
# Program ini di fokuskan untuk mengatur bagian ImageProcessing pada Robot

"""
Library yang digunakan
"""
import cv2
import numpy as np
import serial
import time
from ultralytics import YOLO
import supervision as sv

class Detector:
    """
    Kelas untuk mendeteksi objek menggunakan YOLOv8 dan mengirimkan koordinat deteksi ke Arduino.
    """
    def __init__(self, arduino, resolution=(1280, 720), scale=0.5):
        """
        Inisialisasi kamera, model YOLOv8, dan parameter tampilan.

        :param arduino: objek serial dari main.py
        :param resolution: resolusi kamera (width, height)
        :param scale: skala tampilan (untuk preview)
        """
        self.arduino = arduino
        self.frame_width, self.frame_height = resolution
        self.display_scale = scale
        self.running = True

        # Inisialisasi kamera
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)

        # Load model YOLOv8
        self.model = YOLO("best_ball4.pt")
        self.box_annotator = sv.BoxAnnotator(thickness=2)

        # Simpan data terakhir yang dikirim agar tidak redundant
        self.last_sent = ""

    def run(self):
        """
        Fungsi utama untuk mendeteksi objek, menggambar anotasi, dan mengirim koordinat ke Arduino.
        """
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break

            # Jalankan deteksi objek menggunakan YOLOv8
            results = self.model(frame)[0]
            boxes = results.boxes.xyxy.cpu().numpy()
            confidences = results.boxes.conf.cpu().numpy()
            class_ids = results.boxes.cls.cpu().numpy()
            class_names = self.model.names

            # Konversi hasil ke format Detections dari supervision
            detections = sv.Detections(
                xyxy=boxes,
                confidence=confidences,
                class_id=class_ids.astype(int)
            )

            # Gambar bounding box
            frame = self.box_annotator.annotate(scene=frame, detections=detections)

            # Titik tengah frame kamera
            center_camera_x = self.frame_width // 2
            center_camera_y = self.frame_height // 2

            # Data default jika tidak ada deteksi
            current_data = "x0y0>\n"

            # Iterasi setiap deteksi
            for box, confidence, class_id in zip(boxes, confidences, class_ids):
                x1, y1, x2, y2 = box.astype(int)
                x_center = (x1 + x2) // 2
                y_center = (y1 + y2) // 2

                current_data = f"x{x_center}y{y_center}>\n"

                # Gambar titik tengah objek
                print(f"Bola Terdeteksi pada: X={x_center}, Y={y_center}")
                cv2.circle(frame, (x_center, y_center), 5, (0, 255, 0), -1)

                # Gambar garis dari titik tengah kamera ke objek
                cv2.line(
                    frame,
                    (center_camera_x, center_camera_y),
                    (int(x_center), int(y_center)),
                    (255, 255, 0),
                    2
                )

            # Kirim data ke Arduino hanya jika berbeda dari sebelumnya
            if self.arduino and current_data != self.last_sent:
                try:
                    self.arduino.write(current_data.encode())
                    self.last_sent = current_data
                    print(f"[Kamera => Arduino] {current_data.strip()}")
                except Exception as e:
                    print(f"[ERROR Kirim Serial]: {e}")

            # Tampilkan hasil deteksi (diperbesar sesuai skala)
            frame_resized = cv2.resize(
                frame,
                (int(self.frame_width * self.display_scale), int(self.frame_height * self.display_scale))
            )
            cv2.imshow("YOLOv8 Detection", frame_resized)

            # Baca feedback dari Arduino jika ada
            if self.arduino and self.arduino.in_waiting:
                try:
                    line = self.arduino.readline().decode().strip()
                    if line:
                        print(f"[Arduino => Kamera] {line}")
                except Exception as e:
                    print(f"[Serial Error]: {e}")

            # Tekan tombol 'q' untuk keluar
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cleanup()

    def cleanup(self):
        """
        Bersihkan kamera dan tutup semua jendela saat selesai.
        """
        self.cap.release()
        cv2.destroyAllWindows()
        if self.arduino:
            self.arduino.close()
