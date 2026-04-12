import pandas as pd
from config import RAW_DATA_PATH, DATA_PATH


def compute_features(df):
    # Ordenar correctamente
    df = df.sort_values(["coin", "timestamp"])

    # =========================
    # CAMBIOS PORCENTUALES
    # =========================
    df["change_1h_pct"] = df.groupby("coin")["price_usd"].pct_change(1) * 100
    df["change_24h_pct"] = df.groupby("coin")["price_usd"].pct_change(1) * 100
    df["change_7d_pct"] = df.groupby("coin")["price_usd"].pct_change(7) * 100

    # =========================
    # RSI (14)
    # =========================
    delta = df.groupby("coin")["price_usd"].diff()

    gain = (delta.where(delta > 0, 0)).groupby(df["coin"]).rolling(14).mean().reset_index(level=0, drop=True)
    loss = (-delta.where(delta < 0, 0)).groupby(df["coin"]).rolling(14).mean().reset_index(level=0, drop=True)

    rs = gain / loss
    df["rsi_14"] = 100 - (100 / (1 + rs))

    # =========================
    # VOLATILIDAD (30 días)
    # =========================
    df["volatility_30d"] = df.groupby("coin")["price_usd"].rolling(30).std().reset_index(level=0, drop=True)

    # =========================
    # MEDIAS MÓVILES (SMOOTHING)
    # =========================
    df["price_sma_7"] = df.groupby("coin")["price_usd"].rolling(7).mean().reset_index(level=0, drop=True)
    df["price_sma_30"] = df.groupby("coin")["price_usd"].rolling(30).mean().reset_index(level=0, drop=True)

    return df


def build_dataset():
    print("Cargando datos...")
    df = pd.read_csv(RAW_DATA_PATH)

    # Convertir timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # =========================
    # FEATURE ENGINEERING
    # =========================
    print("Generando features...")
    df = compute_features(df)

    # =========================
    # TARGET (sube/baja)
    # =========================
    df["target"] = (df["change_24h_pct"] > 0).astype(int)

    # =========================
    # LIMPIEZA FINAL
    # =========================
    df = df.dropna()

    # =========================
    # GUARDAR DATASET
    # =========================
    df.to_csv(DATA_PATH, index=False)

    print("Dataset generado correctamente")
    print(f"Shape final: {df.shape}")


if __name__ == "__main__":
    build_dataset()