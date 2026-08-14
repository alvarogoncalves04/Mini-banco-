# 03_consultas_olap.py
# CONSULTAS ANALÍTICAS SOBRE EL DATA WAREHOUSE (OLAP)

import sqlite3
import pandas as pd

def conectar_olap():
    """Conecta al Data Warehouse"""
    return sqlite3.connect('data/olap.db')

def ejecutar_consulta(query, descripcion):
    """Ejecuta una consulta y muestra el resultado"""
    print(f"\n📊 {descripcion}")
    print("-"*50)
    
    conn = conectar_olap()
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    print(df)
    print(f"\nTotal registros: {len(df)}")
    return df

def consultas_analiticas():
    """Ejecuta todas las consultas de negocio"""
    
    print("="*60)
    print("🔍 CONSULTAS ANALÍTICAS SOBRE DATA WAREHOUSE (OLAP)")
    print("="*60)
    
    # 1. Volumen total por tipo de transacción
    query1 = """
    SELECT 
        tipo,
        COUNT(*) as cantidad,
        SUM(monto_usd) as total_usd,
        AVG(monto_usd) as promedio_usd
    FROM transacciones_olap
    GROUP BY tipo
    ORDER BY total_usd DESC
    """
    ejecutar_consulta(query1, "1. VOLUMEN POR TIPO DE TRANSACCIÓN")
    
    # 2. Top 10 clientes con más movimientos
    query2 = """
    SELECT 
        cliente,
        COUNT(*) as transacciones,
        SUM(monto_usd) as total_movido,
        AVG(monto_usd) as promedio
    FROM transacciones_olap
    GROUP BY cliente
    ORDER BY total_movido DESC
    LIMIT 10
    """
    ejecutar_consulta(query2, "2. TOP 10 CLIENTES CON MÁS MOVIMIENTOS")
    
    # 3. Análisis de países de riesgo
    query3 = """
    SELECT 
        pais,
        COUNT(*) as cantidad,
        SUM(monto_usd) as total_usd,
        CASE 
            WHEN pais IN ('Islas Caimán', 'Suiza', 'Panamá') THEN 'Riesgo'
            ELSE 'Normal'
        END as nivel_riesgo
    FROM transacciones_olap
    GROUP BY pais
    ORDER BY total_usd DESC
    """
    ejecutar_consulta(query3, "3. ANÁLISIS POR PAÍS (CON CLASIFICACIÓN DE RIESGO)")
    
    # 4. Transacciones sospechosas
    query4 = """
    SELECT 
        cliente,
        fecha,
        tipo,
        monto_usd,
        pais,
        es_pais_riesgo,
        categoria_monto
    FROM transacciones_olap
    WHERE es_sospechoso = 1
    ORDER BY monto_usd DESC
    LIMIT 20
    """
    ejecutar_consulta(query4, "4. TOP 20 TRANSACCIONES SOSPECHOSAS")
    
    # 5. Resumen general del Data Warehouse
    query5 = """
    SELECT 
        COUNT(*) as total_transacciones,
        SUM(monto_usd) as monto_total_usd,
        AVG(monto_usd) as monto_promedio,
        SUM(CASE WHEN es_sospechoso = 1 THEN 1 ELSE 0 END) as total_sospechosos,
        SUM(CASE WHEN es_pais_riesgo = 1 THEN 1 ELSE 0 END) as total_paises_riesgo,
        ROUND(100.0 * SUM(CASE WHEN es_sospechoso = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) as porcentaje_sospechosos
    FROM transacciones_olap
    """
    ejecutar_consulta(query5, "5. RESUMEN EJECUTIVO DEL DATA WAREHOUSE")
    
    # 6. Tendencia diaria (últimos 7 días)
    query6 = """
    SELECT 
        fecha,
        COUNT(*) as transacciones,
        SUM(monto_usd) as total_usd,
        SUM(CASE WHEN es_sospechoso = 1 THEN 1 ELSE 0 END) as sospechosos
    FROM transacciones_olap
    WHERE fecha >= date('now', '-7 days')
    GROUP BY fecha
    ORDER BY fecha DESC
    """
    ejecutar_consulta(query6, "6. TENDENCIA DIARIA (ÚLTIMOS 7 DÍAS)")

if __name__ == "__main__":
    consultas_analiticas()