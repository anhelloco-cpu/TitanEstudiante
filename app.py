import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración épica
st.set_page_config(page_title="Titán Estudiante - Simulador de Forja", layout="wide", page_icon="⚔️")

# --- ESTILOS DE JUEGO ---
st.markdown("""
    <style>
    .stMetric { background-color: #1c2030; border: 2px solid #3d4156; padding: 10px; border-radius: 10px; }
    .reparacion-critica { color: #ff4b4b; font-weight: bold; animation: pulse 1.5s infinite; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR DE PROCESAMIENTO ---
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
            
            # Lógica de Salud de la Armadura
            if promedio >= 4.5: estado, salud = "ORO", 100
            elif promedio >= 3.8: estado, salud = "PLATA", 70
            else: estado, salud = "¡DAÑADA!", 25
            
            adn_calculado.append({"Área": area, "Puntaje": promedio, "Pieza": piezas[area], "Estado": estado, "Salud": salud})
        
        return pd.DataFrame(adn_calculado)
    except: return None

# --- INTERFAZ ---
st.title("🛡️ TITÁN ESTUDIANTE: El Despertar del Guerrero")
archivo = st.file_uploader("Sube el Excel de Salvador para activar la armadura", type=["xlsx"])

if archivo:
    df_adn = procesar_adn(archivo)
    if df_adn is not None:
        promedio_total = df_adn['Puntaje'].mean()
        
        # --- SELECCIÓN DE GUERRERO (IMÁGENES REALES) ---
        if promedio_total >= 4.5:
            rango, color = "TITÁN LEGENDARIO", "#FFD700"
            # Imagen de Guerrero de Oro
            img_url = "https://img.freepik.com/foto-gratis/caballero-armadura-dorada-brillante-iluminacion-dramatica_933496-18012.jpg"
        elif promedio_total >= 3.8:
            rango, color = "GUERRERO VETERANO", "#C0C0C0"
            # Imagen de Guerrero de Plata
            img_url = "https://img.freepik.com/foto-gratis/caballero-armadura-plata-posando-fondo-oscuro_933496-17495.jpg"
        else:
            rango, color = "RECLUTA EN FORJA", "#CD7F32"
            # Imagen de Guerrero con armadura gastada
            img_url = "https://img.freepik.com/foto-gratis/guerrero-medieval-pie-campo-batalla-armadura-rota_933496-19200.jpg"

        # Sidebar con el Avatar del Guerrero
        with st.sidebar:
            st.markdown(f"<h1 style='text-align: center; color: {color};'>{rango}</h1>", unsafe_allow_html=True)
            st.image(img_url, use_column_width=True)
            st.metric("PUNTOS DE PODER TOTAL", round(promedio_total, 2))
            st.divider()
            st.info("🛡️ **Clan:** Grado 10-A\n\n🏆 **Objetivo:** Tarde de Integración")

        # Pantalla Central
        col_inv, col_radar = st.columns([1, 1])

        with col_inv:
            st.subheader("🛠️ Inventario y Salud de Armadura")
            for _, row in df_adn.iterrows():
                with st.container():
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        st.write(f"**{row['Pieza']}** ({row['Área']})")
                    with c2:
                        if row['Estado'] == "¡DAÑADA!":
                            st.markdown(f"<span class='reparacion-critica'>{row['Estado']}</span>", unsafe_allow_html=True)
                        else:
                            st.write(f"Nivel {row['Estado']}")
                    st.progress(row['Salud'] / 100)

        with col_radar:
            st.subheader("📊 Análisis de Competencias")
            fig = px.line_polar(df_adn, r='Puntaje', theta='Área', line_close=True, range_r=[0,5])
            fig.update_traces(fill='toself', line_color=color)
            st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # --- TALLER DE REPARACIÓN (SIMULACIÓN) ---
        st.header("⚒️ Taller de los Mentores")
        pieza_debil = df_adn.loc[df_adn['Puntaje'].idxmin()]
        
        if pieza_debil['Puntaje'] < 3.8:
            st.error(f"¡ALERTA! El **{pieza_debil['Pieza']}** está en estado crítico por fallas en **{pieza_debil['Área']}**.")
            if st.button("🔥 FORJAR MISIÓN DE REPARACIÓN"):
                st.balloons()
                st.success(f"¡Misión de {pieza_debil['Área']} activada para Salvador!")
                st.write("1. Análisis de Lectura Crítica\n2. Inferencia de Textos\n3. Práctica de Competencias")
        else:
            st.success("Toda la armadura está en buen estado. ¡Sigue entrenando!")

else:
    st.info("Esperando el ADN... Sube el archivo Excel para despertar al Guerrero.")