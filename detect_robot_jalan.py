import cv2
import argparse
import numpy as np
import serial
import time
from ultralytics import YOLO
import supervision as sv

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="YOLOv8 live")
    parser.add_argument("--webcam-resolution", default=[1280, 720], nargs=2, type=int, help="Resolution of the webcam feed (width height)")
    parser.add_argument("--display-scale", default=0.5, type=float, help="Scaling factor for display window")
    return parser.parse_args()

def main():
    args = parse_arguments()
    frame_width, frame_height = args.webcam_resolution
    display_scale = args.display_scale

    # Hubungkan ke Arduino
    try:
        arduino = serial.Serial('COM7', 115200, timeout=1)
        time.sleep(2)  # Tunggu Arduino siap
    except serial.SerialException as e:
        print(f"Gagal membuka port serial: {e}")
        return

    # Inisialisasi kamera
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

    # Load model YOLOv8
    model = YOLO("best_ball2.pt")
    box_annotator = sv.BoxAnnotator(thickness=2)

    last_sent = ""  # Simpan data terakhir yang dikirim

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Deteksi objek menggunakan YOLO
        results = model(frame)[0]
        boxes = results.boxes.xyxy.cpu().numpy()
        confidences = results.boxes.conf.cpu().numpy()
        class_ids = results.boxes.cls.cpu().numpy()
        class_names = model.names

        # Konversi hasil ke format supervision
        detections = sv.Detections(
            xyxy=boxes,
            confidence=confidences,
            class_id=class_ids.astype(int)
        )

        frame = box_annotator.annotate(scene=frame, detections=detections)

        center_camera_x = frame_width // 2
        center_camera_y = frame_height // 2

        bola_terdeteksi = False
        current_data = "x0y0>\n"  # Default: tidak ada bola

        # Cek setiap deteksi
        for box, confidence, class_id in zip(boxes, confidences, class_ids):
            x1, y1, x2, y2 = box.astype(int)
            x_center = (x1 + x2) // 2
            y_center = (y1 + y2) // 2

            roi = frame[y1:y2, x1:x2]
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edged = cv2.Canny(blurred, 50, 150)
            contours, _ = cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                area = max(contours, key=cv2.contourArea)
                ((x, y), radius) = cv2.minEnclosingCircle(area)
                x, y = int(x), int(y)

                bola_terdeteksi = True
                current_data = f"x{x}y{y}>\n"  # Format yang bisa diparse Arduino

                print(f"Bola Terdeteksi pada: X={x}, Y={y}")
                cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

            label = f"{class_names[int(class_id)]} {confidence:.2f}"
            coord_label = f"({int(x_center)}, {int(y_center)})"
            cv2.putText(frame, coord_label, (int(x_center) - 20, int(y_center) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.line(frame, (center_camera_x, center_camera_y), (int(x_center), int(y_center)), (255, 255, 0), 2)


            # cv2.line(frame, (1272, 0), (1275, 720), (255, 0, 0), 2)  # batas kiri-tengah
            # cv2.line(frame, (840, 0), (840, 710), (0, 255, 0), 2)  # batas tengah-kanan


        # Kirim ke Arduino hanya jika data berubah
        if current_data != last_sent:
            try:
                arduino.write(current_data.encode())
                last_sent = current_data
                time.sleep(0.02)
                print(f"Dikirim ke Arduino: {current_data.strip()}")
            except Exception as e:
                print(f"[ERROR Kirim Serial]: {e}")

        # Tampilkan frame
        frame_resized = cv2.resize(frame, (int(frame_width * display_scale), int(frame_height * display_scale)))
        cv2.imshow("YOLOv8 Detection", frame_resized)

        # Baca respon dari Arduino
        if arduino.in_waiting:
            try:
                line = arduino.readline().decode().strip()
                if line:
                    print(f"[Arduino] {line}")
            except Exception as e:
                print(f"[Serial Error]: {e}")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Bersihkan setelah selesai
    cap.release()
    cv2.destroyAllWindows()
    arduino.close()

if __name__ == "__main__":
    main()
