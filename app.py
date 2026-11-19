import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="VoltGuard IoT | Telemetría & Analítica",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# ESTILOS CSS PERSONALIZADOS (NEGRO CARBÓN & NARANJA BRONCE)
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Fondo principal y tipografía */
    .stApp {
        background-color: #0B0C0E;
        color: #F2EFE9;
    }

    /* Barra lateral */
    section[data-testid="stSidebar"] {
        background-color: #121417;
        border-right: 1.5px solid #8C4A1C;
    }

    /* Encabezado principal estilo industrial */
    .hero-banner {
        background: linear-gradient(135deg, #16181D 0%, #0D0E11 100%);
        border: 1.5px solid #C86D2D;
        border-left: 6px solid #E07A2E;
        border-radius: 10px;
        padding: 1.4rem 1.8rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(200, 109, 45, 0.15);
    }
    .hero-title {
        color: #F5F2EB;
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: 0.5px;
    }
    .hero-accent {
        color: #E07A2E;
    }
    .hero-subtitle {
        color: #B8B2A6;
        font-size: 0.98rem;
        margin-top: 0.35rem;
        margin-bottom: 0;
    }

    /* Tarjetas de métricas (KPIs) */
    div[data-testid="stMetric"] {
        background-color: #14161A;
        border: 1.5px solid #9E531E;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.45);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        border-color: #E8873A;
        transform: translateY(-2px);
    }
    div[data-testid="stMetricLabel"] > label {
        color: #C7BEB0 !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        font-size: 0.78rem !important;
        letter-spacing: 0.8px;
    }
    div[data-testid="stMetricValue"] {
        color: #F5F2EB !important;
        font-weight: 700 !important;
    }

    /* Botones con borde bronce y efecto hover */
    .stButton > button, .stDownloadButton > button {
        background-color: #191B20 !important;
        color: #F5F2EB !important;
        border: 1.5px solid #D4722A !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.2rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.4px;
        transition: all 0.25s ease !important;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background-color: #C86D2D !important;
        color: #0B0C0E !important;
        border-color: #F29B50 !important;
        box-shadow: 0 0 14px rgba(212, 114, 42, 0.5) !important;
    }

    /* Contenedores de carga de archivos */
    section[data-testid="stFileUploaderDropzone"] {
        background-color: #181A1F !important;
        border: 1.5px dashed #B56024 !important;
        border-radius: 8px !important;
    }
    section[data-testid="stFileUploaderDropzone"]:hover {
        border-color: #E8873A !important;
        background-color: #1E2127 !important;
    }

    /* Subtítulos de sección */
    .section-header {
        color: #E07A2E;
        font-size: 1.2rem;
        font-weight: 700;
        border-bottom: 1.5px solid #4A2810;
        padding-bottom: 0.4rem;
        margin-top: 1.2rem;
        margin-bottom: 1rem;
        letter-spacing: 0.4px;
    }

    /* Pestañas (Tabs) */
    button[data-baseweb="tab"] {
        background-color: #14161A !important;
        border: 1px solid #593014 !important;
        border-radius: 6px 6px 0 0 !important;
        color: #C7BEB0 !important;
        margin-right: 4px;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #241811 !important;
        border-color: #E07A2E !important;
        color: #F5F2EB !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# ENCABEZADO PRINCIPAL
# ---------------------------------------------------------
st.markdown("""
<div class="hero-banner">
    <h1 class="hero-title">⚡ VOLTGUARD <span class="hero-accent">IoT</span></h1>
    <p class="hero-subtitle">Plataforma de Analítica Histórica y Diagnóstico Térmico-Eléctrico para Estaciones de Carga de Litio</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# FUNCIÓN DE LIMPIEZA PARA CSV EXPORTADOS DESDE GRAFANA
# ---------------------------------------------------------
def cargar_csv_grafana(archivo, nombre_var):
    df = pd.read_csv(archivo, comment="#")
    col_tiempo = df.columns[0]
    col_valor = df.columns[-1]
    df = df[[col_tiempo, col_valor]].copy()
    df.columns = ["Tiempo", nombre_var]
    df["Tiempo"] = pd.to_datetime(df["Tiempo"], errors="coerce")
    df[nombre_var] = pd.to_numeric(df[nombre_var], errors="coerce")
    return df.dropna().sort_values("Tiempo")

def estilizar_figura(fig):
    fig.update_layout(
        paper_bgcolor="#14161A",
        plot_bgcolor="#0F1114",
        font=dict(color="#E8E4DC"),
        xaxis=dict(gridcolor="#262930", zerolinecolor="#3A3E47"),
        yaxis=dict(gridcolor="#262930", zerolinecolor="#3A3E47"),
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(bgcolor="rgba(20,22,26,0.8)", bordercolor="#8C4A1C", borderwidth=1)
    )
    return fig

# ---------------------------------------------------------
# BARRA LATERAL: CARGA DE ARCHIVOS Y UMBRALES
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 📂 Datasets de Grafana")
    st.caption("Sube los registros exportados desde InfluxDB / Grafana:")
    file_temp = st.file_uploader("1. Temperatura de Celdas (.csv)", type=["csv"])
    file_curr = st.file_uploader("2. Corriente de Carga (.csv)", type=["csv"])

    st.markdown("---")
    st.markdown("### 🛡️ Parámetros de Protección")
    umbral_temp = st.slider("Límite Térmico Crítico (°C)", 30.0, 55.0, 40.0, step=0.5)
    umbral_curr = st.slider("Límite de Corriente Máx. (A)", 3.0, 8.0, 6.5, step=0.1)

    st.markdown("---")
    st.caption("Arquitectura: ESP32 • ThingsBoard • InfluxDB • Grafana")

# ---------------------------------------------------------
# CUERPO PRINCIPAL DE ANÁLISIS
# ---------------------------------------------------------
if file_temp and file_curr:
    df_t = cargar_csv_grafana(file_temp, "Temperatura_C")
    df_c = cargar_csv_grafana(file_curr, "Corriente_A")

    # Sincronización temporal de ambas series
    df = pd.merge_asof(
        df_t, df_c, on="Tiempo", direction="nearest", tolerance=pd.Timedelta("15s")
    ).dropna()

    if df.empty:
        st.error("No se encontraron marcas de tiempo coincidentes entre ambos archivos CSV.")
    else:
        df["Estado_Seguridad"] = df.apply(
            lambda r: "Alerta Crítica" if (r["Temperatura_C"] > umbral_temp or r["Corriente_A"] > umbral_curr) else "Operación Nominal",
            axis=1
        )
        alertas = df[df["Estado_Seguridad"] == "Alerta Crítica"]
        corr = df["Temperatura_C"].corr(df["Corriente_A"])

        # Fila de KPIs
        st.markdown('<div class="section-header">📌 Indicadores Clave de Rendimiento (KPIs)</div>', unsafe_allow_html=True)
        k1, k2, k3, k4 = st.columns(4)
        k1.metric(
            "Temperatura Promedio",
            f"{df['Temperatura_C'].mean():.2f} °C",
            f"Pico máx: {df['Temperatura_C'].max():.1f} °C"
        )
        k2.metric(
            "Corriente Promedio",
            f"{df['Corriente_A'].mean():.2f} A",
            f"Pico máx: {df['Corriente_A'].max():.2f} A"
        )
        k3.metric(
            "Eventos Fuera de Rango",
            f"{len(alertas)} reg.",
            f"{(len(alertas) / len(df) * 100):.1f}% del muestreo",
            delta_color="inverse"
        )
        k4.metric(
            "Correlación Térmica-Eléctrica",
            f"{corr:.2f}" if pd.notna(corr) else "0.00",
            f"{len(df)} muestras válidas"
        )

        # Pestañas organizadas
        tab1, tab2, tab3 = st.tabs(["📈 Series Temporales", "🔬 Correlación T vs I", "📋 Auditoría y Exportación"])

        with tab1:
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                fig_t = px.line(
                    df, x="Tiempo", y="Temperatura_C",
                    title="Evolución Térmica del Banco de Celdas (°C)",
                    markers=True
                )
                fig_t.update_traces(line=dict(color="#E07A2E", width=2.5), marker=dict(size=6, color="#F5B076"))
                fig_t.add_hline(
                    y=umbral_temp, line_dash="dash", line_color="#FF4B4B",
                    annotation_text=f"Umbral ({umbral_temp} °C)", annotation_font_color="#FF4B4B"
                )
                st.plotly_chart(estilizar_figura(fig_t), use_container_width=True)

            with col_g2:
                fig_c = px.line(
                    df, x="Tiempo", y="Corriente_A",
                    title="Perfil de Corriente de Carga (A)",
                    markers=True
                )
                fig_c.update_traces(line=dict(color="#C98A3C", width=2.5), marker=dict(size=6, color="#F2D096"))
                fig_c.add_hline(
                    y=umbral_curr, line_dash="dash", line_color="#FF4B4B",
                    annotation_text=f"Umbral ({umbral_curr} A)", annotation_font_color="#FF4B4B"
                )
                st.plotly_chart(estilizar_figura(fig_c), use_container_width=True)

        with tab2:
            fig_scatter = px.scatter(
                df,
                x="Corriente_A",
                y="Temperatura_C",
                color="Estado_Seguridad",
                color_discrete_map={
                    "Operación Nominal": "#D9823B",
                    "Alerta Crítica": "#FF3B30"
                },
                title="Dispersión Corriente de Carga (A) vs. Temperatura de Celdas (°C)",
                labels={"Corriente_A": "Corriente de Carga (A)", "Temperatura_C": "Temperatura (°C)"}
            )
            fig_scatter.update_traces(marker=dict(size=10, line=dict(width=1, color="#0B0C0E")))
            st.plotly_chart(estilizar_figura(fig_scatter), use_container_width=True)

        with tab3:
            if not alertas.empty:
                st.warning(f"⚠️ Se registraron {len(alertas)} lecturas que excedieron los límites de seguridad configurados.")
                st.dataframe(alertas, use_container_width=True)
            else:
                st.success("✅ Todas las lecturas se mantuvieron dentro de los márgenes seguros de operación.")

            csv_consolidado = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Descargar Reporte Consolidado (CSV)",
                data=csv_consolidado,
                file_name="voltguard_reporte_consolidado.csv",
                mime="text/csv"
            )
else:
    st.markdown("""
    <div style="background-color:#14161A; border:1.5px solid #8C4A1C; border-radius:10px; padding:1.5rem; margin-top:1rem;">
        <h4 style="color:#E07A2E; margin-top:0;">👋 Panel Listo para Análisis</h4>
        <p style="color:#D0C9BD; margin-bottom:0.5rem;">
            Para generar las métricas de diagnóstico y las curvas de comportamiento, carga los dos archivos CSV exportados desde Grafana en el panel izquierdo:
        </p>
        <ul style="color:#B8B2A6; margin-bottom:0;">
            <li><b>temperatura_celdas.csv</b> (Serie histórica del sensor DHT22)</li>
            <li><b>corriente_carga.csv</b> (Serie histórica del sensor de corriente)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
