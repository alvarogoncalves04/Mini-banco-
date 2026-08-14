# 04_dashboard.py - VERSIÓN MEJORADA
import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Dashboard Bancario",
    page_icon="🏦",
    layout="wide"
)

st.title("🏦 Dashboard de Monitoreo Bancario")
st.markdown("---")

# ============================================
# CARGAR DATOS
# ============================================
def cargar_datos():
    conn = sqlite3.connect('data/olap.db')
    df = pd.read_sql_query("SELECT * FROM transacciones_olap", conn)
    conn.close()
    return df

df = cargar_datos()

# Convertir fecha a datetime
df['fecha'] = pd.to_datetime(df['fecha'])

# ============================================
# FILTROS LATERALES
# ============================================
st.sidebar.header("🔍 Filtros")

# Filtro de fechas
st.sidebar.subheader("📅 Rango de Fechas")
fecha_min = df['fecha'].min().date()
fecha_max = df['fecha'].max().date()
fecha_inicio = st.sidebar.date_input("Fecha Inicio", fecha_min, min_value=fecha_min, max_value=fecha_max)
fecha_fin = st.sidebar.date_input("Fecha Fin", fecha_max, min_value=fecha_min, max_value=fecha_max)

# Filtro por tipo
tipo = st.sidebar.multiselect(
    "Tipo de Transacción",
    options=df['tipo'].unique(),
    default=df['tipo'].unique()
)

# Filtro por país
pais = st.sidebar.multiselect(
    "País",
    options=df['pais'].unique(),
    default=df['pais'].unique()
)

# Filtro por sospechoso
sospechoso = st.sidebar.selectbox(
    "Mostrar",
    options=["Todos", "Solo Sospechosos", "Solo Normales"]
)

# Aplicar filtros
df_filtrado = df[
    (df['fecha'].dt.date >= fecha_inicio) &
    (df['fecha'].dt.date <= fecha_fin) &
    (df['tipo'].isin(tipo)) &
    (df['pais'].isin(pais))
]

if sospechoso == "Solo Sospechosos":
    df_filtrado = df_filtrado[df_filtrado['es_sospechoso'] == 1]
elif sospechoso == "Solo Normales":
    df_filtrado = df_filtrado[df_filtrado['es_sospechoso'] == 0]

# ============================================
# FILA 1: MÉTRICAS
# ============================================
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("📊 Total Transacciones", f"{len(df_filtrado):,}")
with col2:
    st.metric("💰 Monto Total", f"${df_filtrado['monto_usd'].sum():,.2f}")
with col3:
    st.metric("⚠️ Sospechosos", f"{df_filtrado['es_sospechoso'].sum():,}")
with col4:
    st.metric("🚀 Exceso Velocidad", f"{df_filtrado['excede_velocidad'].sum():,}")
with col5:
    st.metric("🌙 Horario Riesgo", f"{df_filtrado['es_horario_riesgo'].sum():,}")

st.markdown("---")

# ============================================
# FILA 2: GRÁFICOS
# ============================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Transacciones por Tipo")
    fig, ax = plt.subplots()
    df_tipo = df_filtrado.groupby('tipo').size()
    ax.bar(df_tipo.index, df_tipo.values, color=['#3498db', '#e74c3c', '#2ecc71'])
    ax.set_ylabel("Cantidad")
    st.pyplot(fig)
    plt.close()

with col2:
    st.subheader("⚠️ Sospechosos por Tipo")
    fig, ax = plt.subplots()
    df_sos = df_filtrado[df_filtrado['es_sospechoso'] == 1].groupby('tipo').size()
    if not df_sos.empty:
        ax.bar(df_sos.index, df_sos.values, color='#e74c3c')
        ax.set_ylabel("Cantidad de Sospechosos")
    else:
        ax.text(0.5, 0.5, "No hay sospechosos", ha='center', va='center')
    st.pyplot(fig)
    plt.close()

# ============================================
# FILA 3: TENDENCIA TEMPORAL
# ============================================
st.subheader("📈 Tendencia de Transacciones y Sospechosos")

fig, ax = plt.subplots(figsize=(12, 5))
df_tendencia = df_filtrado.groupby('fecha').agg(
    total=('id', 'count'),
    sospechosos=('es_sospechoso', 'sum')
).reset_index()

ax.plot(df_tendencia['fecha'], df_tendencia['total'], label='Total', marker='o', color='#2ecc71')
ax.plot(df_tendencia['fecha'], df_tendencia['sospechosos'], label='Sospechosos', marker='s', color='#e74c3c')
ax.set_xlabel("Fecha")
ax.set_ylabel("Cantidad")
ax.legend()
ax.grid(True, alpha=0.3)
plt.xticks(rotation=45)
st.pyplot(fig)
plt.close()

# ============================================
# FILA 4: TABLA
# ============================================
st.subheader("📋 Datos Filtrados")

columnas_mostrar = ['cliente', 'fecha', 'tipo', 'monto_usd', 'pais', 'es_sospechoso', 'excede_velocidad', 'es_smurfing', 'es_horario_riesgo']
df_mostrar = df_filtrado[columnas_mostrar].copy()

df_mostrar['es_sospechoso'] = df_mostrar['es_sospechoso'].map({0: '✅ Normal', 1: '🚨 Sospechoso'})
df_mostrar['excede_velocidad'] = df_mostrar['excede_velocidad'].map({0: '✅', 1: '🚨'})
df_mostrar['es_smurfing'] = df_mostrar['es_smurfing'].map({0: '✅', 1: '🚨'})
df_mostrar['es_horario_riesgo'] = df_mostrar['es_horario_riesgo'].map({0: '✅', 1: '🌙'})

st.dataframe(df_mostrar, use_container_width=True)

# ============================================
# DESCARGA
# ============================================
st.markdown("---")
if st.button("📥 Descargar datos filtrados (CSV)"):
    csv = df_filtrado.to_csv(index=False)
    st.download_button(
        label="Click para descargar",
        data=csv,
        file_name=f"reporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )