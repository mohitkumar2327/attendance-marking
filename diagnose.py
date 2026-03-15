import os
import cv2
import numpy as np
import pickle
from app import create_app
from app.models import Student

DATASET_DIR     = "dataset"
EMBEDDINGS_FILE = "embeddings.pkl"
face_cascade    = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

app = create_app()

print("=" * 50)
print("DIAGNOSIS REPORT")
print("=" * 50)

# 1. Check database
print("\n1. STUDENTS IN DATABASE:")
with app.app_context():
    students = Student.query.all()
    if not students:
        print("   ERROR: No students in database!")
    for s in students:
        print(f"   ID:{s.id}  Name:'{s.name}'  Roll:{s.roll_no}")

# 2. Check dataset folders
print("\n2. DATASET FOLDERS:")
if not os.path.exists(DATASET_DIR):
    print("   ERROR: dataset/ folder missing!")
else:
    for folder in sorted(os.listdir(DATASET_DIR)):
        path   = os.path.join(DATASET_DIR, folder)
        images = [f for f in os.listdir(path)
                  if f.lower().endswith((".jpg",".png",".jpeg"))]
        faces  = 0
        for img_file in images:
            img = cv2.imread(os.path.join(path, img_file), cv2.IMREAD_GRAYSCALE)
            if img is not None:
                det = face_cascade.detectMultiScale(img, 1.1, 4)
                if len(det) > 0:
                    faces += 1
        status = "OK" if faces >= 20 else f"NEED MORE SAMPLES (only {faces})"
        print(f"   {folder}/  →  {len(images)} images, {faces} faces  →  {status}")

# 3. Check embeddings file
print("\n3. EMBEDDINGS FILE:")
if not os.path.exists(EMBEDDINGS_FILE):
    print("   ERROR: embeddings.pkl not found! Run: python retrain.py")
else:
    with open(EMBEDDINGS_FILE, "rb") as f:
        data = pickle.load(f)
    names  = data["names"]
    unique = list(set(names))
    print(f"   Total embeddings : {len(names)}")
    print(f"   Unique people    : {len(unique)}")
    for u in unique:
        count = names.count(u)
        print(f"     '{u}' → {count} embeddings")

# 4. Check name matching
print("\n4. NAME MATCH CHECK (database vs dataset):")
with app.app_context():
    students = Student.query.all()
    db_names = [s.name for s in students]

if os.path.exists(EMBEDDINGS_FILE):
    with open(EMBEDDINGS_FILE, "rb") as f:
        data = pickle.load(f)
    emb_names = list(set(data["names"]))

    for emb_name in emb_names:
        # Check exact match
        if emb_name in db_names:
            print(f"   '{emb_name}'  →  MATCH FOUND in database")
        else:
            # Try partial match
            partial = [d for d in db_names
                       if emb_name.lower() in d.lower()
                       or d.lower() in emb_name.lower()]
            if partial:
                print(f"   '{emb_name}'  →  PARTIAL match: '{partial[0]}'  "
                      f"(FIX NEEDED)")
            else:
                print(f"   '{emb_name}'  →  NO MATCH in database!  "
                      f"(add student to DB)")

print("\n" + "=" * 50)
print("Run: python fix_students.py  to auto-fix database")
print("=" * 50)