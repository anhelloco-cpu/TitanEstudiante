import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import json
import re

# 1. --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="TITÁN ESTUDIANTE - Edición Completa", layout="wide", page_icon="🛡️")

# Inicializar estados de persistencia
if 'view' not in st.session_state: st.session_state['view'] = 'dashboard'
if 'df_adn' not in st.session_state: st.session_state['df_adn'] = None
if 'mision_data' not in st.session_state: st.session_state['mision_data'] = None
if 'progreso_mision' not in st.session_state:
    st.session_state.progreso_mision = {'idx': 0, 'correctas': 0, 'terminada': False}

# --- 2. ESTILOS VISUALES (Fondo Blanco y Estética Titán) ---
st.markdown("""
<style>
    .stApp { background-color: #ffffff; color: #2b2d33; }
    [data-testid="stSidebar"] { background-color: #f7f7f7; border-right: 1px solid #ddd; }
    
    /* Tarjetas de métricas */
    div[data-testid="stMetric"] {
        background-color: #ffffff; border: 1px solid #d1d5db;
        padding: 15px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    /* Estilo Pergamino */
    .pergamino {
        background-color: #fffcf5; color: #2b2d33; padding: 25px;
        border: 1px solid #d4af37; border-left: 8px solid #d4af37;
        border-radius: 10px; font-family: 'Georgia', serif; margin-bottom: 20px;
    }

    .alerta-daño { color: #ff4b4b; font-weight: bold; animation: pulse 1.5s infinite; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
</style>
""", unsafe_allow_html=True)

# --- 3. CONEXIÓN: LLAVE MAESTRA (Tu formato Unobtanium) ---
with st.sidebar:
    st.title("🦅 TITÁN ESTUDIANTE")
    with st.expander("🔑 LLAVE MAESTRA", expanded=True):
        key = st.text_input("API Key (Google Gemini):", type="password")
        if key:
            try:
                genai.configure(api_key=key)
                model_list = genai.list_models()
                models = [m.name for m in model_list if 'generateContent' in m.supported_generation_methods]
                target = next((m for m in models if 'gemini-1.5-flash' in m), models[0])
                st.session_state['model'] = genai.GenerativeModel(target)
                st.success("Oráculo Conectado")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# --- 4. MOTOR DE ADN (Análisis Inteligente) ---
def procesar_adn_ia(file):
    if 'model' not in st.session_state: return None
    try:
        df_raw = pd.read_excel(file)
        csv_sample = df_raw.head(20).to_csv(index=False)
        prompt = f"""Analiza estos datos académicos: {csv_sample}. Identifica: Matemáticas, Lectura Crítica, Ciencias Naturales, Sociales e Inglés. 
        Detecta la escala (0-500 o 0-5) y normaliza a 0.0-5.0. Devuelve SOLO un JSON: [ {{"Área": "Materia", "Puntaje": 4.2}}, ... ]"""
        response = st.session_state['model'].generate_content(prompt)
        json_clean = re.sub(r'```json\s*|\s*```', '', response.text).strip()
        adn_list = json.loads(json_clean)
        mapeo = {"Matemáticas": "Peto", "Lectura Crítica": "Yelmo", "Ciencias Naturales": "Grebas", "Sociales y Ciudadanas": "Escudo", "Inglés": "Guantelete"}
        for i in adn_list:
            i["Pieza"] = mapeo.get(i["Área"], "Accesorio")
            i["Estado"] = "Oro" if i["Puntaje"] >= 4.5 else "Plata" if i["Puntaje"] >= 3.8 else "Bronce"
            i["Salud"] = int((i["Puntaje"] / 5) * 100)
        return pd.DataFrame(adn_list)
    except: return None

# --- 5. LÓGICA DE MISIÓN (3 Desafíos) ---
def generar_mision_interactiva(area):
    prompt = f"""Genera un caso tipo ICFES de {area} y 3 preguntas con opciones A,B,C,D. Devuelve JSON: {{"caso": "...", "preguntas": [ {{"enunciado": "...", "opciones": {{"A":"..."}}, "correcta": "A"}}, ... ]}}"""
    try:
        res = st.session_state['model'].generate_content(prompt)
        return json.loads(re.sub(r'```json\s*|\s*```', '', res.text).strip())
    except: return None

# --- 6. INTERFAZ: MODO MISIÓN ---
if st.session_state['view'] == 'mision' and st.session_state['mision_data']:
    data = st.session_state['mision_data']
    prog = st.session_state.progreso_mision
    
    st.title(f"⚒️ Taller de Forja: Reparando el {st.session_state.area_reparar}")
    st.markdown(f'<div class="pergamino"><b>CONTEXTO DEL CASO:</b><br>{data["caso"]}</div>', unsafe_allow_html=True)
    
    if not prog['terminada']:
        q = data["preguntas"][prog['idx']]
        st.subheader(f"Desafío {prog['idx'] + 1} de 3")
        st.write(f"**{q['enunciado']}**")
        
        opcion = st.radio("Tu respuesta:", list(q["opciones"].values()), key=f"q_{prog['idx']}")
        
        if st.button("ENTREGAR"):
            letra = [k for k, v in q["opciones"].items() if v == opcion][0]
            if letra == q["correcta"]:
                st.success("✨ ¡Acierto!")
                st.session_state.progreso_mision['correctas'] += 1
            else:
                st.error(f"❌ Fallo. Era la {q['correcta']}")
            
            if prog['idx'] < 2:
                st.session_state.progreso_mision['idx'] += 1
                st.rerun()
            else:
                st.session_state.progreso_mision['terminada'] = True
                st.rerun()
    else:
        st.divider()
        if prog['correctas'] >= 2:
            st.balloons()
            st.success(f"🛡️ **¡PIEZA REPARADA!** Acertaste {prog['correctas']}/3. Tu armadura brilla de nuevo.")
            # Actualizar ADN
            idx_update = st.session_state.df_adn[st.session_state.df_adn['Área'] == st.session_state.area_reparar].index
            st.session_state.df_adn.loc[idx_update, 'Puntaje'] = 4.8
            st.session_state.df_adn.loc[idx_update, 'Estado'] = "Oro"
            st.session_state.df_adn.loc[idx_update, 'Salud'] = 96
        else:
            st.error("🏚️ **FORJA FALLIDA.** No lograste suficientes aciertos. La pieza sigue dañada.")
        
        if st.button("VOLVER AL DASHBOARD"):
            st.session_state.view = 'dashboard'
            st.session_state.mision_data = None
            st.session_state.progreso_mision = {'idx': 0, 'correctas': 0, 'terminada': False}
            st.rerun()

# --- 7. INTERFAZ: DASHBOARD COMPLETO (Lo que te gusta) ---
else:
    st.title("🛡️ TITÁN ESTUDIANTE: El Despertar")
    st.markdown("---")
    
    archivo = st.file_uploader("Cargue el ADN Académico (Excel)", type=["xlsx"])

    if archivo:
        if st.session_state['df_adn'] is None:
            st.session_state['df_adn'] = procesar_adn_ia(archivo)
        
        df = st.session_state['df_adn']
        if df is not None:
            promedio_total = df['Puntaje'].mean()
            color_r = "#d4af37" if promedio_total >= 4.5 else "#7f8c8d" if promedio_total >= 3.8 else "#a0522d"

            # Sidebar con Poder Total y Clan
            with st.sidebar:
                st.image("https://www.freepik.com/premium-psd/ornate-medieval-armor-knights-cuirass_412654456.htm", use_column_width=True)
                st.metric("PODER TOTAL", round(promedio_total, 2))
                st.divider()
                st.write("📍 **Clan:** Miguel - Grado 11-A")
                st.subheader("🏆 Gesta del Clan")
                st.write("Meta: Salida a Cine")
                st.progress(65)

            # Cuerpo del Dashboard
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("⚔️ Inventario de Armadura")
                for _, row in df.iterrows():
                    es_bronce = row['Estado'] == "Bronce"
                    c_txt = "#ff4b4b" if es_bronce else "#2b2d33"
                    label_status = "¡DAÑADA!" if es_bronce else row['Estado']
                    st.markdown(f"<span style='color:{c_txt}; font-weight:bold;'>{row['Pieza']}</span> ({row['Área']}): **{row['Puntaje']}** | {label_status}", unsafe_allow_html=True)
                    st.progress(row['Salud'] / 100)
                
                st.divider()
                fig = px.line_polar(df, r='Puntaje', theta='Área', line_close=True, range_r=[0,5])
                fig.update_traces(fill='toself', line_color=color_r)
                fig.update_layout(polar=dict(bgcolor="white"), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("🧠 Diagnóstico de la IA")
                vulnerables = df[df['Puntaje'] < 3.8]
                
                if not vulnerables.empty:
                    # Encontrar la pieza más débil
                    mas_debil = vulnerables.loc[vulnerables['Puntaje'].idxmin()]
                    
                    for _, row in vulnerables.iterrows():
                        if row['Área'] == mas_debil['Área']:
                            st.error(f"🚨 **CRÍTICO:** Tu {row['Pieza']} está a punto de romperse. (Prioridad)")
                        else:
                            st.warning(f"⚠️ **VULNERABLE:** Tu {row['Pieza']} necesita atención.")
                    
                    st.divider()
                    st.subheader("⚒️ Taller de Mentores")
                    st.write(f"Iniciando reparación de la pieza más débil: **{mas_debil['Área']}**")
                    
                    if st.button(f"🔥 Forjar Reparación: {mas_debil['Pieza'].upper()}"):
                        if 'model' in st.session_state:
                            with st.spinner("Generando 3 desafíos..."):
                                st.session_state.mision_data = generar_mision_interactiva(mas_debil['Área'])
                                st.session_state.area_reparar = mas_debil['Área']
                                st.session_state.view = 'mision'
                                st.rerun()
                        else:
                            st.warning("Conecte la Llave Maestra primero.")
                else:
                    st.success("✨ **INTEGRIDAD TOTAL:** Tu armadura es de leyenda.")