"""
Auto-adds any student found in dataset/ folder
that is missing from the database.
Run: python fix_students.py
"""
import os
import pickle
from app import create_app
from app.models import Student, db

DATASET_DIR     = "dataset"
EMBEDDINGS_FILE = "embeddings.pkl"

app = create_app()

with app.app_context():
    print("=== Auto-fixing missing students ===\n")

    db_students = Student.query.all()
    db_names    = [s.name.lower().strip() for s in db_students]

    print("Current students in database:")
    for s in db_students:
        print(f"  ID:{s.id}  '{s.name}'")

    print("\nScanning dataset folders...")
    fixed = 0

    for folder in sorted(os.listdir(DATASET_DIR)):
        folder_path = os.path.join(DATASET_DIR, folder)
        if not os.path.isdir(folder_path):
            continue

        parts      = folder.split("_", 1)
        folder_id  = parts[0] if parts[0].isdigit() else None
        name       = parts[1].replace("_", " ") if len(parts) > 1 else folder

        # Check if already in database
        if name.lower().strip() in db_names:
            print(f"  '{name}'  →  already in database, skipping")
            continue

        # Add missing student
        student = Student(
            name         = name,
            roll_no      = folder_id or str(len(db_students) + fixed + 1),
            department   = "Not set",
            year         = "Not set",
            email        = "",
            parent_email = ""
        )
        db.session.add(student)
        db.session.commit()
        print(f"  '{name}'  →  ADDED to database (ID: {student.id})")
        fixed += 1

    if fixed == 0:
        print("\nAll dataset students already exist in database.")
        print("The problem might be a NAME MISMATCH.")
        print("\nDataset names vs Database names:")

        # Show side by side for manual comparison
        if os.path.exists(EMBEDDINGS_FILE):
            with open(EMBEDDINGS_FILE, "rb") as f:
                data = pickle.load(f)
            emb_names = list(set(data["names"]))
            all_db    = Student.query.all()
            for e in emb_names:
                match = next(
                    (s for s in all_db
                     if s.name.lower().strip() == e.lower().strip()),
                    None
                )
                if match:
                    print(f"  Dataset: '{e}'  →  DB: '{match.name}'  MATCH")
                else:
                    print(f"  Dataset: '{e}'  →  DB: NO MATCH  ← FIX THIS")
    else:
        print(f"\nFixed! Added {fixed} missing student(s) to database.")

    print("\nNow run: python run.py")