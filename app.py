import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Titán Estudiante - El Despertar", layout="wide", page_icon="🛡️")

# --- LÓGICA DE PROCESAMIENTO DE ADN ---
def procesar_adn(file):
    try:
        # Leer Excel
        df = pd.read_excel(file)
        
        # Limpieza básica
        df = df.dropna(subset=['COMPONENTE'])
        exclude = ['INGLES', 'BAJO', 'BÁSICO', 'BASICO', 'ALTO', 'SUPERIOR', 'TOTAL']
        df = df[~df['COMPONENTE'].str.upper().isin(exclude)]
        df['PROMEDIO'] = pd.to_numeric(df['PROMEDIO'], errors='coerce')
        df = df.dropna(subset=['PROMEDIO'])

        # Mapeo a Áreas ICFES
        mapping = {
            'Matemáticas': ['Numérico', 'Métrico', 'Aleatorio'],
            'Lectura Crítica': ['Pragmático Lector', 'Pragmático Escritor'],
            'Ciencias Naturales': ['Naturales', 'Fisica', 'Quimica', 'Biologia'],
            'Sociales y Ciudadanas': ['Sociales'],
            'Inglés': ['Grammar', 'Communication', 'Reading Plan']
        }

        adn_calculado = []
        for area, lista_componentes in mapping.items():
            # Filtramos las filas que coincidan con los componentes de esta área
            sub_df = df[df['COMPONENTE'].isin(lista_componentes)]
            promedio = round(sub_df['PROMEDIO'].mean(), 2) if not sub_df.empty else 0.0
            
            # Definir estado y pieza
            mapeo_piezas = {
                "Matemáticas": "Peto", 
                "Lectura Crítica": "Yelmo", 
                "Ciencias Naturales": "Grebas", 
                "Sociales y Ciudadanas": "Escudo", 
                "Inglés": "Guantelete"
            }
            pieza = mapeo_piezas.get(area, "Armadura")
            
            # Lógica de estados
            if promedio >= 4.5:
                estado = "Oro"
            elif promedio >= 3.8:
                estado = "Plata"
            else:
                estado = "Bronce"
            
            adn_calculado.append({
                "Área": area,
                "Puntaje": promedio,
                "Pieza": pieza,
                "Estado": estado
            })
        
        return pd.DataFrame(adn_calculado)
    except Exception as e:
        st.error(f"Error técnico en el motor: {e}")
        return None

# --- INTERFAZ STREAMLIT ---
st.title("🛡️ TITÁN ESTUDIANTE: El Despertar")
st.markdown("### Cargue de ADN Académico Institucional")

# Sección de Carga
uploaded_file = st.file_uploader("Arrastra aquí el Excel de notas", type=["xlsx"])

if uploaded_file:
    with st.spinner('Titán está analizando el ADN...'):
        df_