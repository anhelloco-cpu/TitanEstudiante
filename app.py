import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import json
import re

# 1. --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="TITÁN ESTUDIANTE v107", layout="wide", page_icon="🛡️")

# Inicializar estados globales
if 'view' not in st.session_state: st.session_state['view'] = 'dashboard'
if 'df_adn' not in st.session_state: st.session_state['df_adn'] = None
if 'mision_data' not in st.session_state: st.session_state['mision_data'] = None
if 'progreso_mision' not in st.session_state:
    st.session_state.progreso_mision = {'idx': 0, 'correctas': 0, 'intentado': False, 'terminada': False}

# --- 2. ESTILOS VISUALES (Fondo Blanco) ---
st.markdown("""
<style>
    .stApp { background-color: #ffffff; color: #2b2d33; }
    [data-testid="stSidebar"] { background-color: #f7f7f7; }
    div[data-testid="stMetric"] { background-color: #ffffff; border: 1px solid #d1d5db; border-radius: 12px; }
    .pergamino { background-color: #fffcf5; padding: 25px; border: 1px solid #d4af37; border-left: 8px solid #d4af37; border-radius: 10px; font-family: 'Georgia', serif; }
</style>
""", unsafe_allow_html=True)

# --- 3. CONEXIÓN: LLAVE MAESTRA ---
with st.sidebar:
    st.title("🦅 TITÁN ESTUDIANTE")
    with st.expander("🔑 LLAVE MAESTRA", expanded=True):
        key = st.text_input("API Key (Google Gemini):", type="password", key="api_key_input")
        if key:
            try:
                genai.configure(api_key=key)
                model_list = genai.list_models()
                models = [m.name for m in model_list if 'generateContent' in m.supported_generation_methods]
                target = next((m for m in models if 'gemini-1.5-flash' in m), models[0])
                st.session_state['model'] = genai.GenerativeModel(target)
                st.success(f"Oráculo Conectado")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# --- 4. MOTOR DE ADN (Inteligencia de Archivos) ---
def procesar_adn_ia(file):
    if 'model' not in st.session_state: return None
    try:
        df_raw = pd.read_excel(file)
        csv_sample = df_raw.head(20).to_csv(index=False)
        prompt = f"""Analiza estos datos de Miguel: {csv_sample}. Identifica: Matemáticas, Lectura Crítica, Ciencias Naturales, Sociales e Inglés. 
        Normaliza a escala 0.0-5.0. Devuelve SOLO un JSON: [ {{"Área": "Materia", "Puntaje": 4.2}}, ... ]"""
        response = st.session_state['model'].generate_content(prompt)
        json_clean = re.sub(r'```json\s*|\s*```', '', response.text).strip()
        adn_list = json.loads(json_clean)
        mapeo = {"Matemáticas": "Peto", "Lectura Crítica": "Yelmo", "Ciencias Naturales": "Grebas", "Sociales y Ciudadanas": "Escudo", "Inglés": "Guantelete"}
        for i in adn_list:
            i["Pieza"] = mapeo.get(i["Área"], "Accesorio")
            i["Estado"] = "Oro" if i["Puntaje"] >= 4.5 else "Plata" if i["Puntaje"] >= 3.8 else "Bronce"
            i["Salud"] = int((i["Puntaje"] / 5) * 100)
        return pd.DataFrame(adn_list)
    except Exception as e:
        st.error(f"Error ADN: {e}"); return None

# --- 5. GENERADOR DE MISIÓN (3 Preguntas) ---
def generar_mision_interactiva(area):
    prompt = f"""
    Genera un caso de estudio tipo ICFES para el área de {area}.
    Luego genera 3 preguntas diferentes basadas en ese caso.
    Devuelve un JSON con este formato exacto:
    {{
        "caso": "Texto del caso...",
        "preguntas": [
            {{"enunciado": "Q1", "opciones": {{"A": "op1", "B": "op2", "C": "op3", "D": "op4"}}, "correcta": "A"}},
            {{"enunciado": "Q2", "opciones": {{"A": "op1", "B": "op2", "C": "op3", "D": "op4"}}, "correcta": "B"}},
            {{"enunciado": "Q3", "opciones": {{"A": "op1", "B": "op2", "C": "op3", "D": "op4"}}, "correcta": "C"}}
        ]
    }}
    """
    try:
        res = st.session_state['model'].generate_content(prompt)
        return json.loads(re.sub(r'```json\s*|\s*```', '', res.text).strip())
    except:
        return None

# --- 6. INTERFAZ DE MISIÓN ---
if st.session_state['view'] == 'mision' and st.session_state['mision_data']:
    data = st.session_state['mision_data']
    prog = st.session_state.progreso_mision
    
    st.title(f"⚒️ Forjando: {st.session_state.area_reparar}")
    st.markdown(f'<div class="pergamino"><b>CONTEXTO:</b><br>{data["caso"]}</div>', unsafe_allow_html=True)
    
    if not prog['terminada']:
        q = data["preguntas"][prog['idx']]
        st.subheader(f"Desafío {prog['idx'] + 1} de 3")
        st.write(q["enunciado"])
        
        opcion = st.radio("Selecciona tu respuesta:", list(q["opciones"].values()), key=f"radio_{prog['idx']}")
        
        if st.button("ENTREGAR RESPUESTA"):
            letra_seleccionada = [k for k, v in q["opciones"].items() if v == opcion][0]
            if letra_seleccionada == q["correcta"]:
                st.success("✨ ¡CORRECTO! El Titán reconoce tu sabiduría.")
                st.session_state.progreso_mision['correctas'] += 1
            else:
                st.error(f"❌ INCORRECTO. La respuesta era la {q['correcta']}.")
            
            if prog['idx'] < 2:
                st.session_state.progreso_mision['idx'] += 1
                st.rerun()
            else:
                st.session_state.progreso_mision['terminada'] = True
                st.rerun()
    else:
        st.divider()
        st.balloons() if prog['correctas'] >= 2 else None
        st.subheader("🏁 Resultados de la Forja")
        st.write(f"Acertaste **{prog['correctas']}** de 3 desafíos.")
        
        if prog['correctas'] >= 2:
            st.success("🛡️ **¡PIEZA REPARADA!** Has demostrado maestría. Tu armadura ha subido de nivel.")
            # Actualizar el ADN en memoria
            area = st.session_state.area_reparar
            st.session_state.df_adn.loc[st.session_state.df_adn['Área'] == area, 'Puntaje'] = 4.5
            st.session_state.df_adn.loc[st.session_state.df_adn['Área'] == area, 'Estado'] = "Oro"
            st.session_state.df_adn.loc[st.session_state.df_adn['Área'] == area, 'Salud'] = 90
        else:
            st.error("🏚️ **FORJA FALLIDA.** No lograste los aciertos mínimos (2/3). Debes estudiar más.")
        
        if st.button("VOLVER AL DASHBOARD"):
            st.session_state.view = 'dashboard'
            st.session_state.mision_data = None
            st.session_state.progreso_mision = {'idx': 0, 'correctas': 0, 'intentado': False, 'terminada': False}
            st.rerun()

# --- 7. DASHBOARD ---
else:
    st.title("🛡️ DASHBOARD TITÁN")
    archivo = st.file_uploader("Cargar ADN (Miguel/Salvador)", type=["xlsx"])

    if archivo:
        if st.session_state['df_adn'] is None:
            st.session_state['df_adn'] = procesar_adn_ia(archivo)
        
        df = st.session_state['df_adn']
        if df is not None:
            col1, col2 = st.columns([1, 1])
            with col1:
                st.subheader("⚔️ Inventario")
                for _, row in df.iterrows():
                    color = "#ff4b4b" if row['Puntaje'] < 3.8 else "#2b2d33"
                    st.markdown(f"<span style='color:{color}; font-weight:bold;'>{row['Pieza']}</span>: {row['Puntaje']}", unsafe_allow_html=True)
                    st.progress(row['Salud'] / 100)
            
            with col2:
                st.subheader("🧠 Diagnóstico")
                vulnerables = df[df['Puntaje'] < 3.8]
                if not vulnerables.empty:
                    debil = vulnerables.loc[vulnerables['Puntaje'].idxmin()]
                    st.warning(f"Pieza más débil: {debil['Área']}")
                    if st.button(f"🔥 Iniciar Forja: {debil['Área']}"):
                        with st.spinner("IA preparando 3 desafíos..."):
                            st.session_state.mision_data = generar_mision_interactiva(debil['Área'])
                            st.session_state.area_reparar = debil['Área']
                            st.session_state.view = 'mision'
                            st.rerun()
                else:
                    st.success("Armadura de Leyenda Completa.")