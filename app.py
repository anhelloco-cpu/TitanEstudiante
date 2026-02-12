import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import json
import re

# 1. --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="TITÁN ESTUDIANTE v115", layout="wide", page_icon="🛡️")

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

# --- 2. ESTILOS VISUALES (Fondo Blanco y Estética Profesional) ---
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

    /* Caja de Resumen Épico */
    .resumen-caja {
        background-color: #f8fafc; border-radius: 12px; padding: 20px;
        border: 1px solid #e2e8f0; border-left: 6px solid #d4af37;
        margin-bottom: 15px; font-size: 1.1em; line-height: 1.6;
        color: #1e293b; font-weight: 500;
    }

    /* Estilo para el diagnóstico detallado dentro del expander */
    .diagnostico-full {
        font-size: 1em; line-height: 1.8; color: #334155;
        white-space: pre-wrap;
    }

    .alerta-daño { color: #ff4b4b; font-weight: bold; animation: pulse 1.5s infinite; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    
    .stButton>button { border-radius: 8px; font-weight: bold; transition: all 0.3s; }
</style>
""", unsafe_allow_html=True)

# --- 3. FUNCIONES DE IA (Cerebro del Titán con Mapeo de Armadura) ---
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
    prompt = f"""Genera un caso tipo ICFES para {area} y 3 preguntas A,B,C,D. 
    Devuelve JSON: {{ "caso": "...", "preguntas": [ {{"enunciado": "...", "opciones": {{"A":"..."}}, "correcta": "letra"}}, ... ] }}"""
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
    prog = st.session_state.progreso_mision
    
    st.title(f"⚒️ Forja de Reparación: {st.session_state.area_reparar}")
    st.markdown(f'<div class="pergamino"><b>CONTEXTO DEL CASO:</b><br>{data["caso"]}</div>', unsafe_allow_html=True)
    
    if not prog['terminada']:
        q = data["preguntas"][prog['idx']]
        st.subheader(f"Desafío {prog['idx'] + 1} de 3")
        st.write(f"**{q['enunciado']}**")
        
        opcion_elegida = st.radio("Selecciona tu respuesta:", list(q["opciones"].values()), key=f"radio_q_{prog['idx']}")
        
        if st.button("ENTREGAR RESPUESTA"):
            letra_sel = [k for k, v in q["opciones"].items() if v == opcion_elegida][0]
            if letra_sel == q["correcta"]:
                st.success("✨ ¡ACIERTO!")
                st.session_state.progreso_mision['correctas'] += 1
            else:
                st.error(f"❌ FALLO. Era la {q['correcta']}.")
            
            if prog['idx'] < 2:
                st.session_state.progreso_mision['idx'] += 1
            else:
                st.session_state.progreso_mision['terminada'] = True
            st.rerun()
    else:
        st.divider()
        if prog['correctas'] >= 2:
            st.balloons()
            st.success(f"🛡️ **PIEZA REPARADA:** {prog['correctas']}/3 aciertos.")
            df = st.session_state.df_adn
            idx = df[df['Área'] == st.session_state.area_reparar].index
            df.loc[idx, ['Puntaje', 'Estado', 'Salud']] = [4.7, "Oro", 94]
        else:
            st.error("🏚️ **FORJA FALLIDA.**")
        
        if st.button("VOLVER AL DASHBOARD"):
            st.session_state.view = 'dashboard'
            st.session_state.mision_data = None
            st.session_state.progreso_mision = {'idx': 0, 'correctas': 0, 'terminada': False}
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
                    c_txt = "#ff4b4b" if es_bronce else "#2b2d33"
                    label = "¡DAÑADA!" if es_bronce else row['Estado']
                    st.markdown(f"<span style='color:{c_txt}; font-weight:bold;'>{row['Pieza']}</span> ({row['Área']}): {row['Puntaje']} | {label}", unsafe_allow_html=True)
                    st.progress(row['Salud'] / 100)
                
                st.divider()
                fig = px.line_polar(df, r='Puntaje', theta='Área', line_close=True, range_r=[0,5])
                fig.update_traces(fill='toself', line_color="#d4af37")
                fig.update_layout(polar=dict(bgcolor="white"), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("🧠 El Oráculo de la Armadura")
                
                # --- CAPA 1: RESUMEN ÉPICO ---
                if st.session_state['resumen_ia']:
                    st.markdown(f"<div class='resumen-caja'>✨ {st.session_state['resumen_ia']}</div>", unsafe_allow_html=True)

                # --- CAPA 2: DIAGNÓSTICO DETALLADO (DESPLEGABLE) ---
                if st.session_state['diagnostico_detallado']:
                    with st.expander("🔍 VER ESTADO TÉCNICO DE LAS PIEZAS", expanded=False):
                        st.markdown(f"<div class='diagnostico-full'>{st.session_state['diagnostico_detallado']}</div>", unsafe_allow_html=True)
                        
                        # --- GRÁFICA DE TENDENCIA DENTRO DEL DESPLEGABLE ---
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
                    for _, row in vulnerables.iterrows():
                        if row['Área'] == mas_debil['Área']:
                            st.error(f"🚨 **PRIORIDAD:** El {row['Pieza']} requiere forja inmediata.")
                        else:
                            st.warning(f"⚠️ **VULNERABLE:** El {row['Pieza']} tiene fisuras.")
                    
                    st.divider()
                    st.subheader("⚒️ Taller de Mentores")
                    if st.button(f"🔥 Forjar Reparación: {mas_debil['Pieza'].upper()}"):
                        if 'model' in st.session_state:
                            with st.spinner("Generando 3 desafíos interactivos..."):
                                st.session_state.mision_data = generar_mision_ia(mas_debil['Área'])
                                st.session_state.area_reparar = mas_debil['Área']
                                st.session_state.view = 'mision'
                                st.rerun()
                        else: st.warning("Conecte la Llave Maestra.")
                else:
                    st.success("✨ **INTEGRIDAD TOTAL:** Tu armadura es impenetrable.")