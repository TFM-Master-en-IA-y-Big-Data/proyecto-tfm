# 📈 CryptoPredict - Sistema Inteligente de Análisis y Predicción de Criptomonedas

---

## 🎯 Objetivo

CryptoPredict es un sistema end-to-end de análisis y predicción de criptomonedas que integra Data Engineering, Machine Learning, Backend y Frontend en una única arquitectura modular.

Desarrollar un sistema completo de análisis y predicción de criptomonedas que permita:

* Ingerir datos reales de mercado (OHLCV y capitalización).
* Procesar y transformar grandes volúmenes de información financiera.
* Generar variables de análisis técnico automáticamente.
* Entrenar modelos predictivos basados en Machine Learning.
* Servir predicciones mediante una API REST.
* Visualizar resultados mediante una interfaz web y dashboards analíticos.
* Automatizar todo el ciclo de vida del dato y del modelo.

El sistema está orientado inicialmente a criptomonedas, aunque es extensible a cualquier activo financiero.

---

## 👥 Integrantes

* Cristian Cantero López
* Èric García Dalmases
* Jesús García Quesada
* Claudia Tello Calles

---

## 🧠 Estado del proyecto (Entrega TFM - v1.0.0)

El proyecto ha evolucionado desde un MVP funcional hasta una **plataforma completa de predicción financiera automatizada**.

✅ Funcionalidades completadas

* Pipeline de datos completo:
    * Ingesta de datos de Binance y CoinGecko.
    * Limpieza, transformación y validación.
    * Generación de features técnicas (RSI, volatilidad, medias móviles, etc.).
    * Dataset final de 42.920 observaciones válidas.
* Sistema de Machine Learning:
    * Entrenamiento de modelos **XGBoost**.
    * Validación cruzada temporal (TimeSeriesSplit).
    * Reentrenamiento automático semanal.
    * Evaluación con métricas globales y por criptomoneda.
* Backend:
    * API REST desarrollada con **FastAPI**.
    * Endpoints para predicción y consulta de datos.
* Frontend:
    * Interfaz web conectada a la API.
    * Visualización de predicciones y tendencias.
* Dashboard analítico:
    * Análisis de hasta 100 criptomonedas.
    * Visualización exploratoria integrada.
* Sistema de autenticación:
    * Registro e inicio de sesión con **Firebase Authentication**.
    * Persistencia de usuarios en Firestore.

---

## 🚀 Mejoras respecto a la fase MVP

* 📊 Incremento del dataset de **155 → 42.920 registros**.
* ⚙️ Automatización completa del pipeline de datos y ML.
* 🔁 Reentrenamiento periódico del modelo sin intervención manual.
* 📈 Integración del dashboard dentro de la aplicación principal.
* 🧹 Mejora del tratamiento de datos (nulos, duplicados, coherencia temporal).
* 🧠 Validación cruzada temporal para evitar data leakage.
* 🧩 Modularización del código y separación por responsabilidades.

---

## ⚠️ Limitaciones actuales

* Ejecución en entorno local (no productivo).
* Dependencia de APIs externas (CoinGecko, Binance).
* Ventana temporal fija de 365 días (decisión de diseño).
* No se ha implementado escalado distribuido.
* No dispone de sistema de alertas en tiempo real.

---

## 🏗️ Arquitectura resumida

El sistema sigue una arquitectura modular compuesta por:

* Data Layer: APIs externas → Data Lake (Parquet).
* Data Pipeline: Procesamiento con Spark + validación.
* ML Layer: Modelo XGBoost con validación temporal.
* Backend: FastAPI (REST API)
* Frontend: Interfaz web para consulta de predicciones.
* BI Layer: Dashboards para análisis histórico y métricas.

Flujo general:

```
APIs Externas → Data Lake → Pipeline → ML → API (Backend) → Frontend / Dashboard
```

---

## ⚙️ Automatización del sistema

El sistema implementa un sistema de automatización completo basado en Python sin dependencias externas como Airflow o Docker.

### 🧠 Scripts principales

- `setup.py`  
  Inicializa el sistema completo:
  - Ingesta inicial de datos
  - ETL completo
  - Entrenamiento inicial del modelo
  - Arranque backend y frontend

- `scheduler.py`  
  Orquestador de procesos automatizados:
  - Pipeline diario de datos
  - Pipeline semanal de reentrenamiento
  - Ejecución continua en segundo plano

- `start_all.py`  
  Script principal de ejecución:
  - Ejecuta `setup.py`
  - Inicia `scheduler.py`

---

### 🔁 Pipelines automatizados

#### 📅 Pipeline diario (1:00 AM)

- Ingesta de nuevos datos (Binance + CoinGecko).
- Transformación y limpieza.
- Validación de calidad.
- Generación de features con Spark.

---

#### 📅 Pipeline semanal (Lunes 3:00 AM)

- Reentrenamiento del modelo XGBoost.
- Evaluación del modelo.
- Exportación de métricas y predicciones.

---

### 📦 Versionado del modelo

Cada reentrenamiento genera:

- `model.pkl` → modelo activo.
- `model_YYYY-MM-DD.pkl` → versión histórica.

Esto permite trazabilidad y comparación de evolución del modelo.

---

## 📊 Monitorización

El sistema incluye mecanismos completos de observabilidad:

### 📝 Logging estructurado

- Logs por etapa: `[INGEST]`, `[TRANSFORM]`, `[VALIDATE]`, `[FEATURES]`, `[RETRAIN]`, `[EVALUATE]`
- Ficheros separados por día.
- Registro de errores con stack traces.

---

### 🧪 Validación de datos

- Detección de duplicados.
- Control de valores nulos.
- Validación de coherencia de precios.
- Control de cobertura temporal.

---

### 📉 Métricas del modelo

- MAE, RMSE, R² global.
- Validación temporal (holdout 80/20).
- Cross-validation temporal (5 folds).
- Métricas por criptomoneda.
- Importancia de variables.

---

## 🚀 Cómo ejecutar el sistema

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

4. Ejecución del sistema completo:

```
python start_all.py
```

Esto ejecuta:

1. Inicialización del sistema (`setup.py`).
2. Arranque del backend y del frontend.
3. Activación del scheduler automático (`scheduler.py`).

La aplicación, una vez lanzado el script, está disponible desde: `http://localhost:8080`

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
* XGBoost
* Pandas
* Seaborn / Matplotlib

**Base de Datos**

* Data Lake (Parquet)
* NoSQL (Firebase)

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
├── logs/                 # Logs del sistema
├── notebooks/            # Notebooks de exploración de datos
├── outputs/              # Resultados del sistema
├── src/                  # Código fuente (modelos, API, lógica del sistema)
├── .gitignore
├── requirements.txt
├── scheduler.py          # Automatización del pipeline diario y reentrenamiento semanal
├── setup.py              # Inicialización del sistema (ETL, modelo, backend y frontend)
├── start_all.py          # Script principal que lanza setup y scheduler
└── README.md
```

---

## 📌 Buenas prácticas aplicadas

* Código modular y limpio.
* Separación de responsabilidades.
* Pipeline automatizado.
* Versionado de modelos.
* Logging estructurado.
* Validación de datos robusta.
* Arquitectura end-to-end.

---

## 🏁 Versión final

📦 Release: `v1.0.0`.
📅 Estado: Entrega final TFM.
🚀 Tipo: Sistema completo end-to-end (Data + ML + Backend + Frontend).

--- 

## 📌 Nota final

CryptoPredict representa una arquitectura completa de sistema inteligente aplicada al ámbito financiero, integrando desde la ingesta de datos hasta la generación de predicciones automatizadas, con un enfoque realista de ingeniería de datos y machine learning en producción.