# 02_etl_pipeline.py
# PIPELINE ETL: Extraer → Transformar → Cargar

import sqlite3
import pandas as pd
from datetime import datetime
import random

# ============================================
# 1. EXTRACCIÓN (E)
# ============================================
def extraer_de_oltp():
    conn = sqlite3.connect('data/oltp.db')
    df = pd.read_sql_query("SELECT * FROM transacciones_oltp", conn)
    conn.close()
    print(f"📤 Extraídos {len(df)} registros de OLTP")
    return df

# ============================================
# 2. TRANSFORMACIÓN (T)
# ============================================
def transformar_datos(df):
    print("🔄 Transformando datos con reglas de negocio...")
    df_clean = df.copy()
    
    # 1. Limpiar nombres
    df_clean['cliente'] = df_clean['cliente'].str.strip()
    
    # 2. Calcular monto en dólares
    TASA_CAMBIO = 40
    df_clean['monto_usd'] = round(df_clean['monto'] / TASA_CAMBIO, 2)
    
    # 3. Clasificar por monto
    def clasificar_monto(monto):
        if monto < 1000:
            return 'Bajo'
        elif monto < 10000:
            return 'Medio'
        else:
            return 'Alto'
    df_clean['categoria_monto'] = df_clean['monto'].apply(clasificar_monto)
    
    # 4. Detectar países de riesgo
    PAISES_RIESGO = ['Islas Caimán', 'Suiza', 'Panamá']
    df_clean['es_pais_riesgo'] = df_clean['pais'].isin(PAISES_RIESGO)
    
    # 5. Hora aleatoria
    random.seed(42)
    df_clean['hora'] = [random.randint(0, 23) for _ in range(len(df_clean))]
    
    # ============================================
    # REGLAS DE NEGOCIO (MÁS SENSIBLES)
    # ============================================
    
    # 6. Velocidad: Más de 3 transacciones el mismo día (más sensible)
    conteo_por_dia = df_clean.groupby(['cliente', 'fecha']).size().reset_index(name='transacciones_dia')
    df_clean = df_clean.merge(conteo_por_dia, on=['cliente', 'fecha'], how='left')
    df_clean['excede_velocidad'] = df_clean['transacciones_dia'] > 3
    
    # 7. Smurfing: Depósitos entre $8,000 y $10,000 en el mismo día
    df_clean['es_estructuracion'] = (
        (df_clean['tipo'] == 'Depósito') & 
        (df_clean['monto'] >= 8000) & 
        (df_clean['monto'] <= 10000)
    )
    estructuracion_por_dia = df_clean[df_clean['es_estructuracion']].groupby(
        ['cliente', 'fecha']
    ).size().reset_index(name='depositos_estructurados')
    df_clean = df_clean.merge(estructuracion_por_dia, on=['cliente', 'fecha'], how='left')
    df_clean['depositos_estructurados'] = df_clean['depositos_estructurados'].fillna(0)
    df_clean['es_smurfing'] = df_clean['depositos_estructurados'] >= 2
    
    # 8. Horario de riesgo (2am - 5am)
    df_clean['es_horario_riesgo'] = df_clean['hora'].between(2, 5)
    
    # ============================================
    # CLASIFICACIÓN FINAL: ¿ES SOSPECHOSO? (REGLAS MÁS SENSIBLES)
    # ============================================
    def es_sospechoso(row):
        if row['tipo'] == 'Transferencia' and row['monto_usd'] > 3000:  # ANTES: 5000
            return 1
        if row['es_pais_riesgo'] and row['monto_usd'] > 2000:  # ANTES: 3000
            return 1
        if row['tipo'] == 'Depósito' and row['monto_usd'] > 5000:  # ANTES: 10000
            return 1
        if row['excede_velocidad']:
            return 1
        if row['es_smurfing']:
            return 1
        if row['es_horario_riesgo'] and row['monto_usd'] > 1000:  # ANTES: 2000
            return 1
        return 0
    
    df_clean['es_sospechoso'] = df_clean.apply(es_sospechoso, axis=1)
    
    # ============================================
    # RESULTADOS
    # ============================================
    print(f"✅ Transformación completada")
    print(f"   - Sospechosos: {df_clean['es_sospechoso'].sum()}")
    print(f"   - Exceso velocidad: {df_clean['excede_velocidad'].sum()}")
    print(f"   - Smurfing: {df_clean['es_smurfing'].sum()}")
    print(f"   - Horario riesgo: {df_clean['es_horario_riesgo'].sum()}")
    
    return df_clean

# ============================================
# 3. CARGA (L)
# ============================================
def cargar_en_olap(df):
    print("📥 Cargando en Data Warehouse (OLAP)...")
    conn = sqlite3.connect('data/olap.db')
    
    conn.execute('''
    CREATE TABLE IF NOT EXISTS transacciones_olap (
        id INTEGER PRIMARY KEY,
        cliente TEXT,
        fecha TEXT,
        monto REAL,
        tipo TEXT,
        pais TEXT,
        monto_usd REAL,
        categoria_monto TEXT,
        es_pais_riesgo INTEGER,
        es_sospechoso INTEGER,
        hora INTEGER,
        excede_velocidad INTEGER,
        es_smurfing INTEGER,
        es_horario_riesgo INTEGER,
        fecha_procesamiento TEXT
    )
    ''')
    
    df.to_sql('transacciones_olap', conn, if_exists='replace', index=False)
    conn.close()
    print(f"✅ {len(df)} registros cargados en OLAP")

# ============================================
# EJECUTAR
# ============================================
def ejecutar_etl():
    print("="*60)
    print("🚀 PIPELINE ETL")
    print("="*60)
    df_raw = extraer_de_oltp()
    df_clean = transformar_datos(df_raw)
    cargar_en_olap(df_clean)
    print("\n✅ PIPELINE ETL COMPLETADO")
    print("="*60)

if __name__ == "__main__":
    ejecutar_etl()