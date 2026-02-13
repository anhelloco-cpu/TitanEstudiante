import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import json
import re

# 1. --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="TITÁN ESTUDIANTE v117", layout="wide", page_icon="🛡️")

# Inicializar estados de persistencia
if 'view' not in st.session_state: st.session_state['view'] = 'dashboard'
if 'df_adn' not in st.session_state: st.session_state['df_adn'] = None
if 'df_historico' not in st.session_state: st.session_state['df_historico'] = None
if 'resumen_ia' not in st.session_state: st.session_state['resumen_ia'] = ""
if 'diagnostico_detallado' not in st.session_state: st.session_state['diagnostico_detallado'] = ""
if 'mision_data' not in st.session_state: st.session_state['mision_data'] = None
if 'progreso_mision' not in st.session_state:
    st.session_state.progreso_mision = {'idx': 0, 'correctas': 0, 'terminada': False}
if 'area_reparar' not in st.session_state: st.session_state.area_reparar = ""
if 'simulacion_completada' not in st.session_state: st.session_state.simulacion_completada = False
if 'reaccion_npc' not in st.session_state: st.session_state.reaccion_npc = ""

# --- 2. ESTILOS VISUALES (Diseño Futurista Neo-Titán) ---
st.markdown("""
<style>
    /* Fondo con textura tecnológica sutil */
    .stApp { 
        background: radial-gradient(circle at top right, #ffffff, #f1f5f9); 
        color: #1e293b; 
    }
    
    /* Barra lateral estilo Centro de Mando */
    [data-testid="stSidebar"] { 
        background-color: #0f172a !important; 
        border-right: 2px solid #334155;
    }
    [data-testid="stSidebar"] * { color: #f1f5f9 !important; }

    /* Glassmorphism en Métricas con borde de luz */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(226, 232, 240, 0.8);
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    div[data-testid="stMetric"]:hover { 
        transform: translateY(-5px); 
        border-color: #d4af37;
        box-shadow: 0 15px 30px -5px rgba(212, 175, 55, 0.2);
    }

    /* Caja de Resumen "Dark Tech" */
    .resumen-caja {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 20px;
        padding: 25px;
        border-left: 10px solid #d4af37;
        color: #f8fafc;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2);
        margin-bottom: 20px;
    }

    /* Pergaminos y diálogos estilo HUD */
    .pergamino, .npc-dialogo {
        background: #ffffff;
        padding: 30px;
        border-radius: 24px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        position: relative;
    }
    .npc-dialogo::before {
        content: "PROTOCOL: ACTIVE";
        position: absolute;
        top: 10px;
        right: 20px;
        font-size: 0.7em;
        color: #3b82f6;
        font-weight: bold;
    }

    /* Botones con pulso de energía */
    .stButton>button {
        background: #1e293b !important;
        color: #ffffff !important;
        border-radius: 14px !important;
        border: 1px solid #334155 !important;
        padding: 12px 28px !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    }
    .stButton>button:hover {
        background: #d4af37 !important;
        color: #0f172a !important;
        box-shadow: 0 0 20px rgba(212, 175, 55, 0.5) !important;
        border-color: #f59e0b !important;
    }

    /* Barras de progreso futuristas */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #d4af37 0%, #f59e0b 100%) !important;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. FUNCIONES DE IA (Lógica Original Protegida) ---
def procesar_adn_ia(file):
    if 'model' not in st.session_state: return None
    try:
        df_raw = pd.read_excel(file)
        csv_full_sample = df_raw.head(50).to_csv(index=False)
        
        prompt = f"""Analiza estos registros académicos con periodos AP1, AP2, AP3, AP4:
        {csv_full_sample}
        
        MAPEO DE ARMADURA:
        - Yelmo: Lectura Crítica
        - Peto: Matemáticas
        - Grebas: Ciencias Naturales
        - Escudo: Sociales y Ciudadanas
        - Guantelete: Inglés

        TAREA:
        1. Calcula promedios actuales (0.0-5.0).
        2. Genera un "resumen_epico": Una sola frase potente sobre el estado general de la armadura.
        3. Realiza un "diagnostico_maestro": 
           - UN PÁRRAFO POR PIEZA DE ARMADURA.
           - Menciona la materia y la tendencia histórica (AP1 vs Último AP).
           - Usa iconos: 🛡️ (Estable), 📈 (Mejorando), 📉 (Dañada).
        4. Genera datos para gráfica de tendencia.

        Devuelve UNICAMENTE un JSON:
        {{
            "tabla": [ {{"Área": "Materia", "Puntaje": 4.2}}, ... ],
            "resumen_epico": "Tu armadura brilla...",
            "diagnostico_master": "🛡️ YELMO (Lectura Crítica): ...\\n\\n🛡️ PETO (Matemáticas): ...",
            "historico": [ {{"Periodo": "AP1", "Área": "Materia", "Puntaje": 4.0}}, ... ]
        }}
        """
        response = st.session_state['model'].generate_content(prompt)
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        data_packet = json.loads(match.group())
        
        st.session_state['resumen_ia'] = data_packet['resumen_epico']
        st.session_state['diagnostico_detallado'] = data_packet['diagnostico_master']
        st.session_state['df_historico'] = pd.DataFrame(data_packet['historico'])
        
        adn_list = data_packet['tabla']
        mapeo_piezas = {"Matemáticas": "Peto", "Lectura Crítica": "Yelmo", "Ciencias Naturales": "Grebas", "Sociales y Ciudadanas": "Escudo", "Inglés": "Guantelete"}
        for i in adn_list:
            i["Pieza"] = mapeo_piezas.get(i["Área"], "Accesorio")
            i["Estado"] = "Oro" if i["Puntaje"] >= 4.5 else "Plata" if i["Puntaje"] >= 3.8 else "Bronce"
            i["Salud"] = int((i["Puntaje"] / 5) * 100)
        return pd.DataFrame(adn_list)
    except Exception as e:
        st.error(f"Error en el Oráculo: {e}")
        return None

def generar_mision_ia(area):
    prompt = f"""Actúa como Director de una Simulación de Crisis tipo ICFES para el área de {area}. 
    Crea un escenario donde un Personaje (NPC) plantea un dilema con un error de lógica o fuente.
    El estudiante debe elegir la Fuente o Evidencia correcta de un 'Maletín' para resolver la crisis.
    
    Devuelve un JSON puro:
    {{
      "npc": "Nombre/Cargo del Personaje",
      "contexto": "Descripción de la crisis en la ciudad...",
      "dialogo": "Lo que dice el NPC planteando el problema...",
      "maletin": [
        {{"fuente": "Nombre de la Evidencia", "detalle": "Datos técnicos...", "es_correcta": true, "reaccion": "Consecuencia si elige esta..."}},
        {{"fuente": "Fuente poco fiable", "detalle": "Datos de opinión...", "es_correcta": false, "reaccion": "Consecuencia si falla..."}},
        ... (total 4 opciones)
      ]
    }}"""
    try:
        res = st.session_state['model'].generate_content(prompt)
        match = re.search(r'\{.*\}', res.text, re.DOTALL)
        return json.loads(match.group())
    except: return None

# --- 4. BARRA LATERAL (LLAVE MAESTRA INTACTA) ---
with st.sidebar:
    st.title("🦅 TITÁN ESTUDIANTE")
    with st.expander("🔑 LLAVE MAESTRA", expanded=True):
        key = st.text_input("API Key de Gemini:", type="password", key="api_key_sidebar")
        if key:
            try:
                genai.configure(api_key=key)
                model_list = genai.list_models()
                models = [m.name for m in model_list if 'generateContent' in m.supported_generation_methods]
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
        st.write("Meta: Salida a Cine")
        st.progress(65)
        st.caption("Fuerza colectiva: 65%")

# --- 5. LÓGICA DE NAVEGACIÓN ---

if st.session_state['view'] == 'mision' and st.session_state['mision_data']:
    data = st.session_state['mision_data']
    
    st.title(f"💼 Mesa de Crisis: Forjando el {st.session_state.area_reparar}")
    st.markdown(f"**SITUACIÓN:** {data['contexto']}")
    st.markdown(f"<div class='npc-dialogo'><b>{data['npc']} dice:</b><br>'{data['dialogo']}'</div>", unsafe_allow_html=True)
    
    if not st.session_state.simulacion_completada:
        st.subheader("📁 Tu Maletín de Evidencia")
        
        for i, item in enumerate(data['maletin']):
            if st.button(f"📄 {item['fuente']}: {item['detalle']}", key=f"btn_evidencia_{i}", use_container_width=True):
                st.session_state.reaccion_npc = item['reaccion']
                st.session_state.simulacion_completada = "exito" if item['es_correcta'] else "fallo"
                st.rerun()
    else:
        st.divider()
        st.markdown(f"<div class='pergamino'><b>RESULTADO DE TU DECISIÓN:</b><br>{st.session_state.reaccion_npc}</div>", unsafe_allow_html=True)
        
        if st.session_state.simulacion_completada == "exito":
            st.balloons()
            st.success("🛡️ **¡CRISIS EVITADA!** La pieza ha sido reparada.")
            df = st.session_state.df_adn
            idx = df[df['Área'] == st.session_state.area_reparar].index
            df.loc[idx, ['Puntaje', 'Estado', 'Salud']] = [4.8, "Oro", 96]
        else:
            st.error("🏚️ **FRACASO EN LA MISIÓN.**")
            
        if st.button("VOLVER AL DASHBOARD"):
            st.session_state.view = 'dashboard'
            st.session_state.mision_data = None
            st.session_state.simulacion_completada = False
            st.session_state.reaccion_npc = ""
            st.rerun()

else:
    st.title("🛡️ TITÁN ESTUDIANTE: El Despertar")
    archivo = st.file_uploader("Cargue el ADN Académico (Excel)", type=["xlsx"])

    if archivo:
        if st.session_state['df_adn'] is None:
            with st.spinner("Analizando ADN y Estado de Armadura..."):
                st.session_state['df_adn'] = procesar_adn_ia(archivo)
        
        df = st.session_state['df_adn']
        if df is not None:
            col1, col2 = st.columns([1, 1.2]) 
            
            with col1:
                st.subheader("⚔️ Inventario de Armadura")
                for _, row in df.iterrows():
                    es_bronce = row['Estado'] == "Bronce"
                    c_txt = "#ff4b4b" if es_bronce else "#1e293b"
                    label = "¡DAÑADA!" if es_bronce else row['Estado']
                    st.markdown(f"<span style='color:{c_txt}; font-weight:bold;'>{row['Pieza']}</span> ({row['Área']}): {row['Puntaje']} | {label}", unsafe_allow_html=True)
                    st.progress(row['Salud'] / 100)
                
                st.divider()
                fig = px.line_polar(df, r='Puntaje', theta='Área', line_close=True, range_r=[0,5])
                fig.update_traces(fill='toself', line_color="#d4af37", line_width=2)
                fig.update_layout(polar=dict(bgcolor="rgba(255,255,255,0.5)"), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("🧠 El Oráculo de la Armadura")
                
                if st.session_state['resumen_ia']:
                    st.markdown(f"<div class='resumen-caja'>✨ {st.session_state['resumen_ia']}</div>", unsafe_allow_html=True)

                if st.session_state['diagnostico_detallado']:
                    with st.expander("🔍 VER ESTADO TÉCNICO DE LAS PIEZAS", expanded=False):
                        st.markdown(f"<div class='diagnostico-full'>{st.session_state['diagnostico_detallado']}</div>", unsafe_allow_html=True)
                        
                        if st.session_state['df_historico'] is not None:
                            st.divider()
                            st.markdown("#### 📈 Evolución Histórica")
                            fig_trend = px.line(st.session_state['df_historico'], x="Periodo", y="Puntaje", color="Área", markers=True)
                            fig_trend.update_layout(
                                plot_bgcolor="white", paper_bgcolor="rgba(0,0,0,0)", height=300,
                                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                            )
                            st.plotly_chart(fig_trend, use_container_width=True)

                st.divider()
                vulnerables = df[df['Puntaje'] < 3.8]
                if not vulnerables.empty:
                    mas_debil = vulnerables.loc[vulnerables['Puntaje'].idxmin()]
                    st.error(f"🚨 **PRIORIDAD:** El {mas_debil['Pieza']} requiere forja inmediata.")
                    
                    if st.button(f"🔥 Entrar a Mesa de Crisis: {mas_debil['Pieza'].upper()}"):
                        if 'model' in st.session_state:
                            with st.spinner("Preparando simulador de crisis..."):
                                st.session_state.mision_data = generar_mision_ia(mas_debil['Área'])
                                st.session_state.area_reparar = mas_debil['Área']
                                st.session_state.view = 'mision'
                                st.rerun()
                        else: st.warning("Conecte la Llave Maestra.")
                else:
                    st.success("✨ **INTEGRIDAD TOTAL:** Tu armadura es impenetrable.")