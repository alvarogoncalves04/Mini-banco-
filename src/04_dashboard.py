# 04_dashboard.py
# DASHBOARD INTERACTIVO CON STREAMLIT

import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# ============================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================
st.set_page_config(
    page_title="Dashboard Bancario",
    page_icon="🏦",
    layout="wide"
)

st.title("🏦 Dashboard de Monitoreo Bancario")
st.markdown("---")

# ============================================
# CARGAR DATOS DESDE OLAP
# ============================================
# @st.cache_data
def cargar_datos():
    conn = sqlite3.connect('data/olap.db')
    df = pd.read_sql_query("SELECT * FROM transacciones_olap", conn)
    conn.close()
    return df

df = cargar_datos()

# ============================================
# FILTROS LATERALES
# ============================================
st.sidebar.header("🔍 Filtros")

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
    "Mostrar solo sospechosos",
    options=["Todos", "Solo Sospechosos", "Solo Normales"]
)

# Aplicar filtros
df_filtrado = df[df['tipo'].isin(tipo) & df['pais'].isin(pais)]

if sospechoso == "Solo Sospechosos":
    df_filtrado = df_filtrado[df_filtrado['es_sospechoso'] == 1]
elif sospechoso == "Solo Normales":
    df_filtrado = df_filtrado[df_filtrado['es_sospechoso'] == 0]

# ============================================
# FILA 1: MÉTRICAS
# ============================================
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "📊 Total Transacciones",
        f"{len(df_filtrado):,}"
    )

with col2:
    st.metric(
        "💰 Monto Total",
        f"${df_filtrado['monto_usd'].sum():,.2f}"
    )

with col3:
    st.metric(
        "⚠️ Sospechosos",
        f"{df_filtrado['es_sospechoso'].sum():,}",
        delta=f"{df_filtrado['es_sospechoso'].sum() / len(df_filtrado) * 100:.1f}%" if len(df_filtrado) > 0 else "0%"
    )

with col4:
    st.metric(
        "🚀 Velocidad",
        f"{df_filtrado['excede_velocidad'].sum():,}"
    )

with col5:
    st.metric(
        "🌙 Horario Riesgo",
        f"{df_filtrado['es_horario_riesgo'].sum():,}"
    )

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
    df_sospechosos_tipo = df_filtrado[df_filtrado['es_sospechoso'] == 1].groupby('tipo').size()
    if not df_sospechosos_tipo.empty:
        ax.bar(df_sospechosos_tipo.index, df_sospechosos_tipo.values, color='#e74c3c')
        ax.set_ylabel("Cantidad de Sospechosos")
    else:
        ax.text(0.5, 0.5, "No hay sospechosos", ha='center', va='center')
    st.pyplot(fig)
    plt.close()

# ============================================
# FILA 3: GRÁFICOS
# ============================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Monto Promedio por País")
    fig, ax = plt.subplots()
    df_pais = df_filtrado.groupby('pais')['monto_usd'].mean().sort_values(ascending=False).head(10)
    ax.barh(df_pais.index, df_pais.values, color='#f39c12')
    ax.set_xlabel("Monto Promedio (USD)")
    st.pyplot(fig)
    plt.close()

with col2:
    st.subheader("🌙 Transacciones por Hora")
    fig, ax = plt.subplots()
    df_hora = df_filtrado.groupby('hora').size()
    ax.bar(df_hora.index, df_hora.values, color='#9b59b6')
    ax.axvspan(2, 5, alpha=0.2, color='red', label='Horario de Riesgo')
    ax.set_xlabel("Hora del Día")
    ax.set_ylabel("Cantidad")
    ax.legend()
    st.pyplot(fig)
    plt.close()

# ============================================
# FILA 4: TABLA DE DATOS
# ============================================
st.subheader("📋 Datos Filtrados")

# Mostrar solo columnas relevantes
columnas_mostrar = ['cliente', 'fecha', 'tipo', 'monto_usd', 'pais', 'es_sospechoso', 'excede_velocidad', 'es_smurfing', 'es_horario_riesgo']
df_mostrar = df_filtrado[columnas_mostrar].copy()

# Formatear columnas
df_mostrar['es_sospechoso'] = df_mostrar['es_sospechoso'].map({0: '✅ Normal', 1: '🚨 Sospechoso'})
df_mostrar['excede_velocidad'] = df_mostrar['excede_velocidad'].map({0: '✅', 1: '🚨'})
df_mostrar['es_smurfing'] = df_mostrar['es_smurfing'].map({0: '✅', 1: '🚨'})
df_mostrar['es_horario_riesgo'] = df_mostrar['es_horario_riesgo'].map({0: '✅', 1: '🌙'})

st.dataframe(df_mostrar, use_container_width=True)

# ============================================
# DESCARGA DE DATOS
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