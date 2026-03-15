from app import create_app
from app.face.recognize import train_model

app = create_app()
with app.app_context():
    train_model()
    print("Retraining complete!")