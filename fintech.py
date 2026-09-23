import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import plotly.express as px
import io
import time
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Sabertec | Gateway Dashboard & Risk Control",
    page_icon="💳",
    layout="wide"
)

# Estilo visual moderno para el Dashboard
st.markdown("""
    <style>
    .main-header {
        font-size: 24px;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 5px;
    }
    .sub-header {
        font-size: 14px;
        color: #6B7280;
        margin-bottom: 25px;
    }
    </style>
    <div class="main-header">💳 SABERTEC PAYMENTS — DASHBOARD EN TIEMPO REAL</div>
    <div class="sub-header">Monitoreo de transacciones, flujo de caja, pasarelas y auditoría de contracargos.</div>
""", unsafe_allow_html=True)

HAS_GENAI = True

# --- 1. SIMULACIÓN DE LA BASE DE DATOS DE LA PASARELA (TRANSACCIONAL) ---
if "df_gateway" not in st.session_state:
    data_transacciones = [
        # Transacciones Zelle (Disputas / Fraude)
        {"ID_Tx": "TX-9001", "Fecha": "2026-06-10", "Pasarela": "Zelle", "Cliente": "USR-207", "Monto ($)": 4200.00, "Estado": "Disputa / Fraude", "Flujo": "Retenido"},
        {"ID_Tx": "TX-9002", "Fecha": "2026-06-11", "Pasarela": "Zelle", "Cliente": "USR-217", "Monto ($)": 4500.00, "Estado": "Disputa / Fraude", "Flujo": "Retenido"},
        {"ID_Tx": "TX-9003", "Fecha": "2026-06-12", "Pasarela": "Zelle", "Cliente": "USR-227", "Monto ($)": 4100.00, "Estado": "Disputa / Fraude", "Flujo": "Retenido"},
        {"ID_Tx": "TX-9004", "Fecha": "2026-06-13", "Pasarela": "Zelle", "Cliente": "USR-237", "Monto ($)": 4000.00, "Estado": "Disputa / Fraude", "Flujo": "Retenido"},
        {"ID_Tx": "TX-9005", "Fecha": "2026-06-14", "Pasarela": "Zelle", "Cliente": "USR-247", "Monto ($)": 4200.00, "Estado": "Disputa / Fraude", "Flujo": "Retenido"},

        # Transacciones PayPal (Disputas activas)
        {"ID_Tx": "TX-8001", "Fecha": "2026-06-10", "Pasarela": "PayPal", "Cliente": "USR-202", "Monto ($)": 2300.00, "Estado": "Disputa / Fraude", "Flujo": "Retenido"},
        {"ID_Tx": "TX-8002", "Fecha": "2026-06-11", "Pasarela": "PayPal", "Cliente": "USR-212", "Monto ($)": 2400.00, "Estado": "Disputa / Fraude", "Flujo": "Retenido"},
        {"ID_Tx": "TX-8003", "Fecha": "2026-06-12", "Pasarela": "PayPal", "Cliente": "USR-222", "Monto ($)": 2200.00, "Estado": "Disputa / Fraude", "Flujo": "Retenido"},
        {"ID_Tx": "TX-8004", "Fecha": "2026-06-13", "Pasarela": "PayPal", "Cliente": "USR-232", "Monto ($)": 2300.00, "Estado": "Disputa / Fraude", "Flujo": "Retenido"},
        {"ID_Tx": "TX-8005", "Fecha": "2026-06-14", "Pasarela": "PayPal", "Cliente": "USR-242", "Monto ($)": 2300.00, "Estado": "Disputa / Fraude", "Flujo": "Retenido"},

        # Transacciones Stripe (Inconsistencia de Conciliación)
        {"ID_Tx": "TX-7001", "Fecha": "2026-06-10", "Pasarela": "Stripe", "Cliente": "USR-204", "Monto ($)": 1810.00, "Estado": "Inconsistencia Conciliación", "Flujo": "Rechazada en Pasarela / Abonada Errónea"},
        {"ID_Tx": "TX-7002", "Fecha": "2026-06-11", "Pasarela": "Stripe", "Cliente": "USR-214", "Monto ($)": 1810.00, "Estado": "Inconsistencia Conciliación", "Flujo": "Rechazada en Pasarela / Abonada Errónea"},
        {"ID_Tx": "TX-7003", "Fecha": "2026-06-12", "Pasarela": "Stripe", "Cliente": "USR-224", "Monto ($)": 1810.00, "Estado": "Inconsistencia Conciliación", "Flujo": "Rechazada en Pasarela / Abonada Errónea"},
        {"ID_Tx": "TX-7004", "Fecha": "2026-06-13", "Pasarela": "Stripe", "Cliente": "USR-234", "Monto ($)": 1810.00, "Estado": "Inconsistencia Conciliación", "Flujo": "Rechazada en Pasarela / Abonada Errónea"},
        {"ID_Tx": "TX-7005", "Fecha": "2026-06-14", "Pasarela": "Stripe", "Cliente": "USR-244", "Monto ($)": 1810.00, "Estado": "Inconsistencia Conciliación", "Flujo": "Rechazada en Pasarela / Abonada Errónea"},

        # Pago Móvil (Operatividad limpia y regular)
        {"ID_Tx": "TX-6001", "Fecha": "2026-06-14", "Pasarela": "Pago Móvil", "Cliente": "CLIENTE-GENERAL", "Monto ($)": 10925.00, "Estado": "Aprobado / Regular", "Flujo": "Liquidado a Banco"}
    ]
    st.session_state.df_gateway = pd.DataFrame(data_transacciones)

if "ai_response" not in st.session_state:
    st.session_state.ai_response = None

# --- 2. PANEL DE FILTROS EN LA BARRA LATERAL ---
st.sidebar.header("🔍 Filtros y Auditoría de Pasarela")
busqueda_cliente = st.sidebar.text_input("Buscar por ID de Cliente o Transacción:", value="")

pasarela_seleccionada = st.sidebar.multiselect(
    "Filtrar Pasarelas:",
    options=["Zelle", "PayPal", "Stripe", "Pago Móvil"],
    default=["Zelle", "PayPal", "Stripe", "Pago Móvil"]
)

estado_seleccionado = st.sidebar.multiselect(
    "Filtrar Estados de Pago:",
    options=["Disputa / Fraude", "Inconsistencia Conciliación", "Aprobado / Regular"],
    default=["Disputa / Fraude", "Inconsistencia Conciliación", "Aprobado / Regular"]
)

st.sidebar.markdown("---")
ejecutar_ia = st.sidebar.button("🤖 Generar Dictamen IA con Gemini")

# --- APLICAR FILTROS A LOS DATOS ---
df_filtrado = st.session_state.df_gateway.copy()
if pasarela_seleccionada:
    df_filtrado = df_filtrado[df_filtrado["Pasarela"].isin(pasarela_seleccionada)]
if estado_seleccionado:
    df_filtrado = df_filtrado[df_filtrado["Estado"].isin(estado_seleccionado)]
if busqueda_cliente:
    df_filtrado = df_filtrado[
        df_filtrado["Cliente"].str.contains(busqueda_cliente, case=False, na=False) |
        df_filtrado["ID_Tx"].str.contains(busqueda_cliente, case=False, na=False)
    ]

# --- 3. MÉTRICAS EN TIEMPO REAL (KPI CARDS DE PASARELA) ---
st.markdown("### 📊 Métricas de Ingresos y Estado de Cobros")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(label="Volumen Total Procesado", value="$52,475.00", delta="100% General")
with kpi2:
    st.metric(label="Fondos Retenidos (Disputas)", value="$32,500.00", delta="Zelle & PayPal", delta_color="inverse")
with kpi3:
    st.metric(label="Desviación Contable (Stripe)", value="$9,050.00", delta="Conciliación errónea", delta_color="inverse")
with kpi4:
    st.metric(label="Exposición Total al Riesgo", value="$41,550.00", delta="Alerta Crítica", delta_color="inverse")

st.markdown("---")

# --- 4. GRÁFICOS INTERACTIVOS DEL DASHBOARD ---
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("💵 Volumen de Dinero por Pasarela y Estado")
    fig_bar = px.bar(
        df_filtrado,
        x="Pasarela",
        y="Monto ($)",
        color="Estado",
        barmode="group",
        color_discrete_map={
            "Disputa / Fraude": "#EF4444",
            "Inconsistencia Conciliación": "#F59E0B",
            "Aprobado / Regular": "#10B981"
        }
    )
    fig_bar.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=300)
    st.plotly_chart(fig_bar, use_container_width=True)

with col_graf2:
    st.subheader("🥧 Distribución del Flujo de Caja")
    fig_pie = px.pie(
        df_filtrado,
        names="Estado",
        values="Monto ($)",
        hole=0.4,
        color="Estado",
        color_discrete_map={
            "Disputa / Fraude": "#EF4444",
            "Inconsistencia Conciliación": "#F59E0B",
            "Aprobado / Regular": "#10B981"
        }
    )
    fig_pie.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=300)
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# --- 5. TABLA EN TIEMPO REAL CON FILTROS Y BÚSQUEDA ---
st.markdown("### 📋 Registro de Transacciones en Tiempo Real")
st.dataframe(df_filtrado, use_container_width=True)

# Exportar a Excel
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    df_filtrado.to_excel(writer, index=False, sheet_name='Transacciones_Filtradas')
excel_data = output.getvalue()

st.download_button(
    label="📥 Descargar Reporte Filtrado en Excel",
    data=excel_data,
    file_name="reporte_transacciones_filtradas.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# --- 6. INTEGRACIÓN DE LA IA CON MANEJO DE CUOTA (429) ---
if ejecutar_ia:
    if not HAS_GENAI:
        st.error("⚠️ La librería `google-genai` no está disponible.")
    else:
        with st.spinner("🤖 Conectando con Gemini (optimizando cuota y reintentos)..."):
            try:
                client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
                config = types.GenerateContentConfig(
                    system_instruction=(
                        "Eres un sistema experto en auditoría senior de riesgo crediticio y pasarelas de pago. "
                        "Redacta un dictamen profesional detallando el volumen de 52.475,00 USD, los 32.500,00 USD retenidos en Zelle y PayPal, "
                        "los 9.050,00 USD de inconsistencia en Stripe, y la lista de los 15 usuarios de alto riesgo para bloqueo inmediato."
                    ),
                    temperature=0.2
                )
                
                # Usamos un modelo más estable en cuotas gratuitas (gemini-2.5-flash)
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents="Ejecuta el dictamen completo de mitigación de contracargos y aislamiento de cuentas.",
                    config=config
                )
                st.session_state.ai_response = response.text
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    st.warning("⚠️ Límite temporal de peticiones alcanzado (Error 429). Espera 10 segundos y vuelve a hacer clic en el botón de la IA.")
                else:
                    st.error(f"Error al conectar con Gemini: {e}")

if st.session_state.ai_response:
    st.markdown("---")
    st.markdown("### 📑 Dictamen de Riesgo y Mitigación (Generado por IA)")
    st.markdown(st.session_state.ai_response)
