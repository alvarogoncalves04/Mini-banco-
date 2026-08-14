# 01_generar_datos.py
# SIMULA EL SISTEMA OLTP DEL BANCO (donde se registran las transacciones diarias)

import sqlite3
import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta

# Configuración
fake = Faker('es_ES')  # Datos en español
NUM_TRANSACCIONES = 10000  # Solo 10,000 registros (MUY LIGERO)

# Listas de países y tipos de transacción
PAISES = ['Venezuela', 'Colombia', 'Panamá', 'México', 'España', 'EE.UU', 'Islas Caimán', 'Suiza']
TIPOS = ['Depósito', 'Retiro', 'Transferencia']

def generar_transacciones(n):
    """Genera n transacciones falsas"""
    transacciones = []
    
    for i in range(n):
        # Generar un cliente con nombre falso
        cliente = fake.name()
        
        # Fecha aleatoria en los últimos 30 días
        fecha = fake.date_between(start_date='-30d', end_date='today')
        
        # Monto aleatorio (entre 10 y 50,000)
        monto = round(random.uniform(10, 50000), 2)
        
        # Tipo de transacción
        tipo = random.choice(TIPOS)
        
        # País (con más peso a Venezuela)
        pais = random.choices(
            PAISES, 
            weights=[50, 10, 10, 10, 10, 5, 3, 2],  # Venezuela aparece más
            k=1
        )[0]
        
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
    conn = sqlite3.connect('data/oltp.db')
    
    # Crear tabla si no existe
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
    
    # Guardar DataFrame en la tabla
    df.to_sql('transacciones_oltp', conn, if_exists='replace', index=False)
    
    conn.close()
    print(f"✅ {len(df)} transacciones guardadas en OLTP (data/oltp.db)")

if __name__ == "__main__":
    print("🚀 Generando datos transaccionales (OLTP)...")
    
    # Generar datos
    df = generar_transacciones(NUM_TRANSACCIONES)
    
    # Mostrar primeras 5 filas
    print("\n📋 Ejemplo de datos generados:")
    print(df.head())
    
    # Guardar en OLTP
    guardar_en_oltp(df)
    
    print("\n🔍 Resumen de datos:")
    print(f"Total transacciones: {len(df)}")
    print(f"Tipos: {df['tipo'].unique()}")
    print(f"Países: {df['pais'].unique()}")
    print(f"Rango de montos: ${df['monto'].min():,.2f} - ${df['monto'].max():,.2f}")