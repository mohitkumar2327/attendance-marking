import os
from app import create_app
from app.models import Student

app = create_app()
with app.app_context():
    print("=== Students in Database ===")
    for s in Student.query.all():
        print(f"  ID:{s.id}  Name: '{s.name}'")

    print("\n=== Folders in dataset/ ===")
    for folder in os.listdir("dataset"):
        print(f"  {folder}")