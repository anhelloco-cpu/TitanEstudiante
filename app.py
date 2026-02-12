import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Titán Estudiante - Dashboard", layout="wide", page_icon="🛡️")

# --- LÓGICA DE PROCESAMIENTO ---
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
            
            mapeo_piezas = {
                "Matemáticas": "Peto", "Lectura Crítica": "Yelmo", 
                "Ciencias Naturales": "Grebas", "Sociales y Ciudadanas": "Escudo", "Inglés": "Guantelete"
            }
            
            estado = "Oro" if promedio >= 4.5 else "Plata" if promedio >= 3.8 else "Bronce"
            
            adn_calculado.append({
                "Área": area, "Puntaje": promedio, "Pieza": mapeo_piezas.get(area), "Estado": estado
            })
        
        return pd.DataFrame(adn_calculado)
    except Exception as e:
        st.error(f"Error en el motor: {e}")
        return None

# --- INTERFAZ ---
st.title("🛡️ TITÁN ESTUDIANTE: El Despertar")
st.sidebar.markdown("# Perfil del Guerrero")

archivo = st.file_uploader("Cargue el Excel de Notas para despertar al Titán", type=["xlsx"])

if archivo:
    df_adn = procesar_adn(archivo)
    
    if df_adn is not None:
        promedio_gral = df_adn['Puntaje'].mean()
        
        # --- LÓGICA DE AVATAR ---
        if promedio_gral >= 4.5:
            rango = "GUERRERO LEGENDARIO"
            img_url = "https://cdn-icons-png.flaticon.com/512/3534/3534063.png" # Icono Oro
            color_rango = "#FFD700"
        elif promedio_gral >= 3.8:
            rango = "GUERRERO VETERANO"
            img_url = "https://cdn-icons-png.flaticon.com/512/3534/3534033.png" # Icono Plata
            color_rango = "#C0C0C0"
        else:
            rango = "RECLUTA EN ENTRENAMIENTO"
            img_url = "https://cdn-icons-png.flaticon.com/512/3534/3534020.png" # Icono Bronce
            color_rango = "#CD7F32"

        # Sidebar con Avatar
        with st.sidebar:
            st.image(img_url, width=200)
            st.markdown(f"<h2 style='text-align: center; color: {color_rango};'>{rango}</h2>", unsafe_allow_html=True)
            st.metric("Poder Total (Promedio)", round(promedio_gral, 2))
            st.divider()
            st.write("📍 **Clan:** Grado 10-A")
            st.write("🏰 **Santuario:** Protegido")

        # Main Dashboard
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("⚔️ Estado de la Armadura")
            for _, row in df_adn.iterrows():
                # Alerta visual si la pieza está en Bronce
                emoji = "🔴" if row['Estado'] == "Bronce" else "🟢"
                st.write(f"{emoji} **{row['Pieza']} ({row['Área']}):** {row['Puntaje']} - *Nivel {row['Estado']}*")
            
            st.divider()
            # Radar Chart
            fig = px.line_polar(df_adn, r='Puntaje', theta='Área', line_close=True, range_r=[0,5])
            fig.update_traces(fill='toself', line_color=color_rango)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("🧠 Diagnóstico de la IA")
            pieza_debil = df_adn.loc[df_adn['Puntaje'].idxmin()]
            
            st.error(f"**Punto de Quiebre detectado:** Tu {pieza_debil['Pieza']} está vulnerable.")
            st.write(f"La competencia de **{pieza_debil['Área']}** necesita refuerzo inmediato en el Taller de Mentores.")
            
            st.markdown("---")
            st.subheader("⚒️ Taller de Mentores")
            if st.button("Forjar Misión de Reparación"):
                st.success(f"Misión de {pieza_debil['Área']} enviada al pergamino del Guerrero.")

            st.markdown("---")
            st.subheader("🏆 Gesta del Clan (Incentivo)")
            st.write("**Meta Grupal:** Salida a Cine")
            st.progress(65)
            st.caption("Falta un 35% de esfuerzo colectivo para desbloquear.")

else:
    st.info("Esperando el ADN Académico... Por favor cargue el archivo Excel.")
    # Imagen de placeholder para el avatar vacío
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1144/1144760.png", width=200)
    st.sidebar.caption("Avatar pendiente de evolución")