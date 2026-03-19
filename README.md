# 📈 CryptoPredict - Sistema Inteligente de Análisis y Predicción de Criptomonedas

---

## 🎯 Objetivo

Desarrollar un sistema completo que:

* Construya un dataset estructurado de criptomonedas.
* Analice su comportamiento histórico.
* Prediga probabilísticamente su evolución.
* Exponga el modelo mediante una API.
* Muestre los resultados en una interfaz web interactiva.

Aplicado inicialmente a criptomonedas como **Bitcoin (BTC)** y **Ethereum (ETH)**, entre otras.

El proyecto no consiste únicamente en entrenar un modelo, sino en diseñar un sistema completo de análisis y predicción financiera combinando Big Data, Machine Learning y desarrollo web.

---

## 👥 Integrantes

* Cristian Cantero López
* Èric García Dalmases
* Jesús García Quesada
* Claudia Tello Calles

---

## 🏗️ Arquitectura resumida

El sistema sigue una arquitectura modular compuesta por:

* Data Layer: Ingesta de datos desde APIs (CoinGecko, Binance) y almacenamiento en Data Lake (Parquet).
* Data Pipeline: Procesamiento con Apache Spark y orquestación con Airflow (DAG diario ETL + DAG semanal ML).
* ML Layer: Modelos de clasificación binaria para predicción de tendencias.
* Backend (API REST): Exposición de predicciones y lógica de negocio mediante FastAPI.
* Frontend: Interfaz web para consulta de predicciones.
* BI Layer: Dashboards en Power BI para análisis histórico y métricas.

Flujo general:

APIs Externas → Data Lake / Pipeline de Datos → ML → API (Backend) → Frontend / Dashboard

---

## 🚀 Cómo ejecutar (WIP)

⚠️ El proyecto se encuentra en desarrollo. Estos pasos son provisionales.

1. Clonar el repositorio:

```
git clone https://github.com/tu-repo/crypto-predict.git
cd crypto-predict
```

2. Crear el entorno virtual:

```
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Instalar dependencias:

```
pip install -r requirements.txt
```

4. Ejecutar la API (cuando esté disponible):

```
uvicorn src.api.main:app --reload
```

5. (Opcional) Ejecutar pipelines:

* Airflow para DAGs de datos y ML.
* Scripts de Spark para procesamiento.

---

## ⚙️ Tecnologías

**Lenguajes**

* Python (Backend + Data) y JavaScript (Frontend)

**Frameworks**

* FastAPI
* Apache Airflow

**Librerías**

* PySpark
* Scikit-Learn
* Pandas
* Seaborn / Matplotlib

**Base de Datos**

* Data Lake (Parquet)
* SQL / NoSQL (Firebase)

**Herramientas**

* Power BI
* GitHub

---

## 🧱 Estructura y Organización del Repositorio

El repositorio se organizará de forma modular siguiendo la arquitectura del sistema:

```
crypto-predict/
│
├── data/                 # Dataset, scripts de generación y procesamiento de datos
├── docs/                 # Documentación técnica y memoria del proyecto
├── environment/          # Entorno virtual de Python
├── src/                  # Código fuente (modelos, API, lógica del sistema)
├── .gitignore
└── README.md
```

Cada módulo será desarrollado de manera independiente pero coordinada, siguiendo buenas prácticas de control de versiones mediante ramas:

* `main` → versión estable.
* `develop` → integración de funcionalidades.
* `feature/*` → desarrollo individual de tareas.