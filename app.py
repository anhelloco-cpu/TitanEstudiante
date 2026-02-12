import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai

# 1. --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Titán Estudiante - Dashboard", layout="wide", page_icon="🛡️")

# Inicializar estados de la IA
if 'view' not in st.session_state:
    st.session_state['view'] = 'dashboard'
if 'mision_ia' not in st.session_state:
    st.session_state['mision_ia'] = ""

# --- 2. ESTILOS VISUALES (Fondo Blanco y Letras Oscuras) ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #2b2d33; }
    [data-testid="stSidebar"] { background-color: #f7f7f7; }
    .stMetric { background-color: #f7f7f7; border: 1px solid #3d4156; padding: 10px; border-radius: 12px; }
    .alerta-daño { color: #ff4b4b; font-weight: bold; animation: pulse 1.5s infinite; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    .pergamino { background-color: #fff9eb; color: #2b2d33; padding: 25px; border-radius: 10px; border: 1px solid #d4af37; border-left: 8px solid #d4af37; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LÓGICA DE LA IA TITÁN (Conexión) ---
with st.sidebar:
    st.header("🔑 Conexión IA")
    user_api_key = st.text_input("Pega tu API Key de Gemini:", type="password")
    if user_api_key:
        try:
            genai.configure(api_key=user_api_key)
            # Usamos el modelo con el nombre correcto para evitar el error 404
            model = genai.GenerativeModel('gemini-1.5-flash')
            st.success("IA Conectada")
        except Exception as e:
            st.error(f"Error de configuración: {e}")

# --- FUNCIÓN GENERADORA (CORREGIDA LA IDENTACIÓN AQUÍ) ---
def generar_mision_con_ia(area):
    if not user_api_key: 
        return "❌ Error: No has ingresado la API Key en la barra lateral."
    
    prompt = f"""
    Eres el Titán Protector, experto en el examen ICFES Saber 11 de Colombia.
    Analiza la debilidad en {area}. 
    Genera una misión de entrenamiento real basada en la complejidad de los cuadernillos 2024/2025:
    1. Un texto de análisis técnico o literario.
    2. Una pregunta de selección múltiple (A, B, C, D).
    3. Respuesta correcta y una breve explicación técnica.
    Usa un lenguaje motivador de guerrero.
    """
    
    try:
        # Todo este bloque está dentro de la función (8 espacios de indentación)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ El Oráculo dice: {str(e)}"

# --- 4. LÓGICA DE PROCESAMIENTO ADN ---
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
        st.error(f"Error en el motor: {e}"); return None

# --- 5. NAVEGACIÓN ENTRE DASHBOARD Y MISIÓN ---
if st.session_state['view'] == 'mision':
    st.markdown("## ⚒️ FORJA DE REPARACIÓN")
    st.markdown(f'<div class="pergamino">{st.session_state["mision_ia"]}</div>', unsafe_allow_html=True)
    if st.button("TERMINAR REPARACIÓN Y VOLVER"):
        st.session_state['view'] = 'dashboard'
        st.rerun()

else:
    # --- INTERFAZ DASHBOARD ---
    st.title("🛡️ TITÁN ESTUDIANTE: El Despertar")
    st.markdown("---")
    archivo = st.file_uploader("Cargue el Excel de Notas para despertar al Titán", type=["xlsx"])

    if archivo:
        df_adn = procesar_adn(archivo)
        if df_adn is not None:
            promedio_gral = df_adn['Puntaje'].mean()
            
            # Lógica de Avatar
            if promedio_gral >= 4.5: rango, color_r = "TITÁN LEGENDARIO", "#d4af37"
            elif promedio_gral >= 3.8: rango, color_r = "GUERRERO VETERANO", "#7f8c8d"
            else: rango, color_r = "RECLUTA EN FORJA", "#a0522d"
            
            img_url = "https://www.freepik.com/premium-psd/ornate-medieval-armor-knights-cuirass_412654456.htm"

            with st.sidebar:
                st.markdown(f"<h1 style='text-align: center; color: {color_r};'>{rango}</h1>", unsafe_allow_html=True)
                st.image(img_url, use_column_width=True)
                st.metric("PODER TOTAL", round(promedio_gral, 2))
                st.divider()
                st.write("📍 **Clan:** Grado 10-A")

            col1, col2 = st.columns([1, 1])

            with col1:
                st.subheader("⚔️ Inventario de Armadura")
                for _, row in df_adn.iterrows():
                    if row['Estado'] == "Bronce":
                        st.markdown(f"<span style='color: #00262e;'>**{row['Pieza']}** ({row['Área']}): **{row['Puntaje']}**</span> | <span class='alerta-daño'>¡PIEZA DAÑADA!</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<span style='color: #00262e;'>**{row['Pieza']}** ({row['Área']}): **{row['Puntaje']}** | Nivel {row['Estado']}</span>", unsafe_allow_html=True)
                    st.progress(row['Salud'] / 100)
                
                st.divider()
                fig = px.line_polar(df_adn, r='Puntaje', theta='Área', line_close=True, range_r=[0,5])
                fig.update_traces(fill='toself', line_color=color_r)
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", polar=dict(bgcolor="white"))
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("🧠 Diagnóstico de la IA")
                vulnerables = df_adn[df_adn['Puntaje'] < 3.8]
                if not vulnerables.empty:
                    for _, row in vulnerables.iterrows():
                        st.error(f"⚠️ **Punto de Quiebre:** Tu {row['Pieza']} ({row['Área']}) está vulnerable.")
                    
                    st.markdown("---")
                    st.subheader("⚒️ Taller de Mentores")
                    mas_critica = vulnerables.loc[vulnerables['Puntaje'].idxmin()]
                    
                    if st.button(f"🔥 Forjar Reparación: {mas_critica['Área']}"):
                        if user_api_key:
                            with st.spinner("IA generando reto real..."):
                                st.session_state['mision_ia'] = generar_mision_con_ia(mas_critica['Área'])
                                st.session_state['view'] = 'mision'
                                st.rerun()
                        else: st.warning("Conecta la API Key en la barra lateral primero.")
                else:
                    st.success("✅ Integridad Total.")

                st.markdown("---")
                st.subheader("🏆 Gesta del Clan")
                st.write("**Meta Grupal:** Salida a Cine")
                st.progress(65)