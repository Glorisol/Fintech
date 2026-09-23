import streamlit as st
import pandas as pd
import plotly.express as px
import io

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

# --- 1. BASE DE DATOS DE LA PASARELA (TRANSACCIONAL) ---
if "df_gateway" not in st.session_state:
    data_transacciones = [
        # Zelle (Disputas / Fraude)
        {"ID_Tx": "TX-9001", "Fecha": "2026-06-10", "Pasarela": "Zelle", "Cliente": "USR-207", "Monto ($)": 4200.00, "Estado": "Disputa / Fraude", "Flujo": "Retenido"},
        {"ID_Tx": "TX-9002", "Fecha": "2026-06-11", "Pasarela": "Zelle", "Cliente": "USR-217", "Monto ($)": 4500.00, "Estado": "Disputa / Fraude", "Flujo": "Retenido"},
        {"ID_Tx": "TX-9003", "Fecha": "2026-06-12", "Pasarela": "Zelle", "Cliente": "USR-227", "Monto ($)": 4100.00, "Estado": "Disputa / Fraude", "Flujo": "Retenido"},
        {"ID_Tx": "TX-9004", "Fecha": "2026-06-13", "Pasarela": "Zelle", "Cliente": "USR-237", "Monto ($)": 4000.00, "Estado": "Disputa / Fraude", "Flujo": "Retenido"},
        {"ID_Tx": "TX-9005", "Fecha": "2026-06-14", "Pasarela": "Zelle", "Cliente": "USR-247", "Monto ($)": 4200.00, "Estado": "Disputa / Fraude", "Flujo": "Retenido"},

        # PayPal (Disputas activas)
        {"ID_Tx": "TX-8001", "Fecha": "2026-06-10", "Pasarela": "PayPal", "Cliente": "USR-202", "Monto ($)": 2300.00, "Estado": "Disputa / Fraude", "Flujo": "Retenido"},
        {"ID_Tx": "TX-8002", "Fecha": "2026-06-11", "Pasarela": "PayPal", "Cliente": "USR-212", "Monto ($)": 2400.00, "Estado": "Disputa / Fraude", "Flujo": "Retenido"},
        {"ID_Tx": "TX-8003", "Fecha": "2026-06-12", "Pasarela": "PayPal", "Cliente": "USR-222", "Monto ($)": 2200.00, "Estado": "Disputa / Fraude", "Flujo": "Retenido"},
        {"ID_Tx": "TX-8004", "Fecha": "2026-06-13", "Pasarela": "PayPal", "Cliente": "USR-232", "Monto ($)": 2300.00, "Estado": "Disputa / Fraude", "Flujo": "Retenido"},
        {"ID_Tx": "TX-8005", "Fecha": "2026-06-14", "Pasarela": "PayPal", "Cliente": "USR-242", "Monto ($)": 2300.00, "Estado": "Disputa / Fraude", "Flujo": "Retenido"},

        # Stripe (Inconsistencia de Conciliación)
        {"ID_Tx": "TX-7001", "Fecha": "2026-06-10", "Pasarela": "Stripe", "Cliente": "USR-204", "Monto ($)": 1810.00, "Estado": "Inconsistencia Conciliación", "Flujo": "Rechazada / Abonada Errónea"},
        {"ID_Tx": "TX-7002", "Fecha": "2026-06-11", "Pasarela": "Stripe", "Cliente": "USR-214", "Monto ($)": 1810.00, "Estado": "Inconsistencia Conciliación", "Flujo": "Rechazada / Abonada Errónea"},
        {"ID_Tx": "TX-7003", "Fecha": "2026-06-12", "Pasarela": "Stripe", "Cliente": "USR-224", "Monto ($)": 1810.00, "Estado": "Inconsistencia Conciliación", "Flujo": "Rechazada / Abonada Errónea"},
        {"ID_Tx": "TX-7004", "Fecha": "2026-06-13", "Pasarela": "Stripe", "Cliente": "USR-234", "Monto ($)": 1810.00, "Estado": "Inconsistencia Conciliación", "Flujo": "Rechazada / Abonada Errónea"},
        {"ID_Tx": "TX-7005", "Fecha": "2026-06-14", "Pasarela": "Stripe", "Cliente": "USR-244", "Monto ($)": 1810.00, "Estado": "Inconsistencia Conciliación", "Flujo": "Rechazada / Abonada Errónea"},

        # Pago Móvil (Operatividad limpia)
        {"ID_Tx": "TX-6001", "Fecha": "2026-06-14", "Pasarela": "Pago Móvil", "Cliente": "CLIENTE-GENERAL", "Monto ($)": 10925.00, "Estado": "Aprobado / Regular", "Flujo": "Liquidado a Banco"}
    ]
    st.session_state.df_gateway = pd.DataFrame(data_transacciones)

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
    st.metric(label="Volumen Total Procesado", value="$52,475.00", delta="100% General")[cite: 5]
with kpi2:
    st.metric(label="Fondos Retenidos (Disputas)", value="$32,500.00", delta="Zelle & PayPal", delta_color="inverse")[cite: 5]
with kpi3:
    st.metric(label="Desviación Contable (Stripe)", value="$9,050.00", delta="Conciliación errónea", delta_color="inverse")[cite: 5]
with kpi4:
    st.metric(label="Exposición Total al Riesgo", value="$41,550.00", delta="Alerta Crítica", delta_color="inverse")[cite: 5]

st.markdown("---")

# --- 4. GRÁFICOS INTERACTIVOS ---
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

# --- 5. TABLA EN TIEMPO REAL CON FILTROS ---
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

# --- 6. DICTAMEN EJECUTIVO FINANCIERO ---
st.markdown("---")
st.markdown("### 📑 Dictamen Ejecutivo de Mitigación y Prevención de Fraude")
st.markdown("""
**A:** Dirección General y Comité de Riesgos de Sabertec[cite: 5]  
**De:** Auditoría Senior Automática de Riesgo Crediticio y Pasarelas[cite: 5]  
**Asunto:** Dictamen de Mitigación de Contracargos, Discrepancias de Conciliación y Aislamiento de Cuentas Fraudulentas[cite: 5]

#### 📊 Resumen Ejecutivo Financiero
* **Volumen transaccional analizado:** 52.475,00 USD[cite: 5].
* **Fondos retenidos en disputa (sin liquidación):** 32.500,00 USD (61.9% del volumen total en Zelle y PayPal)[cite: 5].
* **Inconsistencia de control interno (Stripe):** 9.050,00 USD en transacciones rechazadas que figuran erróneamente como liquidadas[cite: 5].
* **Exposición total al riesgo operativo y de crédito:** 41.550,00 USD[cite: 5].

#### 🔍 Análisis de Vulnerabilidades por Canal
* **Zelle ($21.000,00):** Mayor severidad financiera con disputas abiertas por sospecha de fraude y saldo liquidado en cero[cite: 5].
* **PayPal ($11.500,00):** Disputas activas por patrones de reincidencia en montos altos sin recuperación de fondos[cite: 5].
* **Stripe ($9.050,00):** Brecha de conciliación con abonos y comisiones fantasmas sobre transacciones declinadas[cite: 5].
* **Pago Móvil:** Operatividad regular y conforme a los parámetros de tolerancia al riesgo[cite: 5].

#### 🚨 Matriz de Riesgo y Bloqueo Obligatorio (15 Usuarios Identificados)
Se identificaron 15 usuarios asociados al segmento de alto riesgo (puntajes crediticios entre 350 y 410, ingresos menores a 1.200,00 USD y banderas rojas de fraude activo)[cite: 5]:
* **Bloque Zelle:** USR-207, USR-217, USR-227, USR-237, USR-247[cite: 5].
* **Bloque PayPal:** USR-202, USR-212, USR-222, USR-232, USR-242[cite: 5].
* **Bloque Stripe:** USR-204, USR-214, USR-224, USR-234, USR-244[cite: 5].

#### ✅ Recomendaciones Obligatorias de Mitigación
1. **Bloqueo preventivo inmediato** e inmovilización de fondos para las 15 cuentas listadas para detener nuevos contracargos[cite: 5].
2. **Suspensión temporal de límites** para transacciones mayores a 2.000,00 USD en Zelle y PayPal sujetas a autenticación reforzada[cite: 5].
3. **Ajuste contable correctivo** para depurar los 9.050,00 USD erróneos en la conciliación de Stripe[cite: 5].
""")
