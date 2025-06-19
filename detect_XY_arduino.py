import cv2
import argparse
import numpy as np
import serial  # Untuk komunikasi serial
import time
from ultralytics import YOLO
import supervision as sv

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="YOLOv8 live")
    parser.add_argument("--webcam-resolution", default=[1280, 720], nargs=2, type=int, help="Resolution of the webcam feed (width height)")
    parser.add_argument("--display-scale", default=0.5, type=float, help="Scaling factor for display window")
    args = parser.parse_args()
    return args

def main():
    args = parse_arguments()
    frame_width, frame_height = args.webcam_resolution
    display_scale = args.display_scale

    # **Buka komunikasi serial ke Arduino**
    arduino = serial.Serial('COM4', 9600, timeout=1)  # Ganti COM3 dengan port Arduino Anda
    time.sleep(2)  # Tunggu Arduino siap

    cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

    model = YOLO("best_ball.pt")
    box_annotator = sv.BoxAnnotator(thickness=2)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)[0]
        boxes = results.boxes.xyxy.cpu().numpy()
        confidences = results.boxes.conf.cpu().numpy()
        class_ids = results.boxes.cls.cpu().numpy()
        class_names = model.names

        detections = sv.Detections(
            xyxy=boxes,
            confidence=confidences,
            class_id=class_ids.astype(int)
        )

        frame = box_annotator.annotate(scene=frame, detections=detections)

        center_camera_x = frame_width // 2
        center_camera_y = frame_height // 2

        bola_terdeteksi = False  # Flag untuk cek apakah bola terdeteksi

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
                
                bola_terdeteksi = True  # Bola ditemukan
                
                print(f"Bola Terdeteksi pada: X={x}, Y={y}")
                cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

                # **Kirim data X dan Y ke Arduino**
                data = f"{x},{y}\n"
                arduino.write(data.encode())

            label = f"{class_names[int(class_id)]} {confidence:.2f}"
            coord_label = f"({int(x_center)}, {int(y_center)})"
            cv2.putText(frame, coord_label, (int(x_center) - 20, int(y_center) - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.line(frame, (center_camera_x, center_camera_y), (int(x_center), int(y_center)), (255, 255, 0), 2)

        # Jika tidak ada bola terdeteksi, kirim koordinat (0,0)
        if not bola_terdeteksi:
            print("Bola tidak terdeteksi, mengirim: X=0, Y=0")
            arduino.write("0,0\n".encode())

        frame_resized = cv2.resize(frame, (int(frame_width * display_scale), int(frame_height * display_scale)))
        cv2.imshow("YOLOv8 Detection", frame_resized)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    arduino.close()  # Tutup komunikasi serial

if __name__ == "__main__":
    main()
