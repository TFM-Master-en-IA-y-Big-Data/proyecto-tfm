import requests
import pandas as pd
from datetime import datetime
from config import COINS, RAW_DATA_PATH


def fetch_coin_data(coin="bitcoin", days=365):
    url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart"

    params = {
        "vs_currency": "usd",
        "days": days
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"Error descargando {coin}")
        return None

    data = response.json()

    prices = data["prices"]
    volumes = data["total_volumes"]
    market_caps = data["market_caps"]

    rows = []

    for i in range(len(prices)):
        timestamp = datetime.fromtimestamp(prices[i][0] / 1000)

        rows.append({
            "timestamp": timestamp,
            "coin": coin,
            "price_usd": prices[i][1],
            "volume_24h": volumes[i][1],
            "market_cap": market_caps[i][1]
        })

    return pd.DataFrame(rows)


def load_all_data():
    all_data = []

    for coin in COINS:
        print(f"Descargando {coin}...")
        df = fetch_coin_data(coin)

        if df is not None:
            all_data.append(df)

    final_df = pd.concat(all_data, ignore_index=True)

    # Ordenar
    final_df = final_df.sort_values(["coin", "timestamp"])

    # Guardar
    final_df.to_csv(RAW_DATA_PATH, index=False)

    print("Datos guardados en raw_data.csv")


if __name__ == "__main__":
    load_all_data()