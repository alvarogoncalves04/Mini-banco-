# 🏦 Mini Banco - Dashboard de Monitoreo Bancario

## 📌 Descripción
Proyecto que simula un sistema de monitoreo bancario para la detección de transacciones sospechosas (AML/FT). Incluye:

- Generación de datos transaccionales (OLTP)
- Pipeline ETL con reglas de negocio
- Data Warehouse (OLAP) para análisis
- Dashboard interactivo con Streamlit

## 🛠️ Tecnologías
- Python 3.x
- Pandas (manipulación de datos)
- SQLite (OLTP + OLAP)
- Streamlit (dashboard)
- Matplotlib (visualizaciones)

## 📁 Estructura del Proyecto
mini_banco/
├── data/

│ ├── oltp.db # Base de datos transaccional

│ └── olap.db # Data Warehouse

├── src/

│ ├── 01_generar_datos.py # Genera datos falsos

│ ├── 02_etl_pipeline.py # Pipeline ETL

│ ├── 03_consultas_olap.py # Consultas analíticas

│ └── 04_dashboard.py # Dashboard Streamlit

├── requirements.txt

└── README.md

📊 Reglas de Negocio Implementadas

-Montos superiores a $10,000 USD

-Transferencias internacionales a países de riesgo

-Depósitos fraccionados (smurfing) entre $8,000 y $10,000

-Más de 5 transacciones en el mismo día

-Transacciones en horario de riesgo (2am - 5am)

🔗 Demo

https://alvarogoncalves04-mini-banco.streamlit.app
