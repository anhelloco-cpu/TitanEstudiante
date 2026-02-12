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
        df_adn = procesar_adn(uploaded_file)
    
    if df_adn is not None and not df_adn.empty:
        st.success("¡ADN Extraído con éxito!")
        
        # --- DASHBOARD ---
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Estado de la Armadura")
            for _, row in df_adn.iterrows():
                # Color rojo si es nivel Bronce (menos de 3.8)
                delta_color = "normal" if row['Puntaje'] >= 3.8 else "inverse"
                st.metric(
                    label=f"{row['Pieza']} ({row['Área']})", 
                    value=row['Puntaje'], 
                    delta=row['Estado'], 
                    delta_color=delta_color
                )

        with col2:
            st.subheader("Radar de Competencias")
            fig = px.line_polar(df_adn, r='Puntaje', theta='Área', line_close=True, range_r=[0,5])
            fig.update_traces(fill='toself', line_color='#00D4FF')
            st.plotly_chart(fig, use_container_width=True)

        st.divider()
        
        # --- MENTORES Y PROTECTORES ---
        c1, c2, c3 = st.columns(3)
        
        with c1:
            # Detectar el área más baja para la misión
            area_debil = df_adn.loc[df_adn['Puntaje'].idxmin()]
            st.info(f"⚒️ **Taller de Mentores**\n\nDebilidad detectada en: **{area_debil['Área']}**")
            if st.button("Generar Misión de Refuerzo"):
                st.write(f"Generando misiones para reparar el {area_debil['Pieza']}...")

        with c2:
            st.warning("🏰 **Protectores del Santuario**\n\nIncentivo Grupal: Tarde de Pizza\nProgreso: 65%")
            
        with c3:
            st.success("👥 **Gestión de Escuadrones**\n\n3 Escuadrones activos reparando el Peto de Matemáticas.")

else:
    st.info("Por favor, cargue un archivo Excel para iniciar el diagnóstico.")