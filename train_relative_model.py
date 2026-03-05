import os
import cv2
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder

# ======================
# Config
# ======================
DATASET_PATH = "relative_faces"
MODEL_PATH = "relative_face_model.pkl"
LABEL_ENCODER_PATH = "relative_label_encoder.pkl"
IMAGE_SIZE = (100, 100)

# ======================
# Load Dataset
# ======================
def load_dataset():
    print("[INFO] Loading relative faces dataset...")
    X, y = [], []

    if not os.path.exists(DATASET_PATH):
        print("[ERROR] Dataset directory not found.")
        return None, None

    for label in os.listdir(DATASET_PATH):
        label_path = os.path.join(DATASET_PATH, label)
        if not os.path.isdir(label_path):
            continue

        for img_name in os.listdir(label_path):
            img_path = os.path.join(label_path, img_name)

            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue

            try:
                img = cv2.resize(img, IMAGE_SIZE)
            except Exception:
                continue

            X.append(img.flatten())
            y.append(label)

    if len(X) == 0:
        return None, None

    return np.array(X), np.array(y)


# ======================
# Main Training
# ======================
if __name__ == "__main__":
    X, y = load_dataset()

    if X is None or y is None or len(np.unique(y)) < 2:
        print("[ERROR] Not enough relative classes to train model.")
        exit(1)

    print("[INFO] Encoding labels...")
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    print("[INFO] Splitting dataset...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42
    )

    print("[INFO] Training SVM model for relatives...")
    model = SVC(kernel='linear', probability=True)
    model.fit(X_train, y_train)

    accuracy = model.score(X_test, y_test)
    print(f"[INFO] Relative face model accuracy: {accuracy * 100:.2f}%")

    print("[INFO] Saving relative model & label encoder...")
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    with open(LABEL_ENCODER_PATH, "wb") as f:
        pickle.dump(label_encoder, f)

    print("[SUCCESS] Relative face training completed.")
