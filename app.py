import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import json
import re

# 1. --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="TITÁN ESTUDIANTE v106", layout="wide", page_icon="🛡️")

# Persistencia de estados
if 'view' not in st.session_state: st.session_state['view'] = 'dashboard'
if 'df_adn' not in st.session_state: st.session_state['df_adn'] = None
if 'mision_ia' not in st.session_state: st.session_state['mision_ia'] = ""

# --- 2. ESTILOS VISUALES (Fondo Blanco - Tu CSS preferido) ---
st.markdown("""
<style>
    .stApp { background-color: #ffffff; color: #2b2d33; }
    [data-testid="stSidebar"] { background-color: #f7f7f7; border-right: 1px solid #ddd; }
    
    /* Tarjetas de métricas blancas */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #d1d5db;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    /* Estilo Pergamino para Misiones */
    .pergamino {
        background-color: #fffcf5;
        color: #2b2d33;
        padding: 25px;
        border-radius: 10px;
        border: 1px solid #d4af37;
        border-left: 8px solid #d4af37;
        font-family: 'Georgia', serif;
        font-size: 1.1em;
        line-height: 1.6;
    }

    .alerta-daño { color: #ff4b4b; font-weight: bold; animation: pulse 1.5s infinite; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
</style>
""", unsafe_allow_html=True)

# --- 3. CONEXIÓN: LLAVE MAESTRA (Estilo Titán) ---
with st.sidebar:
    st.title("🦅 TITÁN ESTUDIANTE")
    with st.expander("🔑 LLAVE MAESTRA", expanded=True):
        key = st.text_input("API Key (Google Gemini):", type="password")
        if key:
            try:
                genai.configure(api_key=key)
                # Auto-detección de modelo para evitar el error 404
                model_list = genai.list_models()
                models = [m.name for m in model_list if 'generateContent' in m.supported_generation_methods]
                target = next((m for m in models if 'gemini-1.5-flash' in m), 
                              next((m for m in models if 'pro' in m), models[0]))
                st.session_state['model'] = genai.GenerativeModel(target)
                st.success(f"Oráculo Conectado: {target.split('/')[-1]}")
            except Exception as e:
                st.error(f"Error con la llave: {str(e)}")

# --- 4. MOTOR DE ADN (Análisis Inteligente de Miguel/Salvador) ---
def procesar_adn_ia(file):
    if 'model' not in st.session_state:
        st.error("Conecta la LLAVE MAESTRA para iniciar el análisis.")
        return None
    
    try:
        df_raw = pd.read_excel(file)
        # Tomamos una muestra para que la IA entienda el formato
        csv_sample = df_raw.head(20).to_csv(index=False)
        
        prompt = f"""
        Actúa como el Auditor de ADN Académico de Titán. Analiza estos datos de Miguel:
        DATOS: {csv_sample}
        
        TAREA:
        1. Identifica los puntajes de: Matemáticas, Lectura Crítica, Ciencias Naturales, Sociales y Ciudadanas, Inglés.
        2. Detecta la escala (0-500, 0-100 o 0-5) y normaliza todo a 0.0 - 5.0.
        3. Devuelve UNICAMENTE un JSON (sin explicaciones):
        [
          {{"Área": "Matemáticas", "Puntaje": 4.2}},
          ... (las 5 áreas)
        ]
        """
        response = st.session_state['model'].generate_content(prompt)
        # Limpieza de JSON
        json_clean = re.sub(r'```json\s*|\s*```', '', response.text).strip()
        adn_list = json.loads(json_clean)
        
        # Mapeo Medieval
        mapeo = {"Matemáticas": "Peto", "Lectura Crítica": "Yelmo", "Ciencias Naturales": "Grebas", "Sociales y Ciudadanas": "Escudo", "Inglés": "Guantelete"}
        for i in adn_list:
            i["Pieza"] = mapeo.get(i["Área"], "Accesorio")
            i["Estado"] = "Oro" if i["Puntaje"] >= 4.5 else "Plata" if i["Puntaje"] >= 3.8 else "Bronce"
            i["Salud"] = int((i["Puntaje"] / 5) * 100)
        return pd.DataFrame(adn_list)
    except Exception as e:
        st.error(f"Fallo al descifrar el ADN: {str(e)}")
        return None

# --- 5. NAVEGACIÓN ---
if st.session_state['view'] == 'mision':
    st.title("⚒️ Forja de Reparación")
    st.markdown(f'<div class="pergamino">{st.session_state["mision_ia"]}</div>', unsafe_allow_html=True)
    if st.button("⬅️ VOLVER AL DASHBOARD"):
        st.session_state['view'] = 'dashboard'
        st.rerun()

else:
    # --- DASHBOARD PRINCIPAL ---
    st.title("🛡️ TABLERO DE COMANDO - TITÁN ESTUDIANTE")
    archivo = st.file_uploader("Cargar ADN (Excel de Miguel/Salvador):", type=["xlsx"])

    if archivo:
        if st.session_state['df_adn'] is None:
            with st.spinner("IA Titán analizando patrones académicos..."):
                st.session_state['df_adn'] = procesar_adn_ia(archivo)
        
        df = st.session_state['df_adn']
        if df is not None:
            promedio = df['Puntaje'].mean()
            color_r = "#d4af37" if promedio >= 4.5 else "#7f8c8d" if promedio >= 3.8 else "#a0522d"

            # Sidebar Stats
            with st.sidebar:
                st.metric("PODER TOTAL", f"{promedio:.2f}")
                st.divider()
                st.info("Clan: Miguel - 11ºA")

            col1, col2 = st.columns([1, 1])
            with col1:
                st.subheader("⚔️ Estado de la Armadura")
                for _, row in df.iterrows():
                    color_t = "#ff4b4b" if row['Estado'] == "Bronce" else "#2b2d33"
                    status_text = "¡PIEZA DAÑADA!" if row['Estado'] == "Bronce" else f"Nivel {row['Estado']}"
                    st.markdown(f"<span style='color:{color_t}; font-weight:bold;'>{row['Pieza']}</span> ({row['Área']}): {row['Puntaje']} | {status_text}", unsafe_allow_html=True)
                    st.progress(row['Salud'] / 100)
                
                # Radar Chart
                fig = px.line_polar(df, r='Puntaje', theta='Área', line_close=True, range_r=[0,5])
                fig.update_traces(fill='toself', line_color=color_r)
                fig.update_layout(polar=dict(bgcolor="white"), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("🧠 Diagnóstico del Oráculo")
                vulnerables = df[df['Puntaje'] < 3.8]
                if not vulnerables.empty:
                    for _, row in vulnerables.iterrows():
                        st.error(f"⚠️ Punto Crítico en {row['Área']}")
                    
                    st.divider()
                    mas_debil = vulnerables.loc[vulnerables['Puntaje'].idxmin()]
                    if st.button(f"🔥 INICIAR MISIÓN: REPARAR {mas_debil['Pieza'].upper()}"):
                        with st.spinner("Generando desafío tipo ICFES..."):
                            prompt_mision = f"Crea un caso de análisis tipo ICFES para {mas_debil['Área']}. Incluye texto, pregunta y 4 opciones (A,B,C,D)."
                            res = st.session_state['model'].generate_content(prompt_mision)
                            st.session_state['mision_ia'] = res.text
                            st.session_state['view'] = 'mision'
                            st.rerun()
                else:
                    st.success("✅ Armadura Integra. ¡Eres un Titán de Oro!")