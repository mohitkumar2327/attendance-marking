"""import os
import cv2

DATASET_DIR = "dataset"
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def save_face_images(student_id, student_name, files):
    folder = os.path.join(DATASET_DIR, f"{student_id}_{student_name}")
    os.makedirs(folder, exist_ok=True)
    saved = 0
    for i, file in enumerate(files):
        if file and file.filename:
            path = os.path.join(folder, f"{i:03d}.jpg")
            file.save(path)
            saved += 1
    print(f"Saved {saved} images for {student_name}")
    # Retrain model after new enrollment
    from app.face.recognize import train_model
    train_model()"""

import os
import cv2

DATASET_DIR = "dataset"
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

def save_face_images(student_id, student_name, files):
    folder = os.path.join(DATASET_DIR, f"{student_id}_{student_name}")
    os.makedirs(folder, exist_ok=True)
    saved = 0

    for i, file in enumerate(files):
        if file and file.filename:
            # Read image from upload
            import numpy as np
            file_bytes = np.frombuffer(file.read(), np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue

            # Detect and crop face from uploaded photo
            faces = face_cascade.detectMultiScale(img, 1.1, 5, minSize=(80,80))
            if len(faces) > 0:
                (x, y, w, h) = faces[0]
                face_crop = cv2.resize(img[y:y+h, x:x+w], (200, 200))
                path = os.path.join(folder, f"{saved:03d}.jpg")
                cv2.imwrite(path, face_crop)
                saved += 1
            else:
                # Save full image if no face detected (let recognizer handle it)
                path = os.path.join(folder, f"{saved:03d}.jpg")
                cv2.imwrite(path, img)
                saved += 1

    print(f"Saved {saved} images for {student_name}")
    from app.face.recognize import train_model
    train_model()