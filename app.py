import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import json
import re

# 1. --- CONFIGURACIÓN DE LA PÁGINA (ESTRUCTURA INTEGRAL) ---
st.set_page_config(page_title="TITÁN ESTUDIANTE v116", layout="wide", page_icon="🛡️")

# Inicializar estados de persistencia para navegación y datos
if 'view' not in st.session_state: st.session_state['view'] = 'dashboard'
if 'df_adn' not in st.session_state: st.session_state['df_adn'] = None
if 'df_historico' not in st.session_state: st.session_state['df_historico'] = None
if 'resumen_ia' not in st.session_state: st.session_state['resumen_ia'] = ""
if 'diagnostico_detallado' not in st.session_state: st.session_state['diagnostico_detallado'] = ""
if 'mision_data' not in st.session_state: st.session_state['mision_data'] = None
if 'area_reparar' not in st.session_state: st.session_state.area_reparar = ""
if 'simulacion_estado' not in st.session_state: st.session_state.simulacion_estado = "inicio"
if 'reaccion_npc' not in st.session_state: st.session_state.reaccion_npc = ""

# --- 2. ESTILOS VISUALES (FONDO BLANCO Y GAMIFICACIÓN) ---
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

    .resumen-caja {
        background-color: #f8fafc; border-radius: 12px; padding: 20px;
        border: 1px solid #e2e8f0; border-left: 6px solid #d4af37;
        margin-bottom: 15px; font-size: 1.1em; line-height: 1.6;
        color: #1e293b; font-weight: 500;
    }

    .npc-briefing {
        background-color: #f1f5f9; padding: 25px; border-radius: 15px;
        border: 1px solid #cbd5e1; margin-bottom: 20px;
        color: #334155; font-size: 1.1em;
    }

    .evidencia-card {
        background-color: #ffffff; border: 1px solid #e2e8f0;
        padding: 15px; border-radius: 10px; margin-bottom: 10px;
    }

    .diagnostico-full { font-size: 1em; line-height: 1.8; color: #334155; white-space: pre-wrap; }

    .alerta-daño { color: #ff4b4b; font-weight: bold; animation: pulse 1.5s infinite; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    
    .stButton>button { border-radius: 8px; font-weight: bold; transition: all 0.3s; }
</style>
""", unsafe_allow_html=True)

# --- 3. FUNCIONES DE IA (CEREBRO DINÁMICO) ---

def procesar_adn_ia(file):
    if 'model' not in st.session_state: return None
    try:
        df_raw = pd.read_excel(file)
        csv_full_sample = df_raw.head(50).to_csv(index=False)
        
        prompt = f"""Analiza estos registros académicos con periodos AP1 a AP4: {csv_full_sample}
        MAPEO DE PIEZAS: Yelmo(Lectura), Peto(Mat), Grebas(Nat), Escudo(Soc), Guantelete(Ing).
        
        TAREA:
        1. Calcula promedios actuales (0.0-5.0).
        2. Genera un "resumen_epico" (conclusión general de la armadura).
        3. Realiza un "diagnostico_maestro": un párrafo por pieza con iconos y tendencias.
        4. Genera datos históricos por área y periodo.
        
        Devuelve UNICAMENTE un JSON: 
        {{'tabla': [...], 'resumen_epico': '...', 'diagnostico_master': '...', 'historico': [...]}}"""
        
        response = st.session_state['model'].generate_content(prompt)
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        data = json.loads(match.group())
        
        st.session_state['resumen_ia'] = data['resumen_epico']
        st.session_state['diagnostico_detallado'] = data['diagnostico_master']
        st.session_state['df_historico'] = pd.DataFrame(data['historico'])
        
        adn_list = data['tabla']
        mapeo_piezas = {"Matemáticas": "Peto", "Lectura Crítica": "Yelmo", "Ciencias Naturales": "Grebas", "Sociales y Ciudadanas": "Escudo", "Inglés": "Guantelete"}
        for i in adn_list:
            i["Pieza"] = mapeo_piezas.get(i["Área"], "Accesorio")
            i["Estado"] = "Oro" if i["Puntaje"] >= 4.5 else "Plata" if i["Puntaje"] >= 3.8 else "Bronce"
            i["Salud"] = int((i["Puntaje"] / 5) * 100)
        return pd.DataFrame(adn_list)
    except Exception as e:
        st.error(f"Error en el Oráculo: {e}")
        return None

def generar_mesa_crisis_ia(area):
    prompt = f"""Actúa como Director de Juego. Crea una 'Mesa de Crisis' para {area} basada en competencias Saber 11.
    Diseña un escenario donde un personaje toma una decisión basada en un error de interpretación o fuente.
    El estudiante debe elegir la evidencia técnica del maletín para corregirlo.
    
    Devuelve un JSON puro:
    {{
      "npc": "Cargo del personaje (ej: El Alcalde, El Científico Jefe)",
      "escenario": "Contexto de la crisis...",
      "dialogo_npc": "Argumento que contiene el error...",
      "opciones": [
        {{"fuente": "Nombre de la evidencia", "detalle": "Qué dice...", "es_correcta": true/false, "feedback": "Consecuencia..."}},
        ... (4 opciones)
      ]
    }}"""
    try:
        res = st.session_state['model'].generate_content(prompt)
        match = re.search(r'\{.*\}', res.text, re.DOTALL)
        return json.loads(match.group())
    except: return None

# --- 4. BARRA LATERAL (ENTRADA DE LLAVE INTACTA) ---
with st.sidebar:
    st.title("🦅 TITÁN ESTUDIANTE")
    with st.expander("🔑 LLAVE MAESTRA", expanded=True):
        key = st.text_input("API Key de Gemini:", type="password", key="api_key_sidebar")
        if key:
            try:
                genai.configure(api_key=key)
                model_list = genai.list_models()
                target = next((m for m in models if '1.5-flash' in m), models[0])
                st.session_state['model'] = genai.GenerativeModel(target)
                st.success("Oráculo Conectado")
            except Exception as e: st.error(f"Error: {e}")

    if st.session_state['df_adn'] is not None:
        st.divider()
        promedio_gral = st.session_state['df_adn']['Puntaje'].mean()
        st.metric("PODER TOTAL", round(promedio_gral, 2))
        st.write("📍 **Clan:** Miguel - Grado 11-A")
        st.markdown("### 🏆 Gesta del Clan")
        st.progress(65)

# --- 5. LÓGICA DE NAVEGACIÓN ---

# A. MODO MESA DE CRISIS (Sustituye a las preguntas)
if st.session_state['view'] == 'mision' and st.session_state['mision_data']:
    data = st.session_state['mision_data']
    st.title(f"💼 Mesa de Crisis: Forjando el {st.session_state.area_reparar}")
    
    st.markdown(f"**SITUACIÓN DE EMERGENCIA:** {data['escenario']}")
    st.markdown(f"<div class='npc-briefing'><b>{data['npc']} dice:</b><br>'{data['dialogo_npc']}'</div>", unsafe_allow_html=True)
    
    if st.session_state.simulacion_estado == "inicio":
        st.subheader("📁 Tu Maletín de Evidencia")
        for i, opt in enumerate(data['opciones']):
            if st.button(f"📄 {opt['fuente']}: {opt['detalle']}", key=f"crisis_{i}", use_container_width=True):
                st.session_state.reaccion_npc = opt['feedback']
                st.session_state.simulacion_estado = "final" if opt['es_correcta'] else "fallo"
                st.rerun()
    else:
        st.divider()
        st.markdown(f"<div class='pergamino'><b>INFORME DE RESULTADOS:</b><br>{st.session_state.reaccion_npc}</div>", unsafe_allow_html=True)
        if st.session_state.simulacion_estado == "final":
            st.balloons(); st.success("🛡️ ¡CRISIS EVITADA! La pieza ha sido reforzada.")
            df = st.session_state.df_adn
            idx = df[df['Área'] == st.session_state.area_reparar].index
            df.loc[idx, ['Puntaje', 'Estado', 'Salud']] = [4.8, "Oro", 96]
        else:
            st.error("🏚️ LA CIUDAD SUFRE LAS CONSECUENCIAS. La evidencia no fue sólida.")
            
        if st.button("VOLVER AL SANTUARIO"):
            st.session_state.view = 'dashboard'; st.session_state.mision_data = None
            st.session_state.simulacion_estado = "inicio"; st.rerun()

# B. MODO DASHBOARD (TODO LO QUE TE GUSTA)
else:
    st.title("🛡️ TITÁN ESTUDIANTE: El Despertar")
    archivo = st.file_uploader("Cargue el ADN Académico (Excel)", type=["xlsx"])

    if archivo:
        if st.session_state['df_adn'] is None:
            with st.spinner("Decodificando ADN y Estado de Armadura..."):
                st.session_state['df_adn'] = procesar_adn_ia(archivo)
        
        df = st.session_state['df_adn']
        if df is not None:
            col1, col2 = st.columns([1, 1.2]) 
            
            with col1:
                st.subheader("⚔️ Inventario de Armadura")
                for _, row in df.iterrows():
                    c_txt = "#ff4b4b" if row['Estado'] == "Bronce" else "#2b2d33"
                    st.markdown(f"<span style='color:{c_txt}; font-weight:bold;'>{row['Pieza']}</span> ({row['Área']}): {row['Puntaje']} | {row['Estado']}", unsafe_allow_html=True)
                    st.progress(row['Salud'] / 100)
                st.divider()
                fig = px.line_polar(df, r='Puntaje', theta='Área', line_close=True, range_r=[0,5])
                fig.update_traces(fill='toself', line_color="#d4af37")
                fig.update_layout(polar=dict(bgcolor="white"), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("🧠 El Oráculo de la Armadura")
                if st.session_state['resumen_ia']:
                    st.markdown(f"<div class='resumen-caja'>✨ {st.session_state['resumen_ia']}</div>", unsafe_allow_html=True)

                if st.session_state['diagnostico_detallado']:
                    with st.expander("🔍 VER ESTADO TÉCNICO DE LAS PIEZAS", expanded=False):
                        st.markdown(f"<div class='diagnostico-full'>{st.session_state['diagnostico_detallado']}</div>", unsafe_allow_html=True)
                        if st.session_state['df_historico'] is not None:
                            st.divider(); st.markdown("#### 📈 Evolución Histórica")
                            fig_trend = px.line(st.session_state['df_historico'], x="Periodo", y="Puntaje", color="Área", markers=True)
                            fig_trend.update_layout(plot_bgcolor="white", paper_bgcolor="rgba(0,0,0,0)", height=300)
                            st.plotly_chart(fig_trend, use_container_width=True)

                st.divider()
                vulnerables = df[df['Puntaje'] < 3.8]
                if not vulnerables.empty:
                    mas_debil = vulnerables.loc[vulnerables['Puntaje'].idxmin()]
                    st.error(f"🚨 **PRIORIDAD:** El {mas_debil['Pieza']} requiere forja inmediata.")
                    if st.button(f"🔥 Entrar a Mesa de Crisis: {mas_debil['Pieza'].upper()}"):
                        if 'model' in st.session_state:
                            with st.spinner("IA preparando simulador de crisis..."):
                                st.session_state.mision_data = generar_mesa_crisis_ia(mas_debil['Área'])
                                st.session_state.area_reparar = mas_debil['Área']
                                st.session_state.view = 'mision'; st.rerun()
                        else: st.warning("Conecte la Llave Maestra.")
                else:
                    st.success("✨ **INTEGRIDAD TOTAL.**")