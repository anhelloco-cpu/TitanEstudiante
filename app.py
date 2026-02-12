import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Titán Estudiante - Dashboard", layout="wide", page_icon="🛡️")

# --- ESTILOS VISUALES MODERNOS (Gris Oxford) ---
st.markdown("""
    <style>
    /* Fondo principal: Gris oscuro suave (no negro) */
    .stApp { 
        background-color: #f7f7f7; 
        color: #e0e0e0; 
    }
    
    /* Barra lateral: Un tono un poco más oscuro para dar contraste */
    [data-testid="stSidebar"] { 
        background-color: #f7f7f7; 
    }
    
    /* Tarjetas de métricas: Bordes sutiles y fondo sólido */
    .stMetric { 
        background-color: #f7f7f7; 
        border: 1px solid #3d4156; 
        padding: 10px; 
        border-radius: 12px; 
    }
    </style>
    """, unsafe_allow_html=True)

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
            # Salud basada en el puntaje
            salud = int((promedio / 5) * 100)
            
            adn_calculado.append({
                "Área": area, "Puntaje": promedio, "Pieza": mapeo_piezas.get(area), "Estado": estado, "Salud": salud
            })
        
        return pd.DataFrame(adn_calculado)
    except Exception as e:
        st.error(f"Error en el motor: {e}")
        return None

# --- INTERFAZ ---
st.title("🛡️ TITÁN ESTUDIANTE: El Despertar")
st.markdown("---")

archivo = st.file_uploader("Cargue el Excel de Notas para despertar al Titán", type=["xlsx"])

if archivo:
    df_adn = procesar_adn(archivo)
    
    if df_adn is not None:
        promedio_gral = df_adn['Puntaje'].mean()
        
    # --- LÓGICA DE AVATAR (Imagen de Freepik en todas las categorías) ---
        if promedio_gral >= 4.5:
            rango = "TITÁN LEGENDARIO"
            img_url = "https://www.freepik.com/premium-psd/ornate-medieval-armor-knights-cuirass_412654456.htm"
            color_rango = "#FFD700"
        elif promedio_gral >= 3.8:
            rango = "GUERRERO VETERANO"
            img_url = "https://www.freepik.com/premium-psd/ornate-medieval-armor-knights-cuirass_412654456.htm"
            color_rango = "#C0C0C0"
        else:
            rango = "RECLUTA EN FORJA"
            img_url = "https://www.freepik.com/premium-psd/ornate-medieval-armor-knights-cuirass_412654456.htm"
            color_rango = "#CD7F32"

        # Sidebar con el Guerrero
        with st.sidebar:
            st.markdown(f"<h1 style='text-align: center; color: {color_rango};'>{rango}</h1>", unsafe_allow_html=True)
            st.image(img_url, use_column_width=True)
            st.metric("PODER TOTAL", round(promedio_gral, 2))
            st.divider()
            st.write("📍 **Clan:** Grado 10-A")
            st.write("🏰 **Santuario:** Protegido")

        # Main Dashboard
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("⚔️ Inventario de Armadura")
            for _, row in df_adn.iterrows():
                # Si la pieza está en Bronce, activamos la alerta visual
                if row['Estado'] == "Bronce":
                    st.markdown(f"**{row['Pieza']}** ({row['Área']}): **{row['Puntaje']}** | <span class='alerta-daño'>¡PIEZA DAÑADA!</span>", unsafe_allow_html=True)
                else:
                    st.write(f"**{row['Pieza']}** ({row['Área']}): **{row['Puntaje']}** | Nivel {row['Estado']}")
                st.progress(row['Salud'] / 100)
            
            st.divider()
            # Radar Chart estilizado
            fig = px.line_polar(df_adn, r='Puntaje', theta='Área', line_close=True, range_r=[0,5])
            fig.update_traces(fill='toself', line_color=color_rango)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white")
            st.plotly_chart(fig, use_container_width=True)


with col2:
            st.subheader("🧠 Diagnóstico de la IA")
            
            # Filtramos todas las piezas que están en nivel Bronce (menor a 3.8)
            piezas_vulnerables = df_adn[df_adn['Puntaje'] < 3.8]
            
            if not piezas_vulnerables.empty:
                for _, row in piezas_vulnerables.iterrows():
                    st.error(f"⚠️ **Punto de Quiebre:** Tu {row['Pieza']} ({row['Área']}) está vulnerable.")
                
                st.write("El taller sugiere misiones de refuerzo inmediatas para estas áreas.")
            else:
                st.success("✅ **Integridad Total:** No se detectan puntos de quiebre. ¡La armadura resiste!")
            
            st.markdown("---")
            st.subheader("⚒️ Taller de Mentores")
            # Si hay debilidades, el botón de reparación se enfoca en la más crítica
            if not piezas_vulnerables.empty:
                mas_critica = piezas_vulnerables.loc[piezas_vulnerables['Puntaje'].idxmin()]
                if st.button(f"🔥 Forjar Reparación: {mas_critica['Área']}"):
                    st.success(f"Misión de {mas_critica['Área']} enviada al pergamino.")
            else:
                st.write("Sin reparaciones pendientes.")


            st.markdown("---")
            st.subheader("🏆 Gesta del Clan (Incentivo)")
            st.write("**Meta Grupal:** Salida a Cine")
            st.progress(65)
            st.caption("Falta un 35% de esfuerzo colectivo para desbloquear el tesoro.")

else:
    st.info("Esperando el ADN Académico... Por favor cargue el archivo Excel.")
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1144/1144760.png", width=200)
    st.sidebar.caption("Avatar pendiente de evolución")