import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import json

# 1. --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Titán Estudiante - Dashboard", layout="wide", page_icon="🛡️")

# Persistencia de datos
if 'view' not in st.session_state: st.session_state['view'] = 'dashboard'
if 'df_adn' not in st.session_state: st.session_state['df_adn'] = None
if 'mision_ia' not in st.session_state: st.session_state['mision_ia'] = ""

# --- 2. ESTILOS (Fondo Blanco y Letras Oscuras) ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #2b2d33; }
    [data-testid="stSidebar"] { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; border: 1px solid #d1d5db; border-radius: 12px; }
    .alerta-daño { color: #ff4b4b; font-weight: bold; animation: pulse 1.5s infinite; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    .pergamino { background-color: #fffcf5; color: #2b2d33; padding: 25px; border-radius: 10px; border: 1px solid #d4af37; border-left: 8px solid #d4af37; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONEXIÓN: LLAVE MAESTRA (Tu formato original) ---
with st.sidebar:
    st.header("🛡️ ACCESO AL SANTUARIO")
    with st.expander("🔑 LLAVE MAESTRA", expanded=True):
        key = st.text_input("API Key (Cualquiera):", type="password")
        if key:
            try:
                genai.configure(api_key=key)
                # Intentamos el nombre más compatible para evitar el 404
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    # Prueba rápida silenciosa
                    model.generate_content("Hola")
                except:
                    model = genai.GenerativeModel('models/gemini-1.5-flash')
                st.success("Oráculo Conectado")
            except Exception as e:
                st.error(f"Error de conexión: {e}")

# --- 4. MOTOR DE ADN INTELIGENTE ---
def descifrar_adn_con_ia(file):
    if not key: return None
    try:
        df_raw = pd.read_excel(file)
        # Convertimos una muestra a CSV para que la IA entienda el formato de Miguel/Salvador
        data_preview = df_raw.head(25).to_csv(index=False)
        
        prompt = f"""
        Actúa como el 'Decodificador de ADN Académico'. Analiza estos datos:
        {data_preview}

        TAREA:
        1. Identifica las notas de: Matemáticas, Lectura Crítica, Ciencias Naturales, Sociales y Ciudadanas, Inglés.
        2. Detecta la escala: Si es 0-500 (ICFES), 0-100 o 0-5.
        3. Normaliza todo a una escala de 0.0 a 5.0.
        4. Si hay varios componentes (Física, Química), promedia.
        5. Devuelve EXCLUSIVAMENTE un JSON:
        [
          {{"Área": "Matemáticas", "Puntaje": 4.2}},
          ...
        ]
        """
        response = model.generate_content(prompt)
        # Limpieza de JSON
        raw_text = response.text.replace('```json', '').replace('```', '').strip()
        adn_data = json.loads(raw_text)
        
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
    archivo = st.file_uploader("Cargue el ADN Académico (Excel)", type=["xlsx"])

    if archivo:
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

            col1, col2 = st.columns([1, 1])
            with col1:
                st.subheader("⚔️ Inventario de Armadura")
                for _, row in df_adn.iterrows():
                    c_txt = "#ff4b4b" if row['Estado'] == "Bronce" else "#00262e"
                    st.markdown(f"<span style='color: {c_txt};'>**{row['Pieza']}** ({row['Área']}): **{row['Puntaje']}**</span>", unsafe_allow_html=True)
                    st.progress(row['Salud'] / 100)

                fig = px.line_polar(df_adn, r='Puntaje', theta='Área', line_close=True, range_r=[0,5])
                fig.update_traces(fill='toself', line_color=color_r)
                fig.update_layout(polar=dict(bgcolor="white"), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("🧠 Diagnóstico de la IA")
                vulnerables = df_adn[df_adn['Puntaje'] < 3.8]
                if not vulnerables.empty:
                    mas_critica = vulnerables.loc[vulnerables['Puntaje'].idxmin()]
                    st.error(f"⚠️ Punto de Quiebre: {mas_critica['Pieza']} ({mas_critica['Área']})")
                    
                    if st.button("🔥 Forjar Reparación"):
                        with st.spinner("Generando reto épico..."):
                            res = model.generate_content(f"Crea un reto tipo ICFES de {mas_critica['Área']} nivel avanzado.")
                            st.session_state['mision_ia'] = res.text
                            st.session_state['view'] = 'mision'
                            st.rerun()
                else:
                    st.success("✅ Armadura Integra. ¡Eres un Titán!")