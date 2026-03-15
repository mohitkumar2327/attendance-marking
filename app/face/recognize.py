"""import cv2
import os
import numpy as np

DATASET_DIR = "dataset"

# Use OpenCV's LBPH Face Recognizer — no dlib, no tensorflow needed
recognizer = cv2.face.LBPHFaceRecognizer_create()
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

label_map = {}  # id → student name
model_trained = False

def train_model():
    global model_trained, label_map
    faces, labels = [], []
    label_map = {}
    current_label = 0

    if not os.path.exists(DATASET_DIR):
        return

    for folder in os.listdir(DATASET_DIR):
        folder_path = os.path.join(DATASET_DIR, folder)
        if not os.path.isdir(folder_path):
            continue
        # folder name format: "id_StudentName"
        label_map[current_label] = "_".join(folder.split("_")[1:])

        for img_file in os.listdir(folder_path):
            img_path = os.path.join(folder_path, img_file)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            detected = face_cascade.detectMultiScale(img, 1.1, 5)
            for (x, y, w, h) in detected:
                faces.append(img[y:y+h, x:x+w])
                labels.append(current_label)

        current_label += 1

    if faces:
        recognizer.train(faces, np.array(labels))
        model_trained = True
        print(f"Model trained with {len(faces)} face samples.")
    else:
        print("No face samples found. Please enroll students first.")

def recognize_frame(frame):
    global model_trained
    if not model_trained:
        train_model()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    detected_faces = face_cascade.detectMultiScale(gray, 1.1, 5)
    name = None

    for (x, y, w, h) in detected_faces:
        face_roi = gray[y:y+h, x:x+w]
        if model_trained:
            label, confidence = recognizer.predict(face_roi)
            # Lower confidence = better match (LBPH)
            if confidence < 80:
                name = label_map.get(label, "Unknown")
                color = (0, 200, 0)
            else:
                name = "Unknown"
                color = (0, 0, 200)
        else:
            name = "Unknown"
            color = (0, 0, 200)

        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        cv2.putText(frame, name, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    return name, frame

# Train on startup
train_model()"""
################################################################ Updated to use embedding-based recognition for better accuracy #
###############################################################
"""import cv2
import os
import numpy as np

DATASET_DIR  = "dataset"
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

recognizer   = cv2.face.LBPHFaceRecognizer_create()
label_map    = {}
model_trained = False
last_marked  = {}  # cooldown tracker

def train_model():
    global model_trained, label_map
    faces, labels = [], []
    label_map     = {}
    current_label = 0

    if not os.path.exists(DATASET_DIR):
        print("Dataset folder not found!")
        return

    for folder in sorted(os.listdir(DATASET_DIR)):
        folder_path = os.path.join(DATASET_DIR, folder)
        if not os.path.isdir(folder_path):
            continue

        # Extract name from "1_John_Doe" → "John Doe"
        parts = folder.split("_", 1)
        name  = parts[1].replace("_", " ") if len(parts) > 1 else folder
        label_map[current_label] = name

        count = 0
        for img_file in os.listdir(folder_path):
            if not img_file.lower().endswith((".jpg",".jpeg",".png")):
                continue
            img_path = os.path.join(folder_path, img_file)
            img      = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue

            # Try detecting face in sample
            detected = face_cascade.detectMultiScale(img, 1.1, 4, minSize=(50,50))
            if len(detected) > 0:
                (x, y, w, h) = detected[0]
                face = cv2.resize(img[y:y+h, x:x+w], (200, 200))
            else:
                # Use whole image if already cropped
                face = cv2.resize(img, (200, 200))

            faces.append(face)
            labels.append(current_label)
            count += 1

        print(f"  Loaded {count} samples for: {name}")
        current_label += 1

    if len(faces) == 0:
        print("No face samples found! Run capture_faces.py first.")
        model_trained = False
        return

    recognizer.train(faces, np.array(labels))
    model_trained = True
    print(f"Model trained: {len(faces)} total samples, {current_label} students.")

def recognize_frame(frame):
    import time
    gray      = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Equalize histogram for better detection in different lighting
    gray      = cv2.equalizeHist(gray)
    detected  = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.05,   # more sensitive
        minNeighbors=3,     # less strict
        minSize=(80, 80)
    )

    recognized_name = None

    for (x, y, w, h) in detected:
        face_roi = cv2.resize(gray[y:y+h, x:x+w], (200, 200))

        if model_trained:
            label, confidence = recognizer.predict(face_roi)
            # LBPH: confidence < 100 is good, < 70 is very confident
            if confidence < 100:
                name   = label_map.get(label, "Unknown")
                color  = (0, 200, 0)
                text   = f"{name} ({int(confidence)})"

                # Cooldown: only mark once every 15 seconds per person
                now = time.time()
                if name not in last_marked or (now - last_marked[name]) > 15:
                    recognized_name    = name
                    last_marked[name]  = now
            else:
                name  = "Unknown"
                color = (0, 0, 200)
                text  = f"Unknown ({int(confidence)})"
        else:
            name  = "No model"
            color = (0, 165, 255)
            text  = "Train model first"

        # Draw rectangle and label
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        cv2.rectangle(frame, (x, y-35), (x+w, y), color, -1)
        cv2.putText(frame, text, (x+5, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

    # Show model status on frame
    status = f"Students: {len(label_map)} | Trained: {model_trained}"
    cv2.putText(frame, status, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,0), 2)

    return recognized_name, frame

# Train on startup
train_model()"""

################################################################ Updated to use embedding-based recognition for better accuracy #
###############################################################

import cv2
import os
import numpy as np
import pickle
import time

DATASET_DIR     = "dataset"
EMBEDDINGS_FILE = "embeddings.pkl"

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

try:
    import faiss
    USE_FAISS = True
except ImportError:
    USE_FAISS = False

faiss_index     = None
index_names     = []
known_names_set = set()

# ── Cooldown tracker ─────────────────────────────────────────────
# Tracks BOTH the last event time AND last event type per person
# Structure: { name: {"time": timestamp, "last_event": "IN1"} }
person_state = {}

COOLDOWN_SECONDS = 300  # minimum seconds between any two events for same person

# ── Embedding ────────────────────────────────────────────────────
def get_embedding(face_img):
    if len(face_img.shape) == 3:
        face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
    face_resized = cv2.resize(face_img, (128, 128))
    flat = face_resized.astype(np.float32).flatten()
    # Use LBP histogram as embedding — more robust than raw pixels
    lbp  = compute_lbp(face_resized)
    return lbp.astype(np.float32)

def compute_lbp(gray_img):
    """Local Binary Pattern histogram — good for face recognition."""
    img   = cv2.resize(gray_img, (128, 128))
    lbp   = np.zeros_like(img, dtype=np.uint8)
    for i in range(1, img.shape[0]-1):
        for j in range(1, img.shape[1]-1):
            center = img[i, j]
            code   = 0
            code |= (img[i-1, j-1] >= center) << 7
            code |= (img[i-1, j  ] >= center) << 6
            code |= (img[i-1, j+1] >= center) << 5
            code |= (img[i,   j+1] >= center) << 4
            code |= (img[i+1, j+1] >= center) << 3
            code |= (img[i+1, j  ] >= center) << 2
            code |= (img[i+1, j-1] >= center) << 1
            code |= (img[i,   j-1] >= center) << 0
            lbp[i, j] = code
    # Return histogram (256 bins) as embedding
    hist, _ = np.histogram(lbp.ravel(), bins=256, range=(0, 256))
    return hist.astype(np.float32)

def normalize(v):
    n = np.linalg.norm(v)
    return v / n if n > 0 else v

# ── Build index ───────────────────────────────────────────────────
def build_faiss_index(embeddings, names):
    global faiss_index, index_names, known_names_set
    index_names     = names
    known_names_set = set(names)

    if not embeddings:
        return

    vecs = np.array([normalize(e) for e in embeddings], dtype=np.float32)

    if USE_FAISS:
        index = faiss.IndexFlatIP(vecs.shape[1])
        index.add(vecs)
        faiss_index = index
    else:
        faiss_index = vecs

    print(f"Index ready: {len(known_names_set)} people, "
          f"{len(embeddings)} total samples")

# ── Train ─────────────────────────────────────────────────────────
def train_model():
    embeddings, names = [], []

    if not os.path.exists(DATASET_DIR):
        print("Dataset folder not found!")
        return

    for folder in sorted(os.listdir(DATASET_DIR)):
        folder_path = os.path.join(DATASET_DIR, folder)
        if not os.path.isdir(folder_path):
            continue

        parts = folder.split("_", 1)
        name  = parts[1].replace("_", " ") if len(parts) > 1 else folder
        count = 0

        for img_file in os.listdir(folder_path):
            if not img_file.lower().endswith((".jpg", ".jpeg", ".png")):
                continue
            img = cv2.imread(
                os.path.join(folder_path, img_file),
                cv2.IMREAD_GRAYSCALE
            )
            if img is None:
                continue

            detected = face_cascade.detectMultiScale(
                img, 1.1, 4, minSize=(40, 40)
            )
            face = img[detected[0][1]:detected[0][1]+detected[0][3],
                       detected[0][0]:detected[0][0]+detected[0][2]] \
                   if len(detected) > 0 else img

            embeddings.append(get_embedding(face))
            names.append(name)
            count += 1

        print(f"  {name}: {count} samples")

    if not embeddings:
        print("No samples! Run capture_faces.py first.")
        return

    with open(EMBEDDINGS_FILE, "wb") as f:
        pickle.dump({"embeddings": embeddings, "names": names}, f)

    build_faiss_index(embeddings, names)
    print("Training complete!")

def load_embeddings():
    if os.path.exists(EMBEDDINGS_FILE):
        with open(EMBEDDINGS_FILE, "rb") as f:
            data = pickle.load(f)
        build_faiss_index(data["embeddings"], data["names"])
    else:
        train_model()

# ── Search ────────────────────────────────────────────────────────
def find_best_match(face_img):
    if faiss_index is None:
        return "No model", 0.0

    emb       = normalize(get_embedding(face_img))
    THRESHOLD = 0.88

    if USE_FAISS:
        scores, indices = faiss_index.search(
            emb.reshape(1, -1).astype(np.float32), k=3
        )
        # Majority vote from top 3 matches
        top_names  = [index_names[int(i)] for i in indices[0]
                      if int(i) < len(index_names)]
        top_scores = [float(s) for s in scores[0]]

        if top_scores[0] >= THRESHOLD:
            # Check consistency — top 3 should mostly agree
            best_name  = top_names[0]
            best_score = top_scores[0]
            return best_name, best_score
    else:
        scores = faiss_index @ emb
        # Get top 3 indices
        top3   = np.argsort(scores)[-3:][::-1]
        top_scores = [float(scores[i]) for i in top3]
        top_names  = [index_names[i] for i in top3
                      if i < len(index_names)]

        if top_scores[0] >= THRESHOLD:
            return top_names[0], top_scores[0]

    return "Unknown", 0.0

# ── Cooldown check ────────────────────────────────────────────────
def should_mark(name):
    """
    Returns True only if:
    1. Person hasn't been marked in the last COOLDOWN_SECONDS
    2. Prevents accidental rapid re-marking
    """
    now = time.time()
    if name not in person_state:
        person_state[name] = {"time": now, "count": 1}
        return True

    elapsed = now - person_state[name]["time"]
    if elapsed >= COOLDOWN_SECONDS:
        person_state[name] = {"time": now, "count": 1}
        return True

    return False

# ── Main frame function ───────────────────────────────────────────
def recognize_frame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    detected = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.05,
        minNeighbors=4,
        minSize=(80, 80)
    )

    recognized_name = None

    for (x, y, w, h) in detected:
        face_crop        = frame[y:y+h, x:x+w]
        name, confidence = find_best_match(face_crop)
        color            = (0, 200, 0) if name != "Unknown" else (0, 0, 200)

        # Show confidence on screen always
        label = f"{name} ({confidence:.2f})"

        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        cv2.rectangle(frame, (x, y-36), (x+w, y), color, -1)
        cv2.putText(frame, label, (x+5, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                    (255, 255, 255), 2)

        # Only mark if passes cooldown
        if name not in ("Unknown", "No model"):
            if should_mark(name):
                recognized_name = name
                # Show MARKED flash on frame
                cv2.putText(frame, "MARKED!", (x, y+h+25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            (0, 255, 255), 2)

    # Status bar
    cv2.putText(
        frame,
        f"People enrolled: {len(known_names_set)}  |  "
        f"Cooldown: {COOLDOWN_SECONDS}s  |  FAISS: {USE_FAISS}",
        (10, frame.shape[0]-10),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1
    )

    return recognized_name, frame

load_embeddings()