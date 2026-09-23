import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import plotly.express as px
import io
from datetime import datetime

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="Sabertec AI: Dashboard de Pasarela de Pagos y Riesgo",
    page_icon="💳",
    layout="wide"
)

# Estilo CSS para el título corporativo
st.markdown("""
    <style>
    .titulo-principal {
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        width: 100%;
        margin-bottom: 20px;
    }
    </style>
    <div class="titulo-principal">DASHBOARD DE PASARELA DE PAGOS Y CONTROL DE RIESGO FINANCIERO</div>
""", unsafe_allow_html=True)

HAS_GENAI = True

# Configuración de la barra lateral para filtros de auditoría y ejecución
st.sidebar.header("⚙️ Filtros de Auditoría y Pasarelas")
filtro_pasarela = st.sidebar.selectbox(
    "Filtrar por Pasarela de Pago:",
    ["Todas", "Zelle", "PayPal", "Stripe", "Pago Móvil"]
)

filtro_estado = st.sidebar.selectbox(
    "Filtrar por Estado de Transacción:",
    ["Todos", "Disputa / Fraude", "Inconsistencia Conciliación", "Aprobado / Regular"]
)

prompt_usuario = st.sidebar.text_area(
    "💬 Objetivo del Agente Auditor:",
    value="Ejecuta la auditoría integral de las pasarelas de pago, evalúa el volumen transaccional de 52.475,00 USD y genera el dictamen de mitigación de contracargos.",
    height=100
)

run_agent = st.sidebar.button("🚀 Ejecutar Análisis de Pasarela")

# Inicialización de estados
if "df_transacciones" not in st.session_state:
    # Construcción de base de datos detallada de la pasarela según el dictamen[cite: 7]
    transacciones_base = [
        # Zelle ($21,000 en disputa)[cite: 7]
        {"ID_Tx": "TX-ZL-101", "Pasarela": "Zelle", "Monto ($)": 4200.0, "Estado": "Disputa / Fraude", "Cliente": "USR-207", "Riesgo": "Alto"},
        {"ID_Tx": "TX-ZL-102", "Pasarela": "Zelle", "Monto ($)": 4500.0, "Estado": "Disputa / Fraude", "Cliente": "USR-217", "Riesgo": "Alto"},
        {"ID_Tx": "TX-ZL-103", "Pasarela": "Zelle", "Monto ($)": 4100.0, "Estado": "Disputa / Fraude", "Cliente": "USR-227", "Riesgo": "Alto"},
        {"ID_Tx": "TX-ZL-104", "Pasarela": "Zelle", "Monto ($)": 4000.0, "Estado": "Disputa / Fraude", "Cliente": "USR-237", "Riesgo": "Alto"},
        {"ID_Tx": "TX-ZL-105", "Pasarela": "Zelle", "Monto ($)": 4200.0, "Estado": "Disputa / Fraude", "Cliente": "USR-247", "Riesgo": "Alto"},
        
        # PayPal ($11,500 en disputa)[cite: 7]
        {"ID_Tx": "TX-PP-201", "Pasarela": "PayPal", "Monto ($)": 2300.0, "Estado": "Disputa / Fraude", "Cliente": "USR-202", "Riesgo": "Alto"},
        {"ID_Tx": "TX-PP-202", "Pasarela": "PayPal", "Monto ($)": 2400.0, "Estado": "Disputa / Fraude", "Cliente": "USR-212", "Riesgo": "Alto"},
        {"ID_Tx": "TX-PP-203", "Pasarela": "PayPal", "Monto ($)": 2200.0, "Estado": "Disputa / Fraude", "Cliente": "USR-222", "Riesgo": "Alto"},
        {"ID_Tx": "TX-PP-204", "Pasarela": "PayPal", "Monto ($)": 2300.0, "Estado": "Disputa / Fraude", "Cliente": "USR-232", "Riesgo": "Alto"},
        {"ID_Tx": "TX-PP-205", "Pasarela": "PayPal", "Monto ($)": 2300.0, "Estado": "Disputa / Fraude", "Cliente": "USR-242", "Riesgo": "Alto"},

        # Stripe ($9,050 de inconsistencia)[cite: 7]
        {"ID_Tx": "TX-ST-301", "Pasarela": "Stripe", "Monto ($)": 1810.0, "Estado": "Inconsistencia Conciliación", "Cliente": "USR-204", "Riesgo": "Alto"},
        {"ID_Tx": "TX-ST-302", "Pasarela": "Stripe", "Monto ($)": 1810.0, "Estado": "Inconsistencia Conciliación", "Cliente": "USR-214", "Riesgo": "Alto"},
        {"ID_Tx": "TX-ST-303", "Pasarela": "Stripe", "Monto ($)": 1810.0, "Estado": "Inconsistencia Conciliación", "Cliente": "USR-224", "Riesgo": "Alto"},
        {"ID_Tx": "TX-ST-304", "Pasarela": "Stripe", "Monto ($)": 1810.0, "Estado": "Inconsistencia Conciliación", "Cliente": "USR-234", "Riesgo": "Alto"},
        {"ID_Tx": "TX-ST-305", "Pasarela": "Stripe", "Monto ($)": 1810.0, "Estado": "Inconsistencia Conciliación", "Cliente": "USR-244", "Riesgo": "Alto"},

        # Pago Móvil (Resto del volumen hasta los 52.475,00 USD con operatividad regular)[cite: 7]
        {"ID_Tx": "TX-PM-401", "Pasarela": "Pago Móvil", "Monto ($)": 10925.0, "Estado": "Aprobado / Regular", "Cliente": "USR-SANO-1", "Riesgo": "Bajo"}
    ]
    st.session_state.df_transacciones = pd.DataFrame(transacciones_base)

if "response_text" not in st.session_state:
    st.session_state.response_text = None
if "fecha_actual" not in st.session_state:
    st.session_state.fecha_actual = None

if run_agent:
    if not HAS_GENAI:
        st.error("⚠️ La librería `google-genai` no está instalada.")
    else:
        with st.spinner("💳 Conectando con los procesadores de pago y analizando flujos..."):
            try:
                client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
                config = types.GenerateContentConfig(
                    system_instruction=(
                        "Eres un sistema experto en auditoría senior automática de riesgo crediticio y pasarelas de pago para Sabertec. "
                        "Genera un dictamen formal detallando el volumen de 52.475,00 USD, los 32.500,00 USD retenidos en Zelle y PayPal, "
                        "y la inconsistencia de 9.050,00 USD en Stripe[cite: 7]."
                    ),
                    temperature=0.2
                )
                chat = client.chats.create(model="gemini-3.6-flash", config=config)
                response = chat.send_message(prompt_usuario)
                st.session_state.response_text = response.text
                
                ahora = datetime.now()
                meses = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}
                st.session_state.fecha_actual = f"{ahora.day} de {meses[ahora.month]} de {ahora.year}"
            except Exception as e:
                st.warning(f"Nota del sistema: {e}")

# --- FILTRADO DINÁMICO DE LA DATA PARA EL DASHBOARD ---
df_filtrado = st.session_state.df_transacciones.copy()
if filtro_pasarela != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Pasarela"] == filtro_pasarela]
if filtro_estado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Estado"] == filtro_estado]

# --- BLOQUE 1: MÉTRICAS EN TIEMPO REAL (KPI CARDS) ---
st.markdown("### 📊 Panel de Control en Tiempo Real")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Volumen Total Procesado", value="$52,475.00", delta="100% Operaciones")[cite: 7]
with col2:
    st.metric(label="Exposición Total al Riesgo", value="$41,550.00", delta="79.1% del total", delta_color="inverse")[cite: 7]
with col3:
    st.metric(label="Fondos Retenidos (Disputas)", value="$32,500.00", delta="Zelle & PayPal", delta_color="inverse")[cite: 7]
with col4:
    st.metric(label="Inconsistencia Contable", value="$9,050.00", delta="Brecha Stripe", delta_color="inverse")[cite: 7]

st.markdown("---")

# --- BLOQUE 2: GRÁFICOS DE FLUJO DE DINERO Y PASARELAS ---
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("💳 Estado del Flujo de Dinero por Pasarela")
    fig_pasarelas = px.bar(
        st.session_state.df_transacciones,
        x="Pasarela",
        y="Monto ($)",
        color="Estado",
        title="Distribución de Fondos y Disputas por Canal",
        color_discrete_map={
            "Disputa / Fraude": "#e74c3c", 
            "Inconsistencia Conciliación": "#f39c12", 
            "Aprobado / Regular": "#27ae60"
        }
    )
    fig_pasarelas.update_layout(margin=dict(t=30, b=20, l=20, r=20), height=320)
    st.plotly_chart(fig_pasarelas, use_container_width=True)

with col_g2:
    st.subheader("🔄 Composición de Riesgo de Cobros")
    resumen_estado = st.session_state.df_transacciones.groupby("Estado")["Monto ($)"].sum().reset_index()
    fig_pie = px.pie(
        resumen_estado,
        names="Estado",
        values="Monto ($)",
        hole=0.4,
        color="Estado",
        color_discrete_map={
            "Disputa / Fraude": "#e74c3c", 
            "Inconsistencia Conciliación": "#f39c12", 
            "Aprobado / Regular": "#27ae60"
        }
    )
    fig_pie.update_layout(margin=dict(t=30, b=20, l=20, r=20), height=320)
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# --- BLOQUE 3: REPORTE Y FILTROS RÁPIDOS (AUDITORÍA) ---
st.markdown("### 📋 Reporte Detallado de Transacciones y Auditoría Rápida")
st.markdown("Utiliza los filtros de la barra lateral para buscar clientes, pasarelas o estados específicos de forma inmediata.")
st.dataframe(df_filtrado, use_container_width=True)

# --- BLOQUE 4: DICTAMEN EJECUTIVO Y DESCARGAS ---
st.markdown("---")
st.markdown("### 📑 Dictamen Ejecutivo de Mitigación de Contracargos")

if st.session_state.response_text:
    st.markdown(f"**Fecha de Emisión:** {st.session_state.fecha_actual}[cite: 7]")
    st.markdown(st.session_state.response_text)
else:
    st.info("💡 Haz clic en **'Ejecutar Análisis de Pasarela'** en la barra lateral para generar el dictamen detallado de la IA.")

# Botones de exportación
st.markdown("### 📥 Exportación de Reportes para el Comité")
def convertir_a_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Auditoria_Pasarelas')
    return output.getvalue()

excel_bytes = convertir_a_excel(st.session_state.df_transacciones)
st.download_button(
    label="📥 Descargar Reporte Completo de Pasarelas (Excel)",
    data=excel_bytes,
    file_name="reporte_pasarelas_sabertec.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
