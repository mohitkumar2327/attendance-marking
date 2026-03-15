from app import create_app
from app import db

app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()
    print("Database reset complete!")
    print("Default admin recreated: admin / admin123")
    print("NOTE: All previous students deleted.")
    print("Re-add them via Excel import or Register form.")