# 06_machine_learning.py
import sqlite3
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import StandardScaler
import joblib

def cargar_datos_olap():
    conn = sqlite3.connect('data/olap.db')
    df = pd.read_sql_query("SELECT * FROM transacciones_olap", conn)
    conn.close()
    return df

def preparar_datos(df):
    """Prepara los datos para el modelo"""
    
    # Seleccionar features para entrenamiento
    features = [
        'monto_usd',
        'hora',
        'es_pais_riesgo',
        'excede_velocidad',
        'es_smurfing',
        'es_horario_riesgo'
    ]
    
    # Variable objetivo (lo que queremos predecir)
    target = 'es_sospechoso'
    
    X = df[features].copy()
    y = df[target].copy()
    
    # Escalar datos numéricos
    scaler = StandardScaler()
    X['monto_usd'] = scaler.fit_transform(X[['monto_usd']])
    
    return X, y, scaler

def entrenar_modelos(X, y):
    """Entrena y compara 2 modelos"""
    
    # Dividir en entrenamiento (80%) y prueba (20%)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\n📊 Datos de entrenamiento: {len(X_train)} registros")
    print(f"📊 Datos de prueba: {len(X_test)} registros")
    print(f"📊 Sospechosos en entrenamiento: {y_train.sum()}")
    print(f"📊 Sospechosos en prueba: {y_test.sum()}")
    
    # Modelo 1: Regresión Logística
    print("\n" + "="*50)
    print("🔍 REGRESIÓN LOGÍSTICA")
    print("="*50)
    
    lr = LogisticRegression(random_state=42, max_iter=1000)
    lr.fit(X_train, y_train)
    y_pred_lr = lr.predict(X_test)
    
    print(f"Accuracy: {accuracy_score(y_test, y_pred_lr):.2%}")
    print(classification_report(y_test, y_pred_lr, target_names=['Normal', 'Sospechoso']))
    
    # Modelo 2: Random Forest
    print("\n" + "="*50)
    print("🌲 RANDOM FOREST")
    print("="*50)
    
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        class_weight='balanced'
    )
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    
    print(f"Accuracy: {accuracy_score(y_test, y_pred_rf):.2%}")
    print(classification_report(y_test, y_pred_rf, target_names=['Normal', 'Sospechoso']))
    
    # Importancia de features
    print("\n📌 IMPORTANCIA DE VARIABLES (Random Forest):")
    for feature, importance in zip(X.columns, rf.feature_importances_):
        print(f"  - {feature}: {importance:.2%}")
    
    # Guardar el mejor modelo
    joblib.dump(rf, 'modelo_rf.pkl')
    joblib.dump(scaler, 'scaler.pkl')
    print("\n✅ Modelo guardado: modelo_rf.pkl")
    
    return rf, scaler

def predecir_nueva_transaccion(monto_usd, hora, es_pais_riesgo, excede_velocidad, es_smurfing, es_horario_riesgo):
    """Predice si una nueva transacción es sospechosa"""
    
    modelo = joblib.load('modelo_rf.pkl')
    scaler = joblib.load('scaler.pkl')
    
    # Crear array con los datos
    datos = np.array([[
        monto_usd,
        hora,
        es_pais_riesgo,
        excede_velocidad,
        es_smurfing,
        es_horario_riesgo
    ]])
    
    # Escalar monto
    datos[0, 0] = scaler.transform([[monto_usd]])[0, 0]
    
    # Predecir
    prediccion = modelo.predict(datos)[0]
    probabilidad = modelo.predict_proba(datos)[0][1]
    
    return prediccion, probabilidad

if __name__ == "__main__":
    print("="*60)
    print("🤖 MACHINE LEARNING - DETECCIÓN DE FRAUDE")
    print("="*60)
    
    # Cargar datos
    df = cargar_datos_olap()
    print(f"📊 Datos cargados: {len(df)} registros")
    
    # Preparar
    X, y, scaler = preparar_datos(df)
    
    # Entrenar
    modelo, scaler = entrenar_modelos(X, y)
    
    # Prueba con una transacción nueva
    print("\n" + "="*50)
    print("🧪 PRUEBA CON NUEVA TRANSACCIÓN")
    print("="*50)
    
    resultado, prob = predecir_nueva_transaccion(
        monto_usd=12000,
        hora=3,
        es_pais_riesgo=1,
        excede_velocidad=0,
        es_smurfing=0,
        es_horario_riesgo=1
    )
    
    print(f"🔍 Transacción: $12,000 USD a las 3 AM desde país de riesgo")
    print(f"📊 Probabilidad de ser sospechosa: {prob:.2%}")
    print(f"🚨 Resultado: {'SOSPECHOSA' if resultado == 1 else 'NORMAL'}")