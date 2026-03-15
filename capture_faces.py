import cv2
import os

DATASET_DIR = "dataset"
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

def capture_faces(student_id, student_name, num_samples=30):
    folder = os.path.join(DATASET_DIR, f"{student_id}_{student_name}")
    os.makedirs(folder, exist_ok=True)

    cap = cv2.VideoCapture(0)
    count = 0

    print(f"\nCapturing {num_samples} face samples for {student_name}")
    print("Look at the camera. Slightly move your head left/right/up/down.")
    print("Press SPACE to capture | Press Q to quit\n")

    while count < num_samples:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        # Show progress
        cv2.putText(frame, f"Captured: {count}/{num_samples}",
                    (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, "SPACE = capture | Q = quit",
                    (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        cv2.imshow("Face Capture", frame)

        key = cv2.waitKey(1)

        if key == ord(' '):  # SPACE to capture
            if len(faces) == 0:
                print("  No face detected! Move closer to camera.")
            else:
                for (x, y, w, h) in faces:
                    face_img = gray[y:y+h, x:x+w]
                    path = os.path.join(folder, f"{count:03d}.jpg")
                    cv2.imwrite(path, face_img)
                    count += 1
                    print(f"  Captured {count}/{num_samples}")

        elif key == ord('q'):
            print("Capture cancelled.")
            break

    cap.release()
    cv2.destroyAllWindows()

    if count >= num_samples:
        print(f"\nDone! {count} samples saved for {student_name}")
        print(f"Saved in: {folder}")
    else:
        print(f"\nPartially done. {count} samples saved.")

if __name__ == "__main__":
    print("=== Face Sample Capture Tool ===\n")
    student_id   = input("Enter Student ID (e.g. 1): ").strip()
    student_name = input("Enter Student Name (no spaces, use underscore e.g. John_Doe): ").strip()
    num          = input("How many samples? (default 30, press Enter to skip): ").strip()
    num_samples  = int(num) if num.isdigit() else 30
    capture_faces(student_id, student_name, num_samples)