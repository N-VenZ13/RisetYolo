import cv2
import argparse
from ultralytics import YOLO
import supervision as sv

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="YOLOv8 live")
    parser.add_argument(
        "--webcam-resolution",
        default=[1280, 720],
        nargs=2,
        type=int,
        help="Resolution of the webcam feed (width height)"
    )
    args = parser.parse_args()
    return args

def main():
    args = parse_arguments()
    frame_width, frame_height = args.webcam_resolution

    cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

    model = YOLO("train2.pt")

    # Inisialisasi BoxAnnotator tanpa parameter tambahan
    box_annotator = sv.BoxAnnotator(thickness=2)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Deteksi objek menggunakan YOLOv8
        results = model(frame)[0]

        # Ekstraksi bounding boxes, confidence, dan class IDs
        boxes = results.boxes.xyxy.cpu().numpy()
        confidences = results.boxes.conf.cpu().numpy()
        class_ids = results.boxes.cls.cpu().numpy()
        class_names = model.names

        # Membuat objek Detections
        detections = sv.Detections(
            xyxy=boxes,
            confidence=confidences,
            class_id=class_ids.astype(int)
        )

        # Menambahkan bounding box pada frame
        frame = box_annotator.annotate(scene=frame, detections=detections)

        # Mendapatkan koordinat tengah kamera
        center_camera_x = frame_width // 2
        center_camera_y = frame_height // 2

        # Menambahkan label, koordinat pusat, dan tali pusat secara manual
        for box, confidence, class_id in zip(boxes, confidences, class_ids):
            x1, y1, x2, y2 = box.astype(int)
            x_center = (x1 + x2) / 2
            y_center = (y1 + y2) / 2

            label = f"{class_names[int(class_id)]} {confidence:.2f}"

            # Menambahkan koordinat pusat
            coord_label = f"({int(x_center)}, {int(y_center)})"

            # Menentukan posisi teks
            text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            text_x = x1
            text_y = y1 - 10 if y1 - 10 > 10 else y1 + 10

            # Menambahkan latar belakang teks
            cv2.rectangle(
                frame,
                (text_x, text_y - text_size[1]),
                (text_x + text_size[0], text_y + 5),
                (0, 0, 0),
                -1
            )

            # Menambahkan teks untuk label
            cv2.putText(
                frame,
                label,
                (text_x, text_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                2
            )

            # Menambahkan teks untuk koordinat pusat
            cv2.putText(
                frame,
                coord_label,
                (int(x_center) - 20, int(y_center) - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )

            # Menambahkan titik pusat
            cv2.circle(frame, (int(x_center), int(y_center)), 5, (0, 255, 0), -1)

            # Menambahkan tali pusat dari tengah kamera ke objek
            cv2.line(
                frame,
                (center_camera_x, center_camera_y),
                (int(x_center), int(y_center)),
                (255, 255, 0),
                2
            )

        # Tampilkan frame yang telah dianotasi
        cv2.imshow("YOLOv8 Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
