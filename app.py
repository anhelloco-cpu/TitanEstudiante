import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import json

# 1. --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Titán Estudiante - Dashboard", layout="wide", page_icon="🛡️")

# Inicializar estados de la IA
if 'view' not in st.session_state: st.session_state['view'] = 'dashboard'
if 'df_adn' not in st.session_state: st.session_state['df_adn'] = None
if 'mision_ia' not in st.session_state: st.session_state['mision_ia'] = ""

# --- 2. ESTILOS VISUALES (Fondo Blanco Moderno) ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #2b2d33; }
    [data-testid="stSidebar"] { background-color: #f7f7f7; }
    .stMetric { background-color: #ffffff; border: 1px solid #d1d5db; padding: 10px; border-radius: 12px; }
    .alerta-daño { color: #ff4b4b; font-weight: bold; animation: pulse 1.5s infinite; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    .pergamino { background-color: #fff9eb; color: #2b2d33; padding: 25px; border: 1px solid #d4af37; border-left: 8px solid #d4af37; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONEXIÓN: LLAVE MAESTRA ---
with st.sidebar:
    st.header("🛡️ ACCESO AL SANTUARIO")
    with st.expander("🔑 LLAVE MAESTRA", expanded=True):
        key = st.text_input("API Key (Cualquiera):", type="password")
        if key:
            try:
                genai.configure(api_key=key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                st.success("Oráculo Conectado")
            except Exception as e:
                st.error(f"Error de conexión: {e}")

# --- 4. MOTOR DE ADN INTELIGENTE (IA Descifrando el Excel) ---
def descifrar_adn_con_ia(file):
    if not key:
        st.error("Introduce la Llave Maestra para despertar el motor.")
        return None

    try:
        # Leemos el archivo y mandamos una muestra a la IA
        df_raw = pd.read_excel(file)
        data_preview = df_raw.head(25).to_csv(index=False)
        
        # El Prompt maestro que analiza el formato
        prompt = f"""
        Eres el 'Decodificador de ADN Académico'. Analiza estos datos:
        {data_preview}

        TAREA:
        1. Identifica las notas de: Matemáticas, Lectura Crítica, Ciencias Naturales, Sociales y Ciudadanas, Inglés.
        2. Si el archivo es del ICFES (puntajes 0-100 o 0-500), normaliza a escala 0.0-5.0.
        3. Si el archivo es de Colegio (puntajes 0-5), mantenlo así.
        4. Si una materia tiene varios componentes (ej. Química, Física), saca el promedio.
        5. Devuelve EXCLUSIVAMENTE un JSON puro (sin texto extra):
        [
          {{"Área": "Matemáticas", "Puntaje": 4.2}},
          ...
        ]
        """
        response = model.generate_content(prompt)
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        adn_data = json.loads(clean_json)
        
        # Mapeo de piezas de armadura
        mapeo = {"Matemáticas": "Peto", "Lectura Crítica": "Yelmo", "Ciencias Naturales": "Grebas", "Sociales y Ciudadanas": "Escudo", "Inglés": "Guantelete"}
        for i in adn_data:
            i["Pieza"] = mapeo.get(i["Área"], "Accesorio")
            i["Estado"] = "Oro" if i["Puntaje"] >= 4.5 else "Plata" if i["Puntaje"] >= 3.8 else "Bronce"
            i["Salud"] = int((i["Puntaje"] / 5) * 100)
        return pd.DataFrame(adn_data)
    except Exception as e:
        st.error(f"El Titán no pudo leer el pergamino: {e}")
        return None

# --- 5. NAVEGACIÓN ---
if st.session_state['view'] == 'mision':
    st.markdown("## ⚒️ FORJA DE REPARACIÓN")
    st.markdown(f'<div class="pergamino">{st.session_state["mision_ia"]}</div>', unsafe_allow_html=True)
    if st.button("VOLVER AL DASHBOARD"):
        st.session_state['view'] = 'dashboard'
        st.rerun()

else:
    st.title("🛡️ TITÁN ESTUDIANTE: El Despertar")
    archivo = st.file_uploader("Cargue el ADN Académico (Miguel o Salvador)", type=["xlsx"])

    if archivo:
        # Solo procesamos si hay cambio de archivo o primera carga
        if st.session_state['df_adn'] is None:
            with st.spinner("La IA está descifrando el ADN..."):
                st.session_state['df_adn'] = descifrar_adn_con_ia(archivo)
        
        df_adn = st.session_state['df_adn']
        if df_adn is not None:
            promedio_gral = df_adn['Puntaje'].mean()
            color_r = "#d4af37" if promedio_gral >= 4.5 else "#7f8c8d" if promedio_gral >= 3.8 else "#a0522d"
            
            with st.sidebar:
                st.image("https://www.freepik.com/premium-psd/ornate-medieval-armor-knights-cuirass_412654456.htm", use_column_width=True)
                st.metric("PODER TOTAL", round(promedio_gral, 2))
                st.divider()
                st.write("📍 **Clan:** Grado 11-A")

            col1, col2 = st.columns([1, 1])
            with col1:
                st.subheader("⚔️ Inventario de Armadura")
                for _, row in df_adn.iterrows():
                    c_txt = "#ff4b4b" if row['Estado'] == "Bronce" else "#00262e"
                    alerta = " | <span class='alerta-daño'>¡PIEZA DAÑADA!</span>" if row['Estado'] == "Bronce" else f" | Nivel {row['Estado']}"
                    st.markdown(f"<span style='color: {c_txt};'>**{row['Pieza']}** ({row['Área']}): **{row['Puntaje']}**</span>{alerta}", unsafe_allow_html=True)
                    st.progress(row['Salud'] / 100)

                fig = px.line_polar(df_adn, r='Puntaje', theta='Área', line_close=True, range_r=[0,5])
                fig.update_traces(fill='toself', line_color=color_r)
                fig.update_layout(polar=dict(bgcolor="white"), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("🧠 Diagnóstico de la IA")
                vulnerables = df_adn[df_adn['Puntaje'] < 3.8]
                if not vulnerables.empty:
                    for _, row in vulnerables.iterrows():
                        st.error(f"⚠️ **Debilidad:** {row['Pieza']} ({row['Área']})")
                    
                    if st.button("🔥 Forjar Reparación"):
                        with st.spinner("Creando misión personalizada..."):
                            area_debil = vulnerables.loc[vulnerables['Puntaje'].idxmin()]['Área']
                            res = model.generate_content(f"Crea un reto tipo ICFES de {area_debil} con un texto de análisis y pregunta A,B,C,D.")
                            st.session_state['mision_ia'] = res.text
                            st.session_state['view'] = 'mision'
                            st.rerun()
                else:
                    st.success("✅ Integridad Total. Armadura de Leyenda.")