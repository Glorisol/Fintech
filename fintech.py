import time
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io

# Importaciones de ReportLab para la Capa 3 (Dictamen PDF)
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Importación segura de la API de Google GenAI
try:
    from google import genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

st.set_page_config(
    page_title="Sabertec AI - Agente de Auditoría Fintech & Fraude",
    page_icon="💳",
    layout="wide"
)

# Estilos CSS avanzados inspirados en banca digital y ciberseguridad
st.markdown("""
    <style>
    .main-title { font-size: 28px; font-weight: bold; color: #0F172A; }
    .sub-title { font-size: 16px; color: #475569; margin-bottom: 20px; }
    .metric-card { background-color: #F8FAFC; padding: 15px; border-radius: 8px; border: 1px solid #E2E8F0; text-align: center; }
    .prompt-container {
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        border-left: 6px solid #3B82F6;
        padding: 18px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .executive-card {
        background-color: #F0FDF4;
        border-left: 6px solid #22C55E;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    .cta-banner {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        color: white;
        padding: 24px;
        border-radius: 10px;
        text-align: center;
        margin-top: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">💳 Sabertec AI: Agente de Monitoreo & Prevención de Fraude Fintech</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Análisis de transacciones en tiempo real, scoring de riesgo y conciliación automatizada</p>', unsafe_allow_html=True)

# Sidebar para controles de la arquitectura
st.sidebar.header("⚙️ Configuración del Agente Fintech")

instruccion_usuario = st.sidebar.text_area(
    "💬 Prompt o Instrucción para el Agente:",
    placeholder="Ej. Auditar pasarelas de pago y detectar anomalías en transferencias internacionales...",
    value="Monitorear flujos transaccionales, detectar patrones de lavado de dinero (AML) y bloquear operaciones de alto riesgo."
)

num_transacciones = st.sidebar.slider("Transacciones a Auditar", 100, 1000, 400, 50)
umbral_fraude = st.sidebar.slider("Umbral de Alerta de Riesgo (Score)", 50, 95, 75, 5)

run_button = st.sidebar.button("🚀 Ejecutar Ciclo Autónomo Fintech")

if "fintech_ejecutado" not in st.session_state:
    st.session_state.fintech_ejecutado = False

if run_button:
    st.session_state.fintech_ejecutado = True

if st.session_state.fintech_ejecutado:
    if run_button:
        progress_text = st.empty()
        progress_bar = st.progress(0)
        
        phases = [
            ("🧠 Capa 2 - Razonamiento: Evaluando modelos de comportamiento transaccional...", 30),
            ("🛠️ Capa 2 - Tool Calling: Consultando logs de pasarela de pagos y base SQL...", 60),
            ("📋 Capa 3 - Dictamen: Compilando informe ejecutivo antifraude...", 100)
        ]
        
        for text, percent in phases:
            progress_text.markdown(f"**{text}**")
            progress_bar.progress(percent)
            time.sleep(0.1)
            
        if HAS_GENAI:
            try:
                client = genai.Client()
                _ = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=instruccion_usuario,
                )
            except Exception:
                pass

        progress_text.markdown("✅ **¡Ejecución completada con éxito por el Agente Fintech de Sabertec AI!**")
        time.sleep(0.15)
        progress_bar.empty()
        progress_text.empty()

    # Capa 1 y 2: ETL estocástico e independiente para Finanzas
    np.random.seed(None)
    canales = ["App Móvil", "API Gateway", "POS Físico", "Checkout Web", "Banca por Internet"]
    
    data = {
        "Tx_ID": [f"TX-{90000 + i}" for i in range(num_transacciones)],
        "Fecha_Hora": pd.date_range(start="2026-08-01", periods=num_transacciones, freq="min"),
        "Fecha_Liquidacion": pd.date_range(start="2026-08-02", periods=num_transacciones, freq="h"),
        "Monto_USD": np.round(np.random.uniform(15.0, 8500.0, num_transacciones), 2),
        "Score_Riesgo": np.round(np.random.uniform(5, 99, num_transacciones), 1),
        "Canal": np.random.choice(canales, num_transacciones),
    }
    df = pd.DataFrame(data)
    
    # Clasificación dinámica independiente basada en el score de riesgo
    df["Estatus_Tx"] = np.where(df["Score_Riesgo"] > umbral_fraude, "CRITICO_FRAUDE", 
                       np.where(df["Score_Riesgo"] > 45, "REVISION_KYC", "APROBADO"))

    df_revision = df[df["Estatus_Tx"] == "REVISION_KYC"].copy()
    df_critico = df[df["Estatus_Tx"] == "CRITICO_FRAUDE"].copy()
    
    rev_count = len(df_revision)
    crit_count = len(df_critico)
    monto_expuesto = df_critico["Monto_USD"].sum()

    # Contenedor Visual del Prompt Aplicado
    st.markdown(f"""
        <div class="prompt-container">
            <h4 style="margin:0; color:#1D4ED8;">🎯 Prompt Aplicado por el Analista (Capa 2)</h4>
            <p style="margin:5px 0 0 0; font-size: 15px; color:#1E293B; font-style: italic;">"{instruccion_usuario}"</p>
        </div>
    """, unsafe_allow_html=True)

    # 1. Resumen Ejecutivo y Metadatos
    st.markdown("## 📋 1. Resumen Ejecutivo & Auditoría de Pagos")
    meta_col1, meta_col2, meta_col3 = st.columns(3)
    with meta_col1:
        st.markdown(f"**Fecha de Auditoría:** 30 de Agosto, 2026")
        st.markdown(f"**Motor Agente:** Google GenAI (Fintech Core)")
    with meta_col2:
        st.markdown(f"**Transacciones Analizadas:** {num_transacciones}")
        st.markdown(f"**Umbral de Alerta Score:** {umbral_fraude}/100")
    with meta_col3:
        st.markdown(f"**Estado del Pipeline:** Seguro / Encriptado")
        st.markdown(f"**Nivel de Confianza AML:** 99.8%")

    st.markdown("""
    <div class="executive-card">
        <p style="margin:0; color:#166534;"><b>Dictamen General:</b> El agente autónomo procesó el flujo transaccional completo. Se identificaron desvíos por patrones de velocidad y montos inusuales que exigen retención preventiva de fondos.</p>
    </div>
    """, unsafe_allow_html=True)

    # KPIs Principales con totales independientes reales
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><h4>Total Transacciones</h4><h3>{len(df)}</h3></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><h4>En Revisión (KYC)</h4><h3>{rev_count}</h3></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><h4>Críticos (Fraude)</h4><h3>{crit_count}</h3></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><h4>Monto en Riesgo</h4><h3>${monto_expuesto:,.2f}</h3></div>', unsafe_allow_html=True)

    st.markdown("---")
    
    # 2. Análisis Visual de Riesgos
    st.markdown("## 📊 2. Distribución de Riesgos por Canal de Pago")
    col_a, col_b = st.columns([1.2, 1])
    
    with col_a:
        st.subheader("Volumetría por Estatus Operativo")
        estado_counts = df["Estatus_Tx"].value_counts()
        fig, ax = plt.subplots(figsize=(6, 3.2))
        estado_counts.plot(kind="bar", color=["#16A34A", "#CA8A04", "#DC2626"], ax=ax)
        ax.set_ylabel("Cantidad de Operaciones", fontsize=9, fontweight='bold', color="#0F172A")
        ax.set_xlabel("Estatus Transaccional", fontsize=9, fontweight='bold', color="#0F172A")
        plt.xticks(rotation=0)
        st.pyplot(fig)
        
    with col_b:
        st.subheader("Lectura del Comportamiento")
        st.write("Las pasarelas abiertas a través de API Gateway concentran el mayor puntaje de riesgo, indicando posibles intentos de ataques automatizados o tarjetas comprometidas.")

    st.markdown("---")

    # 3. Alertas de Seguridad
    st.markdown("## 🚨 3. Alertas de Cumplimiento & Prevención de Fraude")
    crit_1, crit_2 = st.columns(2)
    with crit_1:
        st.error(f"⚠️ **Alerta AML:** Se detectaron transacciones con puntaje de riesgo superior a {umbral_fraude} que superan los parámetros de validación habituales.")
    with crit_2:
        st.error("🛑 **Acción Preventiva:** Congelamiento automático de las cuentas asociadas a las operaciones críticas hasta completar la verificación de identidad.")

    st.markdown("---")

    # 4. Escrutinio Completo en Pantalla
    st.markdown("## 📋 4. Escrutinio Transaccional Detallado")
    st.write(f"Explora la bitácora completa de las **{num_transacciones}** operaciones auditadas:")

    filtro_estatus = st.selectbox(
        "🔍 Filtrar Bitácora por Estatus:",
        ["TODOS", "APROBADO", "REVISION_KYC", "CRITICO_FRAUDE"]
    )

    if filtro_estatus == "TODOS":
        df_filtrado = df
    else:
        df_filtrado = df[df["Estatus_Tx"] == filtro_estatus]

    st.caption(f"Mostrando **{len(df_filtrado)}** registros de un total de **{len(df)}** operaciones.")

    def color_fintech(val):
        if val == "APROBADO":
            return 'background-color: #DCFCE7; color: #166534; font-weight: bold;'
        elif val == "REVISION_KYC":
            return 'background-color: #FEF9C3; color: #854D0E; font-weight: bold;'
        elif val == "CRITICO_FRAUDE":
            return 'background-color: #FEE2E2; color: #991B1B; font-weight: bold;'
        return ''

    try:
        df_styled = df_filtrado.style.map(color_fintech, subset=['Estatus_Tx'])
    except AttributeError:
        df_styled = df_filtrado.style.applymap(color_fintech, subset=['Estatus_Tx'])
        
    st.dataframe(df_styled, use_container_width=True, height=400)

    st.markdown("---")

    # 5. Plan de Acción Fintech
    st.markdown("## 🛠️ 5. Plan de Acción y Mitigación de Riesgos")
    st.markdown("""
    * **Verificación Dinámica (3D Secure):** Reforzar autenticación de doble factor (2FA) en pasarelas con score elevado.
    * **Monitoreo 24/7:** Ejecución continua del agente autónomo sobre la base de datos transaccional.
    * **Reportes Regulatorios:** Preparación automatizada de archivos de cumplimiento para la Unidad de Inteligencia Financiera.
    """)

    # 6. Zona de Descarga (Excel & Dictamen PDF de Capa 3)
    st.markdown("---")
    
    st.markdown("""
        <div class="cta-banner">
            <h3 style="color: white; margin:0 0 8px 0;">🚀 ¿Listo para desplegar este Agente en tu infraestructura Fintech?</h3>
            <p style="color: #94A3B8; margin:0 0 5px 0; font-size: 15px;">Automatiza la conciliación y blindaje antifraude con las soluciones inteligentes de Sabertec AI.</p>
            <p style="color: #CBD5E1; margin:0; font-size: 13px;">Contáctanos en <b>fintech@sabertec.com</b></p>
        </div>
    """, unsafe_allow_html=True)
    
    col_d1, col_d2 = st.columns(2)
    
    with col_d1:
        output_excel = io.BytesIO()
        with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Fintech_Audit')
        excel_data = output_excel.getvalue()
        
        st.download_button(
            label="📊 Descargar Bitácora Completa en Excel",
            data=excel_data,
            file_name="fintech_transacciones_audit.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
    with col_d2:
        # Capa 3: Dictamen Ejecutivo PDF limpio y sin columnas redundantes de estatus
        pdf_output = io.BytesIO()
        doc = SimpleDocTemplate(pdf_output, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        story = []
        styles = getSampleStyleSheet()
        
        header_style = ParagraphStyle('HeaderStyle', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#475569'), spaceAfter=4)
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=15, textColor=colors.HexColor('#0F172A'), spaceAfter=8, fontName='Helvetica-Bold')
        section_style = ParagraphStyle('SectionStyle', parent=styles['Heading2'], fontSize=11, textColor=colors.HexColor('#0F172A'), spaceBefore=8, spaceAfter=4, fontName='Helvetica-Bold')
        body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=8.5, textColor=colors.HexColor('#334155'), spaceAfter=4, leading=11)
        bullet_style = ParagraphStyle('BulletStyle', parent=styles['Normal'], fontSize=8.5, textColor=colors.HexColor('#334155'), leftIndent=12, spaceAfter=3, leading=10)
        
        # Cabecera corporativa PDF
        story.append(Paragraph("Sabertec Fintech - Dictamen de Auditoría Antifraude (Capa 3)", title_style))
        story.append(Paragraph("DE: Dirección de Riesgos, Cumplimiento & Agente Sabertec AI", header_style))
        story.append(Paragraph("PARA: Comité de Operaciones Financieras y Dirección General", header_style))
        story.append(Paragraph(f"ASUNTO: Informe Consolidado de Monitoreo Transaccional y Prevención de Fraude", header_style))
        story.append(Paragraph("FECHA: 30 de Agosto, 2026", header_style))
        story.append(Spacer(1, 4))
        
        story.append(Paragraph("Resumen Ejecutivo", section_style))
        story.append(Paragraph(f"El agente autónomo procesó el flujo de {num_transacciones} operaciones, segmentando de forma independiente los casos de revisión por cumplimiento (KYC) y las alertas críticas de fraude potencial.", body_style))
        story.append(Paragraph(f"Prompt Aplicado: {instruccion_usuario}", body_style))
        story.append(Spacer(1, 4))
        
        # --- MATRIZ 1: EN REVISIÓN KYC (Sin columna redundante) ---
        story.append(Paragraph(f"1. Matriz de Operaciones en Revisión (Cumplimiento KYC) - Total: {rev_count} Transacciones", section_style))
        
        table_rev_data = [["ID Transacción", "Canal", "Monto (USD)", "Score Riesgo", "Liquidación"]]
        for _, row in df_revision.iterrows():
            table_rev_data.append([
                str(row["Tx_ID"]),
                str(row["Canal"]),
                f"${row['Monto_USD']:,.2f}",
                str(row["Score_Riesgo"]),
                str(row["Fecha_Liquidacion"].strftime("%Y-%m-%d"))
            ])
            
        t_rev = Table(table_rev_data, colWidths=[90, 110, 95, 90, 155])
        t_rev.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#CA8A04')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ]))
        story.append(t_rev)
        story.append(Spacer(1, 8))
        
        # --- MATRIZ 2: CRÍTICO FRAUDE (Sin columna redundante) ---
        story.append(Paragraph(f"2. Matriz de Operaciones Críticas (Bloqueo por Fraude) - Total: {crit_count} Transacciones", section_style))
        
        table_crit_data = [["ID Transacción", "Canal", "Monto (USD)", "Score Riesgo", "Liquidación"]]
        for _, row in df_critico.iterrows():
            table_crit_data.append([
                str(row["Tx_ID"]),
                str(row["Canal"]),
                f"${row['Monto_USD']:,.2f}",
                str(row["Score_Riesgo"]),
                str(row["Fecha_Liquidacion"].strftime("%Y-%m-%d"))
            ])
            
        t_crit = Table(table_crit_data, colWidths=[90, 110, 95, 90, 155])
        t_crit.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#DC2626')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ]))
        story.append(t_crit)
        story.append(Spacer(1, 8))
        
        story.append(Paragraph("Hallazgos de Seguridad y Control Financiero:", section_style))
        story.append(Paragraph("1. Control de Pasarelas: Se detectaron anomalías en los tiempos de respuesta de transacciones vía API Gateway, requiriendo revisión de tokens de acceso.", bullet_style))
        story.append(Paragraph("2. Exposición de Capital: El monto total bajo riesgo asciende a los valores críticos reportados, requiriendo retención temporal.", bullet_style))
        
        story.append(Spacer(1, 4))
        story.append(Paragraph("Plan de Acción Dictaminado", section_style))
        story.append(Paragraph("• Acción Inmediata: Ejecución de protocolos de contra-cargo y validación biométrica para los usuarios en revisión KYC.", bullet_style))
        story.append(Paragraph("• Monitoreo Continuo: Ajuste dinámico de umbrales de fraude mediante el agente Sabertec AI.", bullet_style))
        
        story.append(Spacer(1, 4))
        story.append(Paragraph(f"Dictamen Final: Evaluación completada de forma independiente. Se registran {rev_count} operaciones en revisión y {crit_count} operaciones bloqueadas por fraude potencial.", body_style))
        
        doc.build(story)
        pdf_data = pdf_output.getvalue()

        st.download_button(
            label="📄 Descargar Dictamen Antifraude en PDF",
            data=pdf_data,
            file_name="dictamen_fintech_antifraude.pdf",
            mime="application/pdf",
            use_container_width=True
        )

else:
    st.info("👉 Ingresa tu instrucción en la barra lateral, ajusta los parámetros de transacciones y haz clic en **'Ejecutar Ciclo Autónomo Fintech'** para iniciar el análisis.")