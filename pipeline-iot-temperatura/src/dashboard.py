"""Dashboard Streamlit para explorar as views PostgreSQL."""
import os
import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT, ".env"))
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://iot_user:iot_senha_local@localhost:5432/iot_database",
)
engine = create_engine(DATABASE_URL)

st.set_page_config(page_title="Dashboard de Temperaturas IoT", page_icon="🌡️", layout="wide")
st.title("Dashboard de Temperaturas IoT")
st.caption("Leituras importadas do dataset público Temperature Readings: IoT Devices.")


@st.cache_data(ttl=60)
def load_view(view_name: str) -> pd.DataFrame:
    """Consulta somente views previamente autorizadas."""
    allowed = {
        "avg_temp_por_dispositivo",
        "leituras_por_hora",
        "temp_max_min_por_dia",
    }
    if view_name not in allowed:
        raise ValueError("View não permitida.")
    return pd.read_sql(f"SELECT * FROM {view_name}", engine)


try:
    media = load_view("avg_temp_por_dispositivo")
    horas = load_view("leituras_por_hora")
    diaria = load_view("temp_max_min_por_dia")

    a, b, c = st.columns(3)
    a.metric("Total de categorias/dispositivos", len(media))
    b.metric("Horas com registros", len(horas))
    c.metric("Dias analisados", len(diaria))

    st.subheader("1. Temperatura média por dispositivo/localização")
    st.plotly_chart(
        px.bar(media, x="device_id", y="avg_temp", hover_data=["total_leituras"],
               labels={"device_id": "Dispositivo/localização", "avg_temp": "Temperatura média"}),
        width="stretch",
    )

    st.subheader("2. Leituras por hora do dia")
    st.plotly_chart(
        px.line(horas, x="hora", y="contagem", markers=True,
                labels={"hora": "Hora do dia", "contagem": "Número de leituras"}),
        width="stretch",
    )

    st.subheader("3. Temperaturas máxima e mínima por dia")
    longa = diaria.melt(
        id_vars=["data"],
        value_vars=["temp_max", "temp_min"],
        var_name="medida",
        value_name="temperatura",
    )
    st.plotly_chart(
        px.line(longa, x="data", y="temperatura", color="medida", markers=True,
                labels={"data": "Data", "temperatura": "Temperatura", "medida": "Medida"}),
        width="stretch",
    )

    with st.expander("Ver dados agregados"):
        st.dataframe(diaria, width="stretch")
except Exception as exc:
    st.error("Não foi possível consultar o banco. Inicie o Docker e execute src/pipeline.py.")
    st.code(str(exc))
