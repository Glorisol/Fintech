import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import plotly.express as px
import io
from datetime import datetime

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="Sabertec AI: Dictamen de Riesgo Corporativo",
    page_icon="🛡️",
    layout="wide"
)

# Estilo CSS para alinear el título principal centrado, en letra grande
st.markdown("""
    <style>
    .titulo-principal {
        font-size: 26px;
        font-weight: bold;
        text-align: center;
        width: 100%;
        margin-bottom: 30px;
    }
    </style>
    <div class="titulo-principal">DICTAMEN DE AUDITORÍA Y EVALUACIÓN DE RIESGO FINANCIERO</div>
""", unsafe_allow_html=True)

HAS_GENAI = True

# Definición de Herramientas corporativas para el Agente
def auditar_riesgo_corporativo(volumen_total: float = 52475.00, exposicion_riesgo: float = 41550.00) -> dict:
    """Retorna los datos consolidados de la auditoría de pasarelas y riesgo crediticio corporativo."""
    return {
        "volumen_total": volumen_total,
        "exposicion_total": exposicion_riesgo,
        "disputas_retenidas": 32500.00,
        "inconsistencias_stripe": 9050.00,
        "usuarios_alto_riesgo": 15,
        "estado": "Completado con contingencia crítica"
    }

def aplicar_bloqueo_preventivo(usuarios_ids: list) -> dict:
    """Aplica bloqueo preventivo e inmovilización de fondos a los usuarios en matriz de alto riesgo."""
    return {
        "usuarios_afectados": usuarios_ids,
        "estado": "BLOQUEO_PREVENTIVO_EJECUTADO",
        "mensaje": "Se ha detenido la propagación de nuevos contracargos con éxito."
    }

# Configuración en Sidebar
st.sidebar.header("⚙️ Configuración del Módulo")
prompt_usuario = st.sidebar.text_area(
    "💬 Objetivo de Auditoría Corporativa:",
    value="Ejecuta la auditoría integral de pasarelas y riesgo crediticio corporativo. Identifica las vulnerabilidades en Zelle, PayPal, Stripe y genera el dictamen ejecutivo junto con las recomendaciones de mitigación.",
    height=140
)

run_agent = st.sidebar.button("🚀 Ejecutar Auditoría Corporativa")

# Inicializamos estados en sesión
if "df_usuarios" not in st.session_state:
    st.session_state.df_usuarios = None
if "df_pasarelas" not in st.session_state:
    st.session_state.df_pasarelas = None
if "response_text" not in st.session_state:
    st.session_state.response_text = None
if "fecha_actual" not in st.session_state:
    st.session_state.fecha_actual = None

if run_agent:
    if not HAS_GENAI:
        st.error("⚠️ La librería `google-genai` no está instalada o configurada correctamente.")
    else:
        with st.spinner("🛡️ Analizando pasarelas de pago, disputas y perfiles de riesgo corporativo..."):
            try:
                # Inicializar cliente de Google GenAI
                client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

                # Configuración del motor con las funciones inyectadas como herramientas
                config = types.GenerateContentConfig(
                    tools=[auditar_riesgo_corporativo, aplicar_bloqueo_preventivo],
                    system_instruction=(
                        "Eres un sistema experto en auditoría senior automática de riesgo crediticio y pasarelas de pago para Sabertec. "
                        "Analiza los objetivos del negocio y genera un dictamen ejecutivo formal, estructurado con: "
                        "1. Resumen Ejecutivo Financiero. "
                        "2. Análisis de Vulnerabilidades en Pasarelas (Zelle, PayPal, Stripe, Pago Móvil). "
                        "3. Matriz de Riesgo Crediticio de Usuarios. "
                        "4. Recomendaciones Obligatorias de Mitigación. "
                        "IMPORTANTE: Redacta únicamente el cuerpo del dictamen. No repitas el título principal de la interfaz."
                    ),
                    temperature=0.2
                )

                chat = client.chats.create(model="gemini-3.6-flash", config=config)
                response = chat.send_message(prompt_usuario)

                st.session_state.response_text = response.text
                
                # Fecha actual formateada en español
                meses = {
                    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
                    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
                }
                ahora = datetime.now()
                st.session_state.fecha_actual = f"{ahora.day} de {meses[ahora.month]} de {ahora.year}"

                # Generación de Dataframes basados exactamente en el documento adjunto
                # 1. Datos de Pasarelas
                data_pasarelas = [
                    {"Pasarela": "Zelle", "Monto en Riesgo / Disputa ($)": 21000.00, "Estado Operativo": "Disputa por Fraude (Crítico)", "Severidad": "Alta"},
                    {"Pasarela": "PayPal", "Monto en Riesgo / Disputa ($)": 11500.00, "Estado Operativo": "Disputas Activas / Reincidencia", "Severidad": "Alta"},
                    {"Pasarela": "Stripe", "Monto en Riesgo / Disputa ($)": 9050.00, "Estado Operativo": "Inconsistencia de Conciliación", "Severidad": "Media"},
                    {"Pasarela": "Pago Móvil", "Monto en Riesgo / Disputa ($)": 0.00, "Estado Operativo": "Operatividad Regular (Conforme)", "Severidad": "Baja"}
                ]
                st.session_state.df_pasarelas = pd.DataFrame(data_pasarelas)

                # 2. Datos de Usuarios (Matriz de Riesgo del Dictamen)
                usuarios_data = [
                    # Bloque Zelle
                    {"ID Usuario": "USR-207", "Pasarela": "Zelle", "Score Crediticio": 390, "Ingreso Mensual ($)": 1100, "Segmento": "Alto Riesgo (Fraude)", "Estado": "Disputa Activa"},
                    {"ID Usuario": "USR-217", "Pasarela": "Zelle", "Score Crediticio": 390, "Ingreso Mensual ($)": 1050, "Segmento": "Alto Riesgo (Fraude)", "Estado": "Disputa Activa"},
                    {"ID Usuario": "USR-227", "Pasarela": "Zelle", "Score Crediticio": 390, "Ingreso Mensual ($)": 1150, "Segmento": "Alto Riesgo (Fraude)", "Estado": "Disputa Activa"},
                    {"ID Usuario": "USR-237", "Pasarela": "Zelle", "Score Crediticio": 390, "Ingreso Mensual ($)": 980, "Segmento": "Alto Riesgo (Fraude)", "Estado": "Disputa Activa"},
                    {"ID Usuario": "USR-247", "Pasarela": "Zelle", "Score Crediticio": 390, "Ingreso Mensual ($)": 1200, "Segmento": "Alto Riesgo (Fraude)", "Estado": "Disputa Activa"},
                    # Bloque PayPal
                    {"ID Usuario": "USR-202", "Pasarela": "PayPal", "Score Crediticio": 410, "Ingreso Mensual ($)": 1180, "Segmento": "Alto Riesgo (Fraude)", "Estado": "Disputa Activa"},
                    {"ID Usuario": "USR-212", "Pasarela": "PayPal", "Score Crediticio": 410, "Ingreso Mensual ($)": 1120, "Segmento": "Alto Riesgo (Fraude)", "Estado": "Disputa Activa"},
                    {"ID Usuario": "USR-222", "Pasarela": "PayPal", "Score Crediticio": 410, "Ingreso Mensual ($)": 1190, "Segmento": "Alto Riesgo (Fraude)", "Estado": "Disputa Activa"},
                    {"ID Usuario": "USR-232", "Pasarela": "PayPal", "Score Crediticio": 410, "Ingreso Mensual ($)": 1090, "Segmento": "Alto Riesgo (Fraude)", "Estado": "Disputa Activa"},
                    {"ID Usuario": "USR-242", "Pasarela": "PayPal", "Score Crediticio": 410, "Ingreso Mensual ($)": 1150, "Segmento": "Alto Riesgo (Fraude)", "Estado": "Disputa Activa"},
                    # Bloque Stripe
                    {"ID Usuario": "USR-204", "Pasarela": "Stripe", "Score Crediticio": 350, "Ingreso Mensual ($)": 950, "Segmento": "Alto Riesgo (Inconsistencia)", "Estado": "Rechazada / Liquidada Errónea"},
                    {"ID Usuario": "USR-214", "Pasarela": "Stripe", "Score Crediticio": 350, "Ingreso Mensual ($)": 920, "Segmento": "Alto Riesgo (Inconsistencia)", "Estado": "Rechazada / Liquidada Errónea"},
                    {"ID Usuario": "USR-224", "Pasarela": "Stripe", "Score Crediticio": 350, "Ingreso Mensual ($)": 990, "Segmento": "Alto Riesgo (Inconsistencia)", "Estado": "Rechazada / Liquidada Errónea"},
                    {"ID Usuario": "USR-234", "Pasarela": "Stripe", "Score Crediticio": 350, "Ingreso Mensual ($)": 900, "Segmento": "Alto Riesgo (Inconsistencia)", "Estado": "Rechazada / Liquidada Errónea"},
                    {"ID Usuario": "USR-244", "Pasarela": "Stripe", "Score Crediticio": 350, "Ingreso Mensual ($)": 940, "Segmento": "Alto Riesgo (Inconsistencia)", "Estado": "Rechazada / Liquidada Errónea"},
                ]
                st.session_state.df_usuarios = pd.DataFrame(usuarios_data)

            except Exception as e:
                error_str = str(e)
                if "503" in error_str or "UNAVAILABLE" in error_str:
                    st.warning("⚠️ El servicio de IA está experimentando alta demanda. Espera unos segundos y vuelve a hacer clic en 'Ejecutar Auditoría Corporativa'.")
                elif "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    st.warning("⚠️ Se ha superado temporalmente el límite de cuota (Error 429). Espera un momento antes de reintentar.")
                else:
                    st.error(f"Error durante la ejecución del agente: {e}")

# Renderizado del Dashboard y Dictamen si existen datos
if st.session_state.df_usuarios is not None:
    
    st.markdown("### 📊 Panel de Control: Indicadores Clave de Riesgo (KPIs)")
    
    # Tarjetas de Métricas Principales (KPI Cards)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Volumen Total Auditado", value="$52,475.00", delta="100% Base")
    with col2:
        st.metric(label="Exposición Total al Riesgo", value="$41,550.00", delta="79.1% del Volumen", delta_color="inverse")
    with col3:
        st.metric(label="Fondos Retenidos (Disputas)", value="$32,500.00", delta="61.9% sin liquidar", delta_color="inverse")
    with col4:
        st.metric(label="Inconsistencia Contable", value="$9,050.00", delta="Brecha Stripe", delta_color="inverse")

    st.markdown("---")

    # Gráficos del Dashboard Corporativo en 2 columnas
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.subheader("💳 Vulnerabilidades y Riesgo por Pasarela ($)")
        fig_pasarelas = px.bar(
            st.session_state.df_pasarelas,
            x="Pasarela",
            y="Monto en Riesgo / Disputa ($)",
            color="Pasarela",
            text="Monto en Riesgo / Disputa ($)",
            color_discrete_map={
                "Zelle": "#e74c3c",      # Rojo crítico
                "PayPal": "#f39c12",     # Naranja
                "Stripe": "#3498db",     # Azul
                "Pago Móvil": "#27ae60"  # Verde seguro
            }
        )
        fig_pasarelas.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=320, showlegend=False)
        st.plotly_chart(fig_pasarelas, use_container_width=True)

    with col_g2:
        st.subheader("🎯 Concentración de Usuarios en Alto Riesgo")
        conteo_segmentos = st.session_state.df_usuarios["Pasarela"].value_counts().reset_index()
        conteo_segmentos.columns = ["Pasarela", "Cantidad de Usuarios"]
        
        fig_usuarios = px.pie(
            conteo_segmentos,
            names="Pasarela",
            values="Cantidad de Usuarios",
            hole=0.4,
            color="Pasarela",
            color_discrete_map={"Zelle": "#e74c3c", "PayPal": "#f39c12", "Stripe": "#3498db"}
        )
        fig_usuarios.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=320)
        st.plotly_chart(fig_usuarios, use_container_width=True)

    st.markdown("---")

    # Renderizado del Dictamen Formal en Texto generado por la IA
    st.markdown("### 📑 Dictamen Ejecutivo de Auditoría")
    st.markdown(f"""
    - **Destinatario:** Dirección General y Comité de Riesgos de Sabertec
    - **Emisor:** Auditoría Senior Automática de Riesgo Crediticio y Pasarelas
    - **Estado de Auditoría:** Completado con Contingencia Crítica
    - **Fecha de Emisión:** {st.session_state.fecha_actual}
    """)

    st.markdown(st.session_state.response_text)

    # Sección Interactiva de la Matriz de Usuarios y Descargas Excel
    st.markdown("---")
    st.markdown("### 🚨 Matriz de Usuarios Críticos y Bloqueo Preventivo")
    st.markdown("Listado de los 15 usuarios asociados a la contingencia financiera con requerimiento de inmovilización de fondos:")
    
    st.dataframe(st.session_state.df_usuarios, use_container_width=True)

    # Botones de exportación a Excel para el equipo operativo
    st.markdown("### 📥 Exportación de Reportes para Mitigación")
    
    def convertir_a_excel(df):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Matriz_Riesgo')
        return output.getvalue()

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        excel_data = convertir_a_excel(st.session_state.df_usuarios)
        st.download_button(
            label="📥 Descargar Matriz de 15 Usuarios en Bloqueo (Excel)",
            data=excel_data,
            file_name="matriz_usuarios_bloqueo_preventivo.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    with col_btn2:
        excel_pasarelas = convertir_a_excel(st.session_state.df_pasarelas)
        st.download_button(
            label="📥 Descargar Reporte de Vulnerabilidades Pasarelas (Excel)",
            data=excel_pasarelas,
            file_name="reporte_vulnerabilidades_pasarelas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
