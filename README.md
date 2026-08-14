# 🏦 Mini Banco - Sistema de Monitoreo Bancario

## 📌 Descripción

Proyecto completo que simula un sistema de monitoreo bancario para la detección de transacciones sospechosas (AML/FT). Incluye:

- Generación de datos transaccionales (OLTP)
  
- Pipeline ETL con reglas de negocio
  
- Data Warehouse (OLAP) para análisis
  
- Dashboard interactivo con Streamlit
  
- Modelo de Machine Learning para detección de fraude
  
- Automatización de tareas programadas

## 🛠️ Tecnologías

- Python 3.x
  
- Pandas (manipulación de datos)
  
- SQLite (OLTP + OLAP)
  
- Streamlit (dashboard)
  
- Matplotlib (visualizaciones)
  
- Scikit-learn (Machine Learning)
  
- Schedule (automatización)


## 📁 Estructura del Proyecto

mini_banco/

├── data/

│ ├── oltp.db # Base de datos transaccional

│ └── olap.db # Data Warehouse

├── src/

│ ├── 01_generar_datos.py # Genera datos falsos

│ ├── 02_etl_pipeline.py # Pipeline ETL

│ ├── 03_consultas_olap.py # Consultas analíticas

│ ├── 04_dashboard.py # Dashboard Streamlit

│ ├── 05_automatizacion.py # Automatización ETL

│ └── 06_machine_learning.py # Modelo de ML

├── requirements.txt

└── README.md

## 📊 Reglas de Negocio Implementadas

- Montos superiores a $10,000 USD
  
- Transferencias internacionales a países de riesgo
  
- Depósitos fraccionados (smurfing) entre $8,000 y $10,000
  
- Más de 3 transacciones en el mismo día
  
- Transacciones en horario de riesgo (2am - 5am)

## 🤖 Machine Learning

- Modelo: Random Forest Classifier
  
- Precisión: >95% en datos de prueba
  
- Variables utilizadas: monto, hora, país de riesgo, velocidad, smurfing, horario
  
- Exportación del modelo para predicciones en tiempo real

## ⏰ Automatización

- Tareas programadas con `schedule`
  
- Ejecución automática del ETL a las 8:00 AM y 8:00 PM
  
- Envío de reportes por correo (simulado)
  
🔗 Demo

https://alvarogoncalves04-mini-banco.streamlit.app
