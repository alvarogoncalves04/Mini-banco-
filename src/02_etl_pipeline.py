# 02_etl_pipeline.py (VERSIÓN MEJORADA)
import sqlite3
import pandas as pd
from datetime import datetime

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
# 2. TRANSFORMACIÓN (T) MEJORADA
# ============================================
def transformar_datos(df):
    print("🔄 Transformando datos con nuevas reglas...")
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
    
    # 5. Agregar hora de la transacción (para regla de horario)
    # Generamos una hora aleatoria entre 0 y 23 para simular el horario
    import random
    random.seed(42)  # Para que sea reproducible
    df_clean['hora'] = [random.randint(0, 23) for _ in range(len(df_clean))]
    
    # ============================================
    # NUEVAS REGLAS DE NEGOCIO
    # ============================================
    
    # 6. REGLA DE VELOCIDAD: Más de 5 transacciones el mismo día
    # Agrupamos por cliente y fecha para contar transacciones
    conteo_por_dia = df_clean.groupby(['cliente', 'fecha']).size().reset_index(name='transacciones_dia')
    df_clean = df_clean.merge(conteo_por_dia, on=['cliente', 'fecha'], how='left')
    df_clean['excede_velocidad'] = df_clean['transacciones_dia'] > 5
    
    # 7. REGLA DE ESTRUCTURACIÓN (Smurfing): Depósitos entre $8,000 y $10,000 en el mismo día
    # Identificamos depósitos en ese rango
    df_clean['es_estructuracion'] = (
        (df_clean['tipo'] == 'Depósito') & 
        (df_clean['monto'] >= 8000) & 
        (df_clean['monto'] <= 10000)
    )
    # Contamos cuántos depósitos estructurados hizo cada cliente por día
    estructuracion_por_dia = df_clean[df_clean['es_estructuracion']].groupby(
        ['cliente', 'fecha']
    ).size().reset_index(name='depositos_estructurados')
    df_clean = df_clean.merge(estructuracion_por_dia, on=['cliente', 'fecha'], how='left')
    df_clean['depositos_estructurados'] = df_clean['depositos_estructurados'].fillna(0)
    df_clean['es_smurfing'] = df_clean['depositos_estructurados'] >= 3
    
    # 8. REGLA DE HORARIO: Transacciones entre 2 AM y 5 AM
    df_clean['es_horario_riesgo'] = df_clean['hora'].between(2, 5)
    
    # ============================================
    # REGLA PRINCIPAL: ES SOSPECHOSO (combina todas)
    # ============================================
    def es_sospechoso(row):
        # Reglas anteriores
        if row['tipo'] == 'Transferencia' and row['monto_usd'] > 5000:
            return 1
        if row['es_pais_riesgo'] and row['monto_usd'] > 3000:
            return 1
        if row['tipo'] == 'Depósito' and row['monto_usd'] > 10000:
            return 1
        
        # NUEVAS REGLAS
        if row['excede_velocidad']:
            return 1
        if row['es_smurfing']:
            return 1
        if row['es_horario_riesgo'] and row['monto_usd'] > 2000:
            return 1
        
        return 0
    
    df_clean['es_sospechoso'] = df_clean.apply(es_sospechoso, axis=1)
    
    # ============================================
    # RESULTADOS DE LAS NUEVAS REGLAS
    # ============================================
    print(f"✅ Transformación completada")
    print(f"   - Transacciones sospechosas: {df_clean['es_sospechoso'].sum()}")
    print(f"   - Clientes con exceso de velocidad: {df_clean[df_clean['excede_velocidad']]['cliente'].nunique()}")
    print(f"   - Transacciones en horario de riesgo: {df_clean['es_horario_riesgo'].sum()}")
    print(f"   - Posible smurfing detectado: {df_clean['es_smurfing'].sum()}")
    
    return df_clean

# ============================================
# 3. CARGA (L)
# ============================================
def cargar_en_olap(df):
    print("📥 Cargando en Data Warehouse (OLAP)...")
    conn = sqlite3.connect('data/olap.db')
    
    # Crear tabla con nuevas columnas
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
    print("🚀 PIPELINE ETL MEJORADO")
    print("="*60)
    df_raw = extraer_de_oltp()
    df_clean = transformar_datos(df_raw)
    cargar_en_olap(df_clean)
    print("\n✅ PIPELINE ETL COMPLETADO")
    print("="*60)

if __name__ == "__main__":
    ejecutar_etl()