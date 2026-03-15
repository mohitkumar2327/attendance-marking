import os, pickle
from app import create_app
from app.face.recognize import train_model

# Delete old embeddings file so it builds fresh
if os.path.exists("embeddings.pkl"):
    os.remove("embeddings.pkl")
    print("Old embeddings deleted.")

app = create_app()
with app.app_context():
    train_model()
    print("Fresh retrain complete!")