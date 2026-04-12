import pandas as pd
import joblib
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report
from sklearn.model_selection import TimeSeriesSplit
from config import FEATURES, TARGET, MODEL_PATH

df = pd.read_csv("../data/dataset.csv")

X = df[FEATURES]
y = df[TARGET]

# Validación temporal REAL
tscv = TimeSeriesSplit(n_splits=5)

scores = []

for train_idx, test_idx in tscv.split(X):
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

    model = XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric="logloss"
    )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    roc = roc_auc_score(y_test, y_prob)

    scores.append((acc, roc))

print("Resultados CV:")
for i, (acc, roc) in enumerate(scores):
    print(f"Fold {i+1} -> Accuracy: {acc:.4f}, ROC-AUC: {roc:.4f}")

# Entrenamiento final
model.fit(X, y)

joblib.dump(model, MODEL_PATH)

print("Modelo final guardado")