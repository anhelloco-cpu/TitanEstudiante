import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai

# --- 1. CONFIGURACIÓN DE LA IA TITÁN (API KEY) ---
# Pega tu clave aquí o ponla en el buscador de la App para que sea secreta
API_KEY = "TU_API_KEY_AQUÍ" 

if API_KEY != "TU_API_KEY_AQUÍ":
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.warning("⚠️ Titán en modo espera: Por favor ingresa tu API Key en el código.")

# --- 2. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Titán Estudiante - Live AI", layout="wide", page_icon="🛡️")

if 'view' not in st.session_state:
    st.session_state['view'] = 'dashboard'
if 'mision_ia' not in st.session_state:
    st.session_state['mision_ia'] = None

# --- 3. ESTILOS VISUALES (Blanco Moderno) ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #2b2d33; }
    [data-testid="stSidebar"] { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; border: 1px solid #d1d5db; border-radius: 12px; }
    .alerta-daño { color: #ff4b4b; font-weight: bold; animation: pulse 1.5s infinite; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    .pergamino { background-color: #fffcf5; color: #2b2d33; padding: 25px; border-radius: 10px; border-left: 8px solid #d4af37; border: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. MOTOR DE PROCESAMIENTO ---
def procesar_adn(file):
    try:
        df = pd.read_excel(file)
        df = df.dropna(subset=['COMPONENTE'])
        exclude = ['INGLES', 'BAJO', 'BÁSICO', 'BASICO', 'ALTO', 'SUPERIOR', 'TOTAL']
        df = df[~df['COMPONENTE'].str.upper().isin(exclude)]
        df['PROMEDIO'] = pd.to_numeric(df['PROMEDIO'], errors='coerce')
        df = df.dropna(subset=['PROMEDIO'])
        mapping = {
            'Matemáticas': ['Numérico', 'Métrico', 'Aleatorio'],
            'Lectura Crítica': ['Pragmático Lector', 'Pragmático Escritor'],
            'Ciencias Naturales': ['Naturales', 'Fisica', 'Quimica', 'Biologia'],
            'Sociales y Ciudadanas': ['Sociales'],
            'Inglés': ['Grammar', 'Communication', 'Reading Plan']
        }
        adn_calculado = []
        for area, lista_comp in mapping.items():
            sub_df = df[df['COMPONENTE'].isin(lista_comp)]
            promedio = round(sub_df['PROMEDIO'].mean(), 2) if not sub_df.empty else 0.0
            mapeo_piezas = {"Matemáticas": "Peto", "Lectura Crítica": "Yelmo", "Ciencias Naturales": "Grebas", "Sociales y Ciudadanas": "Escudo", "Inglés": "Guantelete"}
            estado = "Oro" if promedio >= 4.5 else "Plata" if promedio >= 3.8 else "Bronce"
            salud = int((promedio / 5) * 100)
            adn_calculado.append({"Área": area, "Puntaje": promedio, "Pieza": mapeo_piezas.get(area), "Estado": estado, "Salud": salud})
        return pd.DataFrame(adn_calculado)
    except Exception as e:
        st.error(f"Error en el motor: {e}")
        return None

# --- 5. LÓGICA DE LA IA (GENERACIÓN DE MISIONES) ---
def generar_mision_ia(area):
    prompt = f"""
    Actúa como el Titán Protector, experto en exámenes ICFES Saber 11 de Colombia.
    El estudiante tiene debilidad en {area}. 
    Genera un reto de nivel profesional con esta estructura exacta:
    TEXTO: (Un párrafo corto de análisis técnico o literario sobre {area})
    PREGUNTA: (Una pregunta de opción múltiple con única respuesta)
    OPCIONES: A, B, C, D
    CORRECTA: (Solo la letra y el texto de la correcta)
    JUSTIFICACIÓN: (Breve explicación de por qué es la correcta)
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "El Titán está meditando... Intenta forjar de nuevo."

# --- 6. NAVEGACIÓN ---
if st.session_state['view'] == 'mision':
    st.markdown(f"## ⚒️ FORJA DE REPARACIÓN ACTIVADA")
    st.write(st.session_state['mision_ia'])
    if st.button("FINALIZAR ENTRENAMIENTO"):
        st.session_state['view'] = 'dashboard'
        st.rerun()

else:
    st.title("🛡️ TITÁN ESTUDIANTE: El Despertar")
    st.markdown("---")
    archivo = st.file_uploader("Cargue el ADN Académico", type=["xlsx"])

    if archivo:
        df_adn = procesar_adn(archivo)
        if df_adn is not None:
            promedio_gral = df_adn['Puntaje'].mean()
            
            # Avatar dinámico
            if promedio_gral >= 4.5: rango, color_r = "TITÁN LEGENDARIO", "#d4af37"
            elif promedio_gral >= 3.8: rango, color_r = "GUERRERO VETERANO", "#7f8c8d"
            else: rango, color_r = "RECLUTA EN FORJA", "#a0522d"

            img_url = "https://cdn-icons-png.flaticon.com/512/3534/3534063.png" # Usamos icono base por ahora

            with st.sidebar:
                st.markdown(f"<h1 style='text-align: center; color: {color_r};'>{rango}</h1>", unsafe_allow_html=True)
                st.image(img_url, use_column_width=True)
                st.metric("PODER TOTAL", round(promedio_gral, 2))
                st.divider()
                # DIAGNÓSTICO LIVE IA
                if st.button("🔮 Pedir Diagnóstico al Titán"):
                    with st.spinner("El Titán analiza tu ADN..."):
                        diag_prompt = f"Basado en estos puntajes: {df_adn[['Área', 'Puntaje']].to_string()}, da un consejo de guerrero corto y motivador."
                        diagnostico = model.generate_content(diag_prompt)
                        st.info(diagnostico.text)

            col1, col2 = st.columns([1, 1])
            with col1:
                st.subheader("⚔️ Inventario de Armadura")
                for _, row in df_adn.iterrows():
                    if row['Estado'] == "Bronce":
                        st.markdown(f"<span style='color: #2b2d33;'>**{row['Pieza']}** ({row['Área']}): **{row['Puntaje']}**</span> | <span class='alerta-daño'>¡PIEZA DAÑADA!</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<span style='color: #00262e;'>**{row['Pieza']}** ({row['Área']}): **{row['Puntaje']}** | Nivel {row['Estado']}</span>", unsafe_allow_html=True)
                    st.progress(row['Salud'] / 100)
                
                fig = px.line_polar(df_adn, r='Puntaje', theta='Área', line_close=True, range_r=[0,5])
                fig.update_traces(fill='toself', line_color=color_r)
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", polar=dict(bgcolor="white"))
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("🧠 Análisis de Vulnerabilidad")
                piezas_vulnerables = df_adn[df_adn['Puntaje'] < 3.8]
                if not piezas_vulnerables.empty:
                    for _, row in piezas_vulnerables.iterrows():
                        st.error(f"⚠️ **Punto de Quiebre:** Tu {row['Pieza']} ({row['Área']}) está vulnerable.")
                    
                    st.divider()
                    mas_critica = piezas_vulnerables.loc[piezas_vulnerables['Puntaje'].idxmin()]
                    if st.button(f"🔥 Forjar Reparación IA: {mas_critica['Área']}"):
                        with st.spinner("Generando desafío ICFES único..."):
                            st.session_state['mision_ia'] = generar_mision_ia(mas_critica['Área'])
                            st.session_state['view'] = 'mision'
                            st.rerun()
                else:
                    st.success("✅ **Integridad Total:** ¡Sigue así, Titán!")
    else:
        st.info("Cargue el archivo para iniciar la conexión.")