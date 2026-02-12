import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import json

# 1. --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Titán Estudiante - Dashboard", layout="wide", page_icon="🛡️")

# Inicializar estados
if 'view' not in st.session_state: st.session_state['view'] = 'dashboard'
if 'mision_ia' not in st.session_state: st.session_state['mision_ia'] = ""
if 'df_adn' not in st.session_state: st.session_state['df_adn'] = None

# --- 2. ESTILOS VISUALES (Fondo Blanco) ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #2b2d33; }
    [data-testid="stSidebar"] { background-color: #f7f7f7; }
    .stMetric { background-color: #f7f7f7; border: 1px solid #d1d5db; padding: 10px; border-radius: 12px; }
    .alerta-daño { color: #ff4b4b; font-weight: bold; animation: pulse 1.5s infinite; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    .pergamino { background-color: #fff9eb; color: #2b2d33; padding: 25px; border-radius: 10px; border: 1px solid #d4af37; border-left: 8px solid #d4af37; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONEXIÓN AL ORÁCULO (IA) ---
with st.sidebar:
    st.header("🔑 Conexión IA")
    user_api_key = st.text_input("Pega tu API Key de Gemini:", type="password", key="key_input")
    if user_api_key:
        try:
            genai.configure(api_key=user_api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            st.success("Oráculo Conectado")
        except Exception as e:
            st.error(f"Error: {e}")

# --- 4. MOTOR DE ADN INTELIGENTE (IA DESCIFRANDO EL EXCEL) ---
def procesar_adn_con_ia(file):
    if not user_api_key:
        st.error("Debes conectar la API Key para que la IA descifre este archivo.")
        return None

    try:
        # Leemos las primeras filas para que la IA entienda el formato
        df_raw = pd.read_excel(file)
        # Convertimos una muestra de los datos a texto para la IA
        data_sample = df_raw.head(20).to_csv(index=False)
        column_names = list(df_raw.columns)

        prompt = f"""
        Actúa como un experto en analítica educativa. Te voy a pasar una muestra de datos de un estudiante:
        COLUMNAS: {column_names}
        DATOS: {data_sample}

        TAREA:
        1. Identifica qué columnas o filas corresponden a estas 5 áreas del ICFES: 
           Matemáticas, Lectura Crítica, Ciencias Naturales, Sociales y Ciudadanas, Inglés.
        2. Calcula el puntaje promedio para cada área.
        3. IMPORTANTE: Si el archivo usa escala 0-100 o 0-500, normalízalo a escala de 0.0 a 5.0.
        4. Devuelve ÚNICAMENTE un JSON con este formato:
        [
          {{"Área": "Matemáticas", "Puntaje": 4.2}},
          ...
        ]
        """
        
        response = model.generate_content(prompt)
        # Limpiar la respuesta de la IA (quitar bloques de código si los hay)
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        adn_list = json.loads(clean_json)
        
        # Enriquecer los datos para el resto de la app
        mapeo_p = {"Matemáticas": "Peto", "Lectura Crítica": "Yelmo", "Ciencias Naturales": "Grebas", "Sociales y Ciudadanas": "Escudo", "Inglés": "Guantelete"}
        for item in adn_list:
            item["Pieza"] = mapeo_p.get(item["Área"], "Accesorio")
            item["Estado"] = "Oro" if item["Puntaje"] >= 4.5 else "Plata" if item["Puntaje"] >= 3.8 else "Bronce"
            item["Salud"] = int((item["Puntaje"] / 5) * 100)

        return pd.DataFrame(adn_list)
    except Exception as e:
        st.error(f"El Titán no pudo descifrar el ADN: {e}")
        return None

def generar_mision_con_ia(area):
    prompt = f"Genera un reto ICFES de {area} con texto, pregunta A,B,C,D y explicación técnica."
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Fallo en la forja: {e}"

# --- 5. NAVEGACIÓN ---
if st.session_state['view'] == 'mision':
    st.markdown("## ⚒️ FORJA DE REPARACIÓN")
    st.markdown(f'<div class="pergamino">{st.session_state["mision_ia"]}</div>', unsafe_allow_html=True)
    if st.button("VOLVER AL DASHBOARD"):
        st.session_state['view'] = 'dashboard'
        st.rerun()

else:
    st.title("🛡️ TITÁN ESTUDIANTE: El Despertar")
    st.markdown("---")
    archivo = st.file_uploader("Cargue el archivo de Notas (Cualquier formato)", type=["xlsx"])

    if archivo:
        # Solo procesamos si los datos no han sido cargados o es un archivo nuevo
        if st.session_state['df_adn'] is None:
            with st.spinner("La IA está descifrando el ADN Académico..."):
                st.session_state['df_adn'] = procesar_adn_con_ia(archivo)
        
        df_adn = st.session_state['df_adn']
        
        if df_adn is not None:
            promedio_gral = df_adn['Puntaje'].mean()
            
            # Avatar y Rango
            if promedio_gral >= 4.5: rango, color_r = "TITÁN LEGENDARIO", "#d4af37"
            elif promedio_gral >= 3.8: rango, color_r = "GUERRERO VETERANO", "#7f8c8d"
            else: rango, color_r = "RECLUTA EN FORJA", "#a0522d"
            
            with st.sidebar:
                st.markdown(f"<h1 style='text-align: center; color: {color_r};'>{rango}</h1>", unsafe_allow_html=True)
                st.image("https://www.freepik.com/premium-psd/ornate-medieval-armor-knights-cuirass_412654456.htm", use_column_width=True)
                st.metric("PODER TOTAL", round(promedio_gral, 2))

            col1, col2 = st.columns([1, 1])
            with col1:
                st.subheader("⚔️ Inventario de Armadura")
                for _, row in df_adn.iterrows():
                    color_txt = "#ff4b4b" if row['Estado'] == "Bronce" else "#00262e"
                    alerta = " | <span class='alerta-daño'>¡PIEZA DAÑADA!</span>" if row['Estado'] == "Bronce" else f" | Nivel {row['Estado']}"
                    st.markdown(f"<span style='color: {color_txt};'>**{row['Pieza']}** ({row['Área']}): **{row['Puntaje']}**</span>{alerta}", unsafe_allow_html=True)
                    st.progress(row['Salud'] / 100)
                
                fig = px.line_polar(df_adn, r='Puntaje', theta='Área', line_close=True, range_r=[0,5])
                fig.update_traces(fill='toself', line_color=color_r)
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", polar=dict(bgcolor="white"))
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("🧠 Diagnóstico de la IA")
                vulnerables = df_adn[df_adn['Puntaje'] < 3.8]
                if not vulnerables.empty:
                    for _, row in vulnerables.iterrows():
                        st.error(f"⚠️ **Debilidad:** {row['Pieza']} ({row['Área']})")
                    
                    st.divider()
                    st.subheader("⚒️ Taller de Mentores")
                    mas_critica = vulnerables.loc[vulnerables['Puntaje'].idxmin()]
                    
                    if st.button(f"🔥 Forjar Reparación: {mas_critica['Área']}"):
                        with st.spinner("Generando desafío personalizado..."):
                            st.session_state['mision_ia'] = generar_mision_con_ia(mas_critica['Área'])
                            st.session_state['view'] = 'mision'
                            st.rerun()
                else:
                    st.success("✅ Integridad Total.")