import streamlit as st
import pandas as pd
import plotly.express as px
import os

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
    /* Fondo principal */
    .stApp {
        background-color: #0B0C0E;
        color: #F5F2EB;
    }

    /* Barra lateral con fondo oscuro y contraste forzado */
    section[data-testid="stSidebar"] {
        background-color: #101215 !important;
        border-right: 2px solid #B86224 !important;
    }

    /* Forzar color claro y legible en TODOS los textos de la barra lateral */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] {
        color: #F5F2EB !important;
    }

    /* Marco naranja bronce automático para TODAS las imágenes (st.image) */
    div[data-testid="stImage"] img {
        border: 1.5px solid #D4722A !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 18px rgba(212, 114, 42, 0.22) !important;
        transition: transform 0.25s ease, border-color 0.25s ease !important;
    }
    div[data-testid="stImage"] img:hover {
        border-color: #F5A35C !important;
        transform: scale(1.01);
    }

    /* Recuadros naranja bronce tenue para secciones de la barra lateral */
    .sidebar-card {
        background: linear-gradient(145deg, rgba(212, 114, 42, 0.20) 0%, rgba(140, 74, 28, 0.12) 100%);
        border: 1.5px solid #C86D2D;
        border-left: 4px solid #E8873A;
        border-radius: 10px;
        padding: 0.85rem 1rem;
        margin-bottom: 0.85rem;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.35);
    }
    .sidebar-card-title {
        color: #F5A35C !important;
        font-size: 1.02rem;
        font-weight: 700;
        margin: 0 0 0.25rem 0;
        letter-spacing: 0.3px;
    }
    .sidebar-card-desc {
        color: #EFECE6 !important;
        font-size: 0.84rem;
        margin: 0;
        line-height: 1.35;
    }

    /* Contenedores de File Uploader y Sliders en la barra lateral con fondo bronce tenue */
    section[data-testid="stSidebar"] div[data-testid="stFileUploader"],
    section[data-testid="stSidebar"] div[data-testid="stSlider"] {
        background-color: rgba(212, 114, 42, 0.14) !important;
        border: 1px solid #9E531E !important;
        border-radius: 8px !important;
        padding: 0.65rem 0.75rem !important;
        margin-bottom: 0.75rem !important;
    }

    /* Zona interna de arrastrar archivo */
    section[data-testid="stFileUploaderDropzone"] {
        background-color: #171513 !important;
        border: 1.5px dashed #D4722A !important;
        border-radius: 8px !important;
        color: #F5F2EB !important;
    }
    section[data-testid="stFileUploaderDropzone"]:hover {
        border-color: #F29B50 !important;
        background-color: #221912 !important;
    }

    /* Botón "Upload" / "Browse files" dentro del File Uploader */
    section[data-testid="stFileUploaderDropzone"] button {
        background-color: #26180E !important;
        color: #F5B076 !important;
        border: 1.5px solid #D4722A !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }
    section[data-testid="stFileUploaderDropzone"] button:hover {
        background-color: #D4722A !important;
        color: #0B0C0E !important;
    }

    /* Encabezado principal estilo industrial */
    .hero-banner {
        background: linear-gradient(135deg, #1A1613 0%, #0E1013 100%);
        border: 1.5px solid #C86D2D;
        border-left: 6px solid #E07A2E;
        border-radius: 10px;
        padding: 1.4rem 1.8rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 20px rgba(200, 109, 45, 0.18);
    }
    .hero-title {
        color: #F5F2EB;
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: 0.5px;
    }
    .hero-accent {
        color: #E8873A;
    }
    .hero-subtitle {
        color: #D6CFC3;
        font-size: 0.98rem;
        margin-top: 0.35rem;
        margin-bottom: 0;
    }

    /* Tarjetas de métricas (KPIs) */
    div[data-testid="stMetric"] {
        background: linear-gradient(160deg, #1B1613 0%, #131519 100%);
        border: 1.5px solid #B56024;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.45);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        border-color: #F29B50;
        transform: translateY(-2px);
    }
    div[data-testid="stMetricLabel"] > label {
        color: #E6DFD3 !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        font-size: 0.78rem !important;
        letter-spacing: 0.8px;
    }
    div[data-testid="stMetricValue"] {
        color: #F5F2EB !important;
        font-weight: 700 !important;
    }

    /* Botones generales con borde bronce */
    .stButton > button, .stDownloadButton > button {
        background-color: #21160F !important;
        color: #F5F2EB !important;
        border: 1.5px solid #D4722A !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.2rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.4px;
        transition: all 0.25s ease !important;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background-color: #D4722A !important;
        color: #0B0C0E !important;
        border-color: #F29B50 !important;
        box-shadow: 0 0 14px rgba(212, 114, 42, 0.5) !important;
    }

    /* Subtítulos de sección */
    .section-header {
        background-color: rgba(212, 114, 42, 0.14);
        color: #F5A35C;
        font-size: 1.15rem;
        font-weight: 700;
        border-left: 4px solid #E07A2E;
        border-bottom: 1px solid #6E3B16;
        border-radius: 0 6px 6px 0;
        padding: 0.45rem 0.9rem;
        margin-top: 1.2rem;
        margin-bottom: 1rem;
        letter-spacing: 0.4px;
    }

    /* Pestañas (Tabs) */
    button[data-baseweb="tab"] {
        background-color: #161412 !important;
        border: 1px solid #7A4219 !important;
        border-radius: 6px 6px 0 0 !important;
        color: #D6CFC3 !important;
        margin-right: 4px;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #2B1B10 !important;
        border-color: #E8873A !important;
        color: #F5F2EB !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# UTILIDADES PARA IMÁGENES Y CSV
# ---------------------------------------------------------
def buscar_imagen(nombre_base):
    """Busca automáticamente una imagen en el repositorio con distintas extensiones."""
    extensiones = [".png", ".jpg", ".jpeg", ".webp", ".png.jpg"]
    for ext in extensiones:
        ruta = f"{nombre_base}{ext}"
        if os.path.exists(ruta):
            return ruta
    return None

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
        font=dict(color="#F5F2EB"),
        xaxis=dict(gridcolor="#262930", zerolinecolor="#3A3E47"),
        yaxis=dict(gridcolor="#262930", zerolinecolor="#3A3E47"),
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(bgcolor="rgba(26,20,15,0.85)", bordercolor="#C86D2D", borderwidth=1)
    )
    return fig

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
# BARRA LATERAL: LOGO, DATASETS Y PARÁMETROS
# ---------------------------------------------------------
with st.sidebar:
    ruta_logo = buscar_imagen("logo")
    if ruta_logo:
        st.image(ruta_logo, use_container_width=True)

    st.markdown("""
    <div class="sidebar-card">
        <div class="sidebar-card-title">📂 Datasets de Grafana</div>
        <p class="sidebar-card-desc">Carga los archivos CSV exportados desde InfluxDB / Grafana para iniciar el diagnóstico:</p>
    </div>
    """, unsafe_allow_html=True)

    file_temp = st.file_uploader("1. Temperatura de Celdas (.csv)", type=["csv"])
    file_curr = st.file_uploader("2. Corriente de Carga (.csv)", type=["csv"])

    st.markdown("""
    <div class="sidebar-card" style="margin-top: 0.6rem;">
        <div class="sidebar-card-title">🛡️ Parámetros de Protección</div>
        <p class="sidebar-card-desc">Ajusta los límites operativos de seguridad del banco de baterías:</p>
    </div>
    """, unsafe_allow_html=True)

    umbral_temp = st.slider("Límite Térmico Crítico (°C)", 30.0, 55.0, 40.0, step=0.5)
    umbral_curr = st.slider("Límite de Corriente Máx. (A)", 3.0, 8.0, 6.5, step=0.1)

    st.markdown("""
    <div class="sidebar-card" style="margin-top: 0.6rem;">
        <div class="sidebar-card-title">🖼️ Galería Visual (Opcional)</div>
        <p class="sidebar-card-desc">Sube capturas de Wokwi o Grafana para mostrarlas en la interfaz:</p>
    </div>
    """, unsafe_allow_html=True)
    imgs_extra = st.file_uploader(
        "Subir imágenes (.png, .jpg)", type=["png", "jpg", "jpeg"], accept_multiple_files=True
    )

    st.markdown("""
    <div class="sidebar-card" style="margin-top: 0.8rem; padding: 0.65rem 0.85rem;">
        <p class="sidebar-card-desc" style="font-size: 0.78rem; text-align: center;">
            <b>Arquitectura IoT:</b><br>ESP32 • ThingsBoard • InfluxDB • Grafana
        </p>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# CUERPO PRINCIPAL DE ANÁLISIS
# ---------------------------------------------------------
ruta_portada = buscar_imagen("portada")
ruta_wokwi = buscar_imagen("wokwi")
ruta_grafana = buscar_imagen("grafana")

if file_temp and file_curr:
    df_t = cargar_csv_grafana(file_temp, "Temperatura_C")
    df_c = cargar_csv_grafana(file_curr, "Corriente_A")

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

        tab1, tab2, tab3, tab4 = st.tabs([
            "📈 Series Temporales",
            "🔬 Correlación T vs I",
            "📋 Auditoría y Exportación",
            "🖼️ Arquitectura & Evidencias"
        ])

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

        with tab4:
            st.markdown('<div class="section-header">🏗️ Evidencias del Ecosistema IoT</div>', unsafe_allow_html=True)
            imagenes_disponibles = []
            if ruta_portada:
                imagenes_disponibles.append((ruta_portada, "Arquitectura General VoltGuard IoT"))
            if ruta_wokwi:
                imagenes_disponibles.append((ruta_wokwi, "Simulación Hardware ESP32 + DHT22 + Relé (Wokwi)"))
            if ruta_grafana:
                imagenes_disponibles.append((ruta_grafana, "Telemetría en Tiempo Real (InfluxDB + Grafana)"))
            if imgs_extra:
                for img in imgs_extra:
                    imagenes_disponibles.append((img, img.name))

            if imagenes_disponibles:
                cols_img = st.columns(2)
                for idx, (fuente, titulo) in enumerate(imagenes_disponibles):
                    with cols_img[idx % 2]:
                        st.image(fuente, caption=titulo, use_container_width=True)
            else:
                st.info("Sube imágenes en el panel izquierdo o guarda `portada.png`, `wokwi.png` o `grafana.png` en tu repositorio de GitHub para visualizarlas aquí.")

else:
    # ---------------------------------------------------------
    # PANTALLA DE INICIO CON IMAGEN DE PORTADA E INSTRUCCIONES
    # ---------------------------------------------------------
    if ruta_portada:
        col_banner, col_desc = st.columns([1.15, 1])
        with col_banner:
            st.image(ruta_portada, use_container_width=True)
        with col_desc:
            st.markdown("""
            <div style="background: linear-gradient(145deg, rgba(212, 114, 42, 0.16) 0%, #14161A 100%); border: 1.5px solid #C86D2D; border-left: 5px solid #E8873A; border-radius: 10px; padding: 1.5rem;">
                <h4 style="color: #F5A35C; margin-top: 0; font-size: 1.25rem; font-weight: 700;">👋 Panel Listo para Análisis</h4>
                <p style="color: #EFECE6; font-size: 0.94rem; margin-bottom: 0.8rem; line-height: 1.45;">
                    Para generar las métricas de diagnóstico y las curvas de comportamiento, carga los registros históricos en la barra lateral izquierda:
                </p>
                <ul style="color: #D6CFC3; font-size: 0.9rem; padding-left: 1.2rem; margin-bottom: 1rem; line-height: 1.5;">
                    <li style="margin-bottom: 0.4rem;"><b>1. Temperatura de Celdas (.csv)</b> — Lecturas del sensor DHT22.</li>
                    <li><b>2. Corriente de Carga (.csv)</b> — Lecturas de corriente del banco.</li>
                </ul>
                <p style="color: #B8B2A6; font-size: 0.84rem; margin-bottom: 0;">
                    <i>El sistema sincronizará ambas series automáticamente para calcular KPIs, correlación y alertas críticas.</i>
                </p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: linear-gradient(145deg, rgba(212, 114, 42, 0.16) 0%, #14161A 100%); border: 1.5px solid #C86D2D; border-left: 5px solid #E8873A; border-radius: 10px; padding: 1.5rem; margin-top: 0.5rem;">
            <h4 style="color: #F5A35C; margin-top: 0; font-size: 1.25rem; font-weight: 700;">👋 Panel Listo para Análisis</h4>
            <p style="color: #EFECE6; font-size: 0.95rem; margin-bottom: 0.7rem;">
                Carga los dos archivos CSV exportados desde Grafana en el panel izquierdo para iniciar el análisis:
            </p>
            <ul style="color: #D6CFC3; font-size: 0.92rem; margin-bottom: 0.8rem;">
                <li><b>1. Temperatura de Celdas (.csv)</b> — Serie histórica del sensor DHT22</li>
                <li><b>2. Corriente de Carga (.csv)</b> — Serie histórica del sensor de corriente</li>
            </ul>
            <p style="color: #B8B2A6; font-size: 0.85rem; margin-bottom: 0;">
                💡 <i>Tip visual: Si subes una imagen llamada <b>portada.png</b> o <b>portada.jpg</b> a la raíz de tu repositorio en GitHub, aparecerá automáticamente aquí con borde bronce.</i>
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Mostrar capturas extra si el usuario las sube en la pantalla inicial
    if imgs_extra:
        st.markdown('<div class="section-header">🖼️ Vista Previa de Evidencias Cargadas</div>', unsafe_allow_html=True)
        cols_prev = st.columns(min(len(imgs_extra), 3))
        for idx, img in enumerate(imgs_extra):
            with cols_prev[idx % 3]:
                st.image(img, caption=img.name, use_container_width=True)
