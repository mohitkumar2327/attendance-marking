import os, cv2

DATASET_DIR  = "dataset"
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

print("=== Dataset Check ===\n")
if not os.path.exists(DATASET_DIR):
    print("ERROR: dataset/ folder not found!")
else:
    for folder in os.listdir(DATASET_DIR):
        path   = os.path.join(DATASET_DIR, folder)
        images = [f for f in os.listdir(path) if f.endswith((".jpg",".png",".jpeg"))]
        faces_found = 0
        for img_file in images:
            img = cv2.imread(os.path.join(path, img_file), cv2.IMREAD_GRAYSCALE)
            det = face_cascade.detectMultiScale(img, 1.1, 4)
            if len(det) > 0:
                faces_found += 1
        print(f"  {folder}/")
        print(f"    Images : {len(images)}")
        print(f"    Faces detected in samples: {faces_found}/{len(images)}")
        if faces_found < 10:
            print(f"    Need more samples! Run capture_faces.py again.")
        else:
            print(f"    Good to go!")
        print()