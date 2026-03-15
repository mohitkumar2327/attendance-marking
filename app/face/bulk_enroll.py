"""
Bulk enroll students from a folder structure:
  photos/
    StudentName1/
      photo1.jpg
      photo2.jpg
    StudentName2/
      photo1.jpg

Run: python bulk_enroll.py
"""
import os, shutil

SOURCE_DIR  = "photos"    # put all student photo folders here
DATASET_DIR = "dataset"

def bulk_enroll():
    if not os.path.exists(SOURCE_DIR):
        print(f"Create a '{SOURCE_DIR}' folder with student subfolders inside.")
        return

    student_id = 1
    # Find highest existing ID
    if os.path.exists(DATASET_DIR):
        existing = os.listdir(DATASET_DIR)
        if existing:
            ids = [int(f.split("_")[0]) for f in existing
                   if f.split("_")[0].isdigit()]
            student_id = max(ids) + 1 if ids else 1

    for name in sorted(os.listdir(SOURCE_DIR)):
        src = os.path.join(SOURCE_DIR, name)
        if not os.path.isdir(src):
            continue

        dst = os.path.join(DATASET_DIR, f"{student_id}_{name}")
        os.makedirs(dst, exist_ok=True)

        files = [f for f in os.listdir(src)
                 if f.lower().endswith((".jpg",".jpeg",".png"))]
        for f in files:
            shutil.copy(os.path.join(src, f), os.path.join(dst, f))

        print(f"  Enrolled: {name} ({len(files)} photos) → ID {student_id}")
        student_id += 1

    print(f"\nDone! Now run: python retrain.py")

if __name__ == "__main__":
    bulk_enroll()