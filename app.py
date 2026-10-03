import streamlit as st
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(layout="wide", page_title="Dashboard Departamento", page_icon="📊")

# --- ESTILO BONITO ---
st.markdown("""
<style>
    .metric-card {background-color: #f0f2f6; padding: 20px; border-radius: 10px;}
    h1 {color: #0d47a1;}
</style>
""", unsafe_allow_html=True)

st.title("📊 DASHBOARD DEPARTAMENTO - DADOS KOBO LIVE")
st.caption("Atualiza automaticamente a cada 60 segundos | Ligado ao KoboCollect")

TOKEN = "961a037d2ce73679325a3fd54ed89c423e7d2de3"
FORM_ID = "a3jNwETyGCEhGxwFP9YsTA"
URL = f"https://kf.kobotoolbox.org/api/v2/assets/{FORM_ID}/data.json"

@st.cache_data(ttl=60)
def carregar():
    headers = {"Authorization": f"Token {TOKEN}"}
    r = requests.get(URL, headers=headers)
    if r.status_code != 200:
        return pd.DataFrame()
    df = pd.DataFrame(r.json().get('results', []))
    return df

df_raw = carregar()

if df_raw.empty:
    st.warning("Sem dados ainda.")
    st.stop()

# Limpar e organizar só o que importa
df = pd.DataFrame()
df['Reparticao'] = df_raw['Reparticao']
df['Pessoal'] = pd.to_numeric(df_raw['Pessoal'], errors='coerce')
df['Ano'] = pd.to_numeric(df_raw['Ano'], errors='coerce')
df['Actividades'] = pd.to_numeric(df_raw['Actividades'], errors='coerce')
df['Data'] = pd.to_datetime(df_raw['start']).dt.date

# --- SIDEBAR FILTROS ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1828/1828919.png", width=80)
st.sidebar.header("Filtros")
rep_filtro = st.sidebar.multiselect("Filtrar Repartição", options=sorted(df['Reparticao'].unique()), default=sorted(df['Reparticao'].unique()))
ano_filtro = st.sidebar.multiselect("Filtrar Ano", options=sorted(df['Ano'].unique()), default=sorted(df['Ano'].unique()))

df_f = df[(df['Reparticao'].isin(rep_filtro)) & (df['Ano'].isin(ano_filtro))]

# --- KPIs ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("👥 Total Pessoal", int(df_f['Pessoal'].sum()))
col2.metric("📝 Total Actividades", int(df_f['Actividades'].sum()))
col3.metric("🏢 Repartições", df_f['Reparticao'].nunique())
col4.metric("📋 Registos", len(df_f))

st.divider()

# --- GRAFICOS ---
c1, c2 = st.columns(2)
with c1:
    fig1 = px.bar(df_f.groupby('Reparticao', as_index=False).sum(numeric_only=True), 
                  x='Reparticao', y='Actividades', color='Reparticao',
                  title="Actividades por Repartição", text_auto=True)
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    fig2 = px.pie(df_f, names='Reparticao', values='Pessoal', title="Distribuição de Pessoal por Repartição", hole=0.5)
    st.plotly_chart(fig2, use_container_width=True)

c3, c4 = st.columns(2)
with c3:
    fig3 = px.bar(df_f.groupby('Ano', as_index=False).sum(numeric_only=True), x='Ano', y='Pessoal', title="Evolução Pessoal por Ano")
    st.plotly_chart(fig3, use_container_width=True)
with c4:
    fig4 = px.bar(df_f, x='Reparticao', y='Pessoal', color='Ano', barmode='group', title="Pessoal por Repartição e Ano")
    st.plotly_chart(fig4, use_container_width=True)

st.subheader("📄 Tabela Detalhada (Live)")
st.dataframe(df_f, use_container_width=True)

st.download_button("📥 Baixar Excel Filtrado", df_f.to_csv(index=False).encode('utf-8'), "base_departamento.csv", "text/csv")

if st.sidebar.button("🔄 Atualizar Agora"):
    st.cache_data.clear()
    st.rerun()
