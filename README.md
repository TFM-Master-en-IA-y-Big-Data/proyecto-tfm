# 📈 CryptoPredict - Sistema Inteligente de Análisis y Predicción de Criptomonedas

---

## 🎯 Objetivo

Desarrollar un sistema completo de análisis y predicción de criptomonedas que permita:

* Construir y procesar un dataset estructurado a partir de datos reales de mercado.
* Analizar el comportamiento histórico de criptomonedas.
* Generar variables predictivas basadas en análisis técnico.
* Entrenar modelos de Machine Learning para predicción de tendencias.
* Exponer el sistema mediante una API REST.
* Visualizar resultados en una interfaz web interactiva y dashboards analíticos.

El sistema está orientado inicialmente a criptomonedas, aunque es extensible a cualquier activo financiero.

Este proyecto no se limita al entrenamiento de un modelo, sino que implementa una arquitectura completa end-to-end de Data Engineering + Machine Learning + Backend + Frontend.

---

## 👥 Integrantes

* Cristian Cantero López
* Èric García Dalmases
* Jesús García Quesada
* Claudia Tello Calles

---

## 🧠 Estado del proyecto (MVP - Fase 2)

En la presente fase se dispone de una versión funcional inicial (MVP), orientada a validar la arquitectura técnica, la integración entre componentes y la viabilidad del sistema predictivo.

✅ Funcionalidades completadas

* Pipeline de datos completo:
    * Ingesta de datos históricos de criptomonedas.
    * Transformación, limpieza y validación de datos.
* Generación automática de features de análisis técnico:
    * RSI, medias móviles, volatilidad, entre otras.
* Sistema de Machine Learning:
    * Entrenamiento de modelos XGBoost.
    * Reentrenamiento con calibración de probabilidades.
    * Evaluación mediante métricas como accuracy y ROC-AUC.
* Backend funcional con FastAPI:
    * Endpoints para consulta de datos y predicciones.
* Frontend web conectado a la API:
    * Interfaz gráfica para visualización de resultados.
* Dashboard analítico adicional:
    * Visualización de tendencias y análisis exploratorio.

---

## ⚠️ Funcionalidades parcialmente implementadas

* Uso de dataset reducido (~155 registros reales):
    * Válido para pruebas de lógica, no representativo de entorno productivo.
* Modelo predictivo en entorno controlado:
    * Pendiente de validación con datos en tiempo real.
* Interfaz de usuario funcional pero básica:
    * Sin sistema de login ni personalización avanzada.
* Pipeline parcialmente automatizado:
    * Algunos procesos se ejecutan de forma manual.

---

## 🚀 Aspectos pendientes (Fase 3)

* Ampliación del dataset hasta ~9.000 registros.
* Automatización completa del pipeline (ETL + ML).
* Reentrenamiento periódico del modelo.
* Mejora del sistema predictivo en tiempo real.
* Optimización del frontend (UX/UI + nuevas visualizaciones).
* Despliegue en entorno productivo.
* Refuerzo de seguridad, escalabilidad y monitorización.

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

4. Ejecución del sistema (orden recomendado):

Terminal 1 - Pipeline + modelo ML

```
python src/main.py
```

Este proceso:

* Ingesta datos.
* Genera features.
* Entrena modelo.
* Guarda modelo en disco.

Terminal 2 - Backend (API FastAPI)

```
python -m uvicorn src.backend.main:app --reload
```

📍 Disponible en: http://127.0.0.1:8000

Terminal 3 - Frontend

```
cd src/frontend
python -m http.server 8080
```

📍 Disponible en: http://127.0.0.1:8080

5. Dashboard analítico:

El sistema incluye un dashboard adicional generado automáticamente:

```
python src/reports/create_dashboard.py
```

Esto genera:

```
src/frontend/dashboard_crypto.html
```

📍 Acceso: http://127.0.0.1:8080/dashboard_crypto.html

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
├── .requiremnts.txt
└── README.md
```

Cada módulo será desarrollado de manera independiente pero coordinada, siguiendo buenas prácticas de control de versiones mediante ramas:

* `main` → versión estable.
* `develop` → integración de funcionalidades.
* `feature/*` → desarrollo individual de tareas.

## 📌 Nota final

Este sistema representa un **MVP funcional completo de un sistema de predicción financiera end-to-end**, integrando ingesta de datos, pipeline, machine learning, backend y frontend en una única arquitectura modular.