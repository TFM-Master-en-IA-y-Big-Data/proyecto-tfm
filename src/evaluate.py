import joblib
import pandas as pd
import matplotlib.pyplot as plt
from config import FEATURES, MODEL_PATH

model = joblib.load(MODEL_PATH)

df = pd.read_csv("../data/dataset.csv")

importances = model.feature_importances_

plt.figure()
plt.barh(FEATURES, importances)
plt.title("Feature Importance")
plt.xlabel("Importancia")
plt.show()