import cv2

def cek_webcam():
    for i in range(6):  # Cek dari indeks 0 hingga 5
        cap = cv2.VideoCapture(i)
        
        if not cap.isOpened():
            print(f"Webcam pada index {i} tidak tersedia.")
            continue
        
        print(f"Webcam pada index {i} berhasil dibuka. Tekan 'q' untuk keluar.")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print(f"Gagal membaca frame dari webcam pada index {i}.")
                break
            
            cv2.imshow(f"Cek Webcam {i}", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    cek_webcam()
