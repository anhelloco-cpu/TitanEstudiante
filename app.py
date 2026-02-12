import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import json
import re

# 1. --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="TITÁN ESTUDIANTE v112", layout="wide", page_icon="🛡️")

# Inicializar estados de persistencia
if 'view' not in st.session_state: st.session_state['view'] = 'dashboard'
if 'df_adn' not in st.session_state: st.session_state['df_adn'] = None
if 'diagnostico_ia' not in st.session_state: st.session_state['diagnostico_ia'] = ""
if 'mision_data' not in st.session_state: st.session_state['mision_data'] = None
if 'progreso_mision' not in st.session_state:
    st.session_state.progreso_mision = {'idx': 0, 'correctas': 0, 'terminada': False}
if 'area_reparar' not in st.session_state: st.session_state.area_reparar = ""

# --- 2. ESTILOS VISUALES (Blanco y Profesional) ---
st.markdown("""
<style>
    .stApp { background-color: #ffffff; color: #2b2d33; }
    [data-testid="stSidebar"] { background-color: #f8f9fa; border-right: 1px solid #eee; }
    
    div[data-testid="stMetric"] {
        background-color: #ffffff; border: 1px solid #d1d5db;
        padding: 15px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    .pergamino {
        background-color: #fffcf5; color: #2b2d33; padding: 25px;
        border: 1px solid #d4af37; border-left: 8px solid #d4af37;
        border-radius: 10px; font-family: 'Georgia', serif; margin-bottom: 25px;
        font-size: 1.1em; line-height: 1.6;
    }

    /* Caja especial para el Diagnóstico Maestro */
    .diagnostico-master {
        background-color: #f0f4f8; border-radius: 12px; padding: 25px;
        border-left: 6px solid #1e293b; margin-bottom: 20px;
        font-size: 1em; line-height: 1.5; color: #1e293b;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.05);
    }

    .alerta-daño { color: #ff4b4b; font-weight: bold; animation: pulse 1.5s infinite; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
</style>
""", unsafe_allow_html=True)

# --- 3. FUNCIONES DE IA (Análisis de Periodos y Misión) ---
def procesar_adn_ia_maestro(file):
    if 'model' not in st.session_state: return None
    try:
        df_raw = pd.read_excel(file)
        csv_sample = df_raw.to_csv(index=False)
        
        prompt = f"""Analiza estos registros académicos con múltiples periodos (AP1, AP2, AP3, etc.):
        {csv_sample}
        
        TAREA:
        1. Extrae el puntaje actual por área (normaliza a 0-5).
        2. Analiza la TENDENCIA histórica (¿mejoró o bajó entre periodos?).
        3. Genera un DIAGNÓSTICO MAESTRO: Un análisis narrativo de 2-3 párrafos que explique la evolución del estudiante, detecte riesgos y mencione la materia más crítica según el último periodo.
        
        Devuelve SOLO un JSON:
        {{
            "tabla": [ {{"Área": "Materia", "Puntaje": 4.2}}, ... ],
            "diagnostico": "Texto del diagnóstico de tendencia..."
        }}
        """
        response = st.session_state['model'].generate_content(prompt)
        data = json.loads(re.sub(r'```json\s*|\s*```', '', response.text).strip())
        
        st.session_state['diagnostico_ia'] = data['diagnostico']
        
        adn_list = data['tabla']
        mapeo = {"Matemáticas": "Peto", "Lectura Crítica": "Yelmo", "Ciencias Naturales": "Grebas", "Sociales y Ciudadanas": "Escudo", "Inglés": "Guantelete"}
        for i in adn_list:
            i["Pieza"] = mapeo.get(i["Área"], "Accesorio")
            i["Estado"] = "Oro" if i["Puntaje"] >= 4.5 else "Plata" if i["Puntaje"] >= 3.8 else "Bronce"
            i["Salud"] = int((i["Puntaje"] / 5) * 100)
        return pd.DataFrame(adn_list)
    except: return None

def generar_mision_ia(area):
    prompt = f"""Genera un caso ICFES de {area} y 3 preguntas A,B,C,D. 
    Devuelve JSON: {{ "caso": "...", "preguntas": [ {{"enunciado": "...", "opciones": {{"A":"..."}}, "correcta": "letra"}}, ... ] }}"""
    try:
        res = st.session_state['model'].generate_content(prompt)
        return json.loads(re.sub(r'```json\s*|\s*```', '', res.text).strip())
    except: return None

# --- 4. BARRA LATERAL (Persistencia Total) ---
with st.sidebar:
    st.title("🦅 TITÁN ESTUDIANTE")
    with st.expander("🔑 LLAVE MAESTRA", expanded=True):
        key = st.text_input("API Key de Gemini:", type="password", key="api_key")
        if key:
            try:
                genai.configure(api_key=key)
                model_list = genai.list_models()
                target = next((m.name for m in model_list if '1.5-flash' in m.name), "models/gemini-pro")
                st.session_state['model'] = genai.GenerativeModel(target)
                st.success("Oráculo Despierto")
            except: st.error("Llave no válida")

    if st.session_state['df_adn'] is not None:
        st.divider()
        poder = st.session_state['df_adn']['Puntaje'].mean()
        st.metric("PODER TOTAL", round(poder, 2))
        st.write("📍 **Clan:** Miguel - Grado 11-A")
        st.subheader("🏆 Gesta del Clan")
        st.progress(65)
        st.caption("Meta: Salida a Cine (65%)")

# --- 5. LÓGICA DE NAVEGACIÓN ---

# A. MODO MISIÓN (La Forja Interactiva)
if st.session_state['view'] == 'mision' and st.session_state['mision_data']:
    data = st.session_state['mision_data']
    prog = st.session_state.progreso_mision
    
    st.title(f"⚒️ Forja de Reparación: {st.session_state.area_reparar}")
    st.markdown(f'<div class="pergamino"><b>CONTEXTO DEL CASO:</b><br>{data["caso"]}</div>', unsafe_allow_html=True)
    
    if not prog['terminada']:
        q = data["preguntas"][prog['idx']]
        st.subheader(f"Desafío {prog['idx'] + 1} de 3")
        st.write(f"**{q['enunciado']}**")
        
        ans = st.radio("Selecciona tu respuesta:", list(q["opciones"].values()), key=f"q_radio_{prog['idx']}")
        
        if st.button("ENTREGAR"):
            letra = [k for k, v in q["opciones"].items() if v == ans][0]
            if letra == q["correcta"]:
                st.success("✨ ¡Acierto!")
                st.session_state.progreso_mision['correctas'] += 1
            else:
                st.error(f"❌ Fallo. La respuesta era la {q['correcta']}.")
            
            if prog['idx'] < 2:
                st.session_state.progreso_mision['idx'] += 1
            else:
                st.session_state.progreso_mision['terminada'] = True
            st.rerun()
    else:
        if prog['correctas'] >= 2:
            st.balloons()
            st.success(f"🛡️ PIEZA REPARADA ({prog['correctas']}/3).")
            df = st.session_state.df_adn
            idx = df[df['Área'] == st.session_state.area_reparar].index
            df.loc[idx, ['Puntaje', 'Estado', 'Salud']] = [4.7, "Oro", 94]
        else:
            st.error("🏚️ FORJA FALLIDA. Necesitas más entrenamiento.")
        
        if st.button("VOLVER AL DASHBOARD"):
            st.session_state.view = 'dashboard'
            st.session_state.mision_data = None
            st.session_state.progreso_mision = {'idx': 0, 'correctas': 0, 'terminada': False}
            st.rerun()

# B. MODO DASHBOARD (Análisis Completo)
else:
    st.title("🛡️ TITÁN ESTUDIANTE: El Despertar")
    archivo = st.file_uploader("Cargue el ADN Académico (Excel)", type=["xlsx"])

    if archivo:
        if st.session_state['df_adn'] is None:
            with st.spinner("Analizando ADN y Tendencias históricas..."):
                st.session_state['df_adn'] = procesar_adn_ia_maestro(archivo)
        
        df = st.session_state['df_adn']
        if df is not None:
            col1, col2 = st.columns([1, 1.2])
            
            with col1:
                st.subheader("⚔️ Inventario de Armadura")
                for _, row in df.iterrows():
                    c_txt = "#ff4b4b" if row['Estado'] == "Bronce" else "#2b2d33"
                    label = "¡DAÑADA!" if row['Estado'] == "Bronce" else row['Estado']
                    st.markdown(f"<span style='color:{c_txt}; font-weight:bold;'>{row['Pieza']}</span> ({row['Área']}): {row['Puntaje']} | {label}", unsafe_allow_html=True)
                    st.progress(row['Salud'] / 100)
                
                st.divider()
                fig = px.line_polar(df, r='Puntaje', theta='Área', line_close=True, range_r=[0,5])
                fig.update_traces(fill='toself', line_color="#d4af37")
                fig.update_layout(polar=dict(bgcolor="white"), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("🧠 El Oráculo de Tendencias")
                # Mostrar el diagnóstico de periodos en una caja elegante
                if st.session_state['diagnostico_ia']:
                    st.markdown(f'<div class="diagnostico-master">{st.session_state["diagnostico_ia"]}</div>', unsafe_allow_html=True)
                
                vulnerables = df[df['Puntaje'] < 3.8]
                if not vulnerables.empty:
                    mas_debil = vulnerables.loc[vulnerables['Puntaje'].idxmin()]
                    for _, row in vulnerables.iterrows():
                        if row['Área'] == mas_debil['Área']:
                            st.error(f"🚨 **PRIORIDAD:** El {row['Pieza']} ({row['Área']}) requiere forja inmediata.")
                        else:
                            st.warning(f"⚠️ **DEBILIDAD:** {row['Pieza']} ({row['Área']}) con fisuras.")
                    
                    st.divider()
                    st.subheader("⚒️ Taller de Mentores")
                    if st.button(f"🔥 Forjar Reparación: {mas_debil['Pieza'].upper()}"):
                        if 'model' in st.session_state:
                            with st.spinner("Generando 3 retos..."):
                                st.session_state.mision_data = generar_mision_ia(mas_debil['Área'])
                                st.session_state.area_reparar = mas_debil['Área']
                                st.session_state.view = 'mision'
                                st.rerun()
                        else: st.warning("Conecte la Llave Maestra primero.")
                else:
                    st.success("✨ **INTEGRIDAD TOTAL:** Eres un Titán invencible.")