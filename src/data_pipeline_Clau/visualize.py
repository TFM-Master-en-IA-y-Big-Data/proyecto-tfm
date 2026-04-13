import pandas as pd  # Esta es la forma correcta
import matplotlib.pyplot as plt
import seaborn as sns
import os

def generar_grafica():
    print("📊 Generando visualización de datos...")
    
    ruta_input = "data/processed/crypto_prices_clean.parquet"
    
    if not os.path.exists(ruta_input):
        print("❌ No se encuentran los datos procesados. Ejecuta primero transform.py")
        return

    # 1. Cargar datos
    df = pd.read_parquet(ruta_input)
    
    # 2. Configurar estilo
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 6))
    
    # 3. Crear gráfica de barras para comparar precios
    # Usamos una escala logarítmica porque el precio de BTC es mucho más alto que el de ETH
    ax = sns.barplot(x='coin_id', y='usd', data=df, palette='viridis')
    
    # Añadir etiquetas de precio encima de las barras
    for p in ax.patches:
        ax.annotate(f'${p.get_height():,.2f}', 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha = 'center', va = 'center', 
                    xytext = (0, 9), 
                    textcoords = 'offset points')

    plt.title('Comparativa de Precios Actuales: BTC vs ETH', fontsize=15)
    plt.xlabel('Criptomoneda', fontsize=12)
    plt.ylabel('Precio (USD)', fontsize=12)
    
    # 4. Guardar la gráfica
    os.makedirs("outputs", exist_ok=True)
    plt.savefig("outputs/comparativa_precios.png")
    
    print("✅ Gráfica generada con éxito en: outputs/comparativa_precios.png")
    plt.show() # Esto abrirá una ventana con la imagen

if __name__ == "__main__":
    generar_grafica()
