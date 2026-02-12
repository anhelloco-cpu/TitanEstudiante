import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración épica de la página
st.set_page_config(page_title="Titán Estudiante - Simulador", layout="wide", page_icon="⚔️")

# --- ESTILOS DE JUEGO (CSS) ---
st.markdown("""
    <style>
    .reportview-container { background: #0e1117; }
    .stMetric { background-color: #1c2030; border: 2px solid #3d4156; padding: 10px; border-radius: 10px; }
    .reparacion-critica { color: #ff4b4b; font-weight: bold; animation: pulse 2s infinite; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR DE ADN ---
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
            
            piezas = {"Matemáticas": "Peto", "Lectura Crítica": "Yelmo", "Ciencias Naturales": "Grebas", "Sociales y Ciudadanas": "Escudo", "Inglés": "Guantelete"}
            
            # Lógica de Daño
            if promedio >= 4.5: estado, salud = "ORO", "100%"
            elif promedio >= 3.8: estado, salud = "PLATA", "75%"
            else: estado, salud = "¡DAÑADA!", "CRÍTICO"
            
            adn_calculado.append({"Área": area, "Puntaje": promedio, "Pieza": piezas[area], "Estado": estado, "Salud": salud})
        
        return pd.DataFrame(adn_calculado)
    except: return None

# --- INTERFAZ PRINCIPAL ---
st.title("🛡️ TITÁN ESTUDIANTE: El Despertar del Guerrero")
st.write("Cargue el ADN para activar el simulador de armadura.")

archivo = st.file_uploader("", type=["xlsx"])

if archivo:
    df_adn = procesar_adn(archivo)
    if df_adn is not None:
        promedio_total = df_adn['Puntaje'].mean()
        
        # --- SELECCIÓN DE GUERRERO SEGÚN PODER ---
        if promedio_total >= 4.5:
            rango, color = "TITÁN LEGENDARIO", "#FFD700"
            img_guerrero = "https://img.freepik.com/premium-photo/golden-knight-shining-armor-dramatic-lighting_933496-18012.jpg"
        elif promedio_total >= 3.8:
            rango, color = "GUERRERO VETERANO", "#C0C0C0"
            img_guerrero = "https://img.freepik.com/premium-photo/knight-silver-armor-posing-dark-background_933496-17495.jpg"
        else:
            rango, color = "RECLUTA EN FORJA", "#CD7F32"
            img_guerrero = "https://img.freepik.com/premium-photo/medieval-warrior-standing-battlefield-broken-armor_933496-19200.jpg"

        # Sidebar con el Guerrero
        with st.sidebar:
            st.markdown(f"<h1 style='text-align: center; color: {color};'>{rango}</h1>", unsafe_allow_html=True)
            st.image(img_guerrero, use_container_width=True)
            st.metric("PUNTOS DE PODER", round(promedio_total, 2))
            st.divider()
            st.write("👥 **Escuadrón:** 10-A")
            st.write("🏆 **Meta Clan:** Tarde de Integración")

        # Pantalla Central: El Taller de Reparación
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("🛠️ Inventario de Armadura")
            for _, row in df_adn.iterrows():
                with st.container():
                    c_a, c_b = st.columns([2, 1])
                    with c_a:
                        st.write(f"**{row['Pieza']}** ({row['Área']})")
                    with c_b:
                        if row['Estado'] == "¡DAÑADA!":
                            st.markdown(f"<span class='reparacion-critica'>{row['Estado']}</span>", unsafe_allow_html=True)
                        else:
                            st.write(f"Nivel {row['Estado']}")
                    st.progress(float(row['Puntaje']/5))

        with col2:
            st.subheader("📊 Radar de Competencias ICFES")
            fig = px.line_polar(df_adn, r='Puntaje', theta='Área', line_close=True, range_r=[0,5])
            fig.update_traces(fill='toself', line_color=color)
            st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # --- SECCIÓN DE SIMULACIÓN DE REPARACIÓN ---
        st.header("⚒️ Taller de los Mentores: Forja de Misiones")
        debilidad = df_adn.loc[df_adn['Puntaje'].idxmin()]
        
        col_m1, col_m2 = st.columns([2, 1])
        with col_m1:
            st.warning(f"La IA ha detectado que el **{debilidad['Pieza']}** ({debilidad['Área']}) necesita reparación inmediata.")
            st.write("Para reparar esta pieza, el Guerrero debe completar 5 misiones de entrenamiento focalizado.")
        
        with col_m2:
            if st.button("🔥 INICIAR REPARACIÓN"):
                st.balloons()
                st.success(f"¡Misiones de {debilidad['Área']} activadas!")
                st.write("1. Análisis de Textos\n2. Inferencia Lógica\n3. Vocabulario Crítico")