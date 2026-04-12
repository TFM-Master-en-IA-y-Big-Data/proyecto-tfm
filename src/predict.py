import joblib
import numpy as np
from config import MODEL_PATH, FEATURES

model = joblib.load(MODEL_PATH)

def predict(data):
    values = [data[f] for f in FEATURES]
    arr = np.array([values])

    prob = model.predict_proba(arr)[0][1]

    return {
        "prediction": int(prob > 0.5),
        "probability": float(prob)
    }