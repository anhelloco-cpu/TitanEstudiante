import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Titán Estudiante", layout="wide")

# --- LÓGICA DE PROCESAMIENTO (Igual a la anterior) ---
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
            pieza = {"Matemáticas": "Peto", "Lectura Crítica": "Yelmo", "Ciencias Naturales": "Grebas", "Sociales y Ciudadanas": "Escudo", "Inglés": "Guantelete"}[area]
            estado = "Oro" if promedio >= 4.5 else "Plata" if promedio >= 3.8 else "Bronce"
            adn_calculado.append({"Área": area, "Puntaje": promedio, "Pieza": pieza, "Estado": estado})
        return pd.DataFrame(adn_calculado)
    except: return None

# --- ESTILOS DE GUERRERO ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #0e1117; border-right: 2px solid #00d4ff; }
    .stProgress > div > div > div > div { background-color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ TITÁN ESTUDIANTE: El Despertar")

archivo = st.file_uploader("Sube el Excel de Notas", type=["xlsx"])

if archivo:
    df_adn = procesar_adn(archivo)
    if df_adn is not None:
        promedio = df_adn['Puntaje'].mean()
        
        # --- SELECCIÓN DE AVATAR DE GUERRERO ---
        if promedio >= 4.5:
            rango = "TITÁN DE ORO"
            # Imagen de un Guerrero Legendario
            url_guerrero = "https://img.freepik.com/premium-photo/golden-knight-full-armor-white-background_933496-17865.jpg"
            color = "#FFD700"
        elif promedio >= 3.8:
            rango = "CABALLERO DE PLATA"
            # Imagen de un Guerrero Veterano
            url_guerrero = "https://img.freepik.com/premium-photo/knight-shining-armor-standing-tall_933496-17482.jpg"
            color = "#C0C0C0"
        else:
            rango = "RECLUTA DE BRONCE"
            # Imagen de un Guerrero Iniciado
            url_guerrero = "https://img.freepik.com/premium-photo/medieval-knight-armor-standing-white-background_933496-17520.jpg"
            color = "#CD7F32"

        # Mostrar el Guerrero en la Sidebar
        with st.sidebar:
            st.markdown(f"<h1 style='text-align: center; color: {color};'>{rango}</h1>", unsafe_allow_html=True)
            st.image(url_guerrero, use_column_width=True)
            st.metric("PODER TOTAL", round(promedio, 2))
            st.progress(int((promedio/5)*100))

        # El resto del Dashboard
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Estado de la Armadura")
            st.table(df_adn[['Área', 'Puntaje', 'Estado']])
        with c2:
            fig = px.line_polar(df_adn, r='Puntaje', theta='Área', line_close=True)
            st.plotly_chart(fig)