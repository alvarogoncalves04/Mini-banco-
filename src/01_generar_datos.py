# 01_generar_datos.py
# SIMULA EL SISTEMA OLTP DEL BANCO

import sqlite3
import pandas as pd
from faker import Faker
import random
from datetime import datetime

# ============================================
# CONFIGURACIÓN
# ============================================
fake = Faker('es_ES')
NUM_TRANSACCIONES = 50000

PAISES = ['Venezuela', 'Colombia', 'Panamá', 'México', 'España', 'EE.UU', 'Islas Caimán', 'Suiza']
TIPOS = ['Depósito', 'Retiro', 'Transferencia']

# ============================================
# FUNCIONES
# ============================================
def generar_transacciones(n):
    """
    Genera n transacciones falsas.
    El 60% de los casos serán de alto riesgo (montos altos, países de riesgo).
    """
    transacciones = []
    
    for i in range(n):
        cliente = fake.name()
        fecha = fake.date_between(start_date='-30d', end_date='today')
        
        # 60% de probabilidad de ser sospechoso
        es_riesgo = random.random() < 0.60
        
        if es_riesgo:
            # Caso SOSPECHOSO: montos altos, países de riesgo
            monto = round(random.uniform(15000, 100000), 2)
            pais = random.choices(
                PAISES, 
                weights=[15, 10, 30, 5, 5, 5, 20, 10],
                k=1
            )[0]
            tipo = random.choices(
                TIPOS,
                weights=[20, 10, 70],
                k=1
            )[0]
        else:
            # Caso NORMAL: montos bajos, países seguros
            monto = round(random.uniform(10, 2000), 2)
            pais = random.choices(
                PAISES, 
                weights=[70, 10, 3, 10, 5, 2, 0, 0],
                k=1
            )[0]
            tipo = random.choice(['Depósito', 'Retiro'])
        
        transacciones.append({
            'id': i + 1,
            'cliente': cliente,
            'fecha': fecha.strftime('%Y-%m-%d'),
            'monto': monto,
            'tipo': tipo,
            'pais': pais
        })
    
    return pd.DataFrame(transacciones)

def guardar_en_oltp(df):
    """Guarda los datos en la base de datos OLTP"""
    import os
    os.makedirs('data', exist_ok=True)
    
    conn = sqlite3.connect('data/oltp.db')
    
    conn.execute('''
    CREATE TABLE IF NOT EXISTS transacciones_oltp (
        id INTEGER PRIMARY KEY,
        cliente TEXT,
        fecha TEXT,
        monto REAL,
        tipo TEXT,
        pais TEXT
    )
    ''')
    
    df.to_sql('transacciones_oltp', conn, if_exists='replace', index=False)
    conn.close()
    
    print(f"✅ {len(df)} transacciones guardadas en OLTP (data/oltp.db)")

# ============================================
# EJECUCIÓN
# ============================================
if __name__ == "__main__":
    print("🚀 Generando datos transaccionales (OLTP)...")
    print(f"📊 Generando {NUM_TRANSACCIONES} transacciones...")
    
    df = generar_transacciones(NUM_TRANSACCIONES)
    
    print("\n📋 Ejemplo de datos generados:")
    print(df.head())
    
    guardar_en_oltp(df)
    
    print("\n🔍 Resumen de datos:")
    print(f"Total transacciones: {len(df)}")
    print(f"Tipos: {df['tipo'].unique()}")
    print(f"Países: {df['pais'].unique()}")
    print(f"Rango de montos: ${df['monto'].min():,.2f} - ${df['monto'].max():,.2f}")
    print(f"Monto promedio: ${df['monto'].mean():,.2f}")