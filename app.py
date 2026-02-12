import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página con tema oscuro por defecto
st.set_page_config(
    page_title="Titán Estudiante - Dashboard", 
    layout="wide", 
    page_icon="🛡️"
)

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

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3d4156; }
    .avatar-frame {
        border-radius: 50%;
        padding: 5px;
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 180px;
        border: 4px solid #00d4ff;
        box-shadow: 0 0 20px #00d4ff;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INTERFAZ ---
st.title("🛡️ TITÁN ESTUDIANTE: El Despertar")
st.markdown("---")

archivo = st.file_uploader("📂 Cargue el ADN Académico (Excel) para evolucionar", type=["xlsx"])

if archivo:
    df_adn = procesar_adn(archivo)
    
    if df_adn is not None:
        promedio_gral = df_adn['Puntaje'].mean()
        
        # --- LÓGICA DE AVATAR MODERNO ---
        # He seleccionado URLs de avatares estilo "Knight/Titan" modernos
        if promedio_gral >= 4.5:
            rango = "TITÁN LEGENDARIO"
            # Avatar Guerrero Dorado High Tech
            img_url = "https://cdn-icons-png.flaticon.com/512/11100/11100067.png" 
            color_rango = "#FFD700"
            glow_color = "rgba(255, 215, 0, 0.6)"
        elif promedio_gral >= 3.8:
            rango = "GUERRERO DE ELITE"
            # Avatar Caballero de Plata
            img_url = "https://cdn-icons-png.flaticon.com/512/11100/11100057.png" 
            color_rango = "#C0C0C0"
            glow_color = "rgba(192, 192, 192, 0.6)"
        else:
            rango = "ESCUDERO EN FORJA"
            # Avatar Recluta
            img_url = "https://cdn-icons-png.flaticon.com/512/11100/11100051.png" 
            color_rango = "#CD7F32"
            glow_color = "rgba(205, 127, 50, 0.6)"

        # Sidebar con Avatar Moderno y Efectos
        with st.sidebar:
            st.markdown(f"""
                <div style="text-align: center;">
                    <img src="{img_url}" style="border-radius: 20px; width: 100%; border: 3px solid {color_rango}; box-shadow: 0 0 15px {glow_color};">
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"<h2 style='text-align: center; color: {color_rango}; margin-top: 10px;'>{rango}</h2>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; font-size: 20px;'>Nivel de Poder: <b>{round(promedio_gral, 2)}</b></p>", unsafe_allow_html=True)
            
            st.divider()
            st.info("🛡️ **Clan:** Grado 10-A\n\n🎯 **Misión:** Rumbo al Saber 11")

        # Layout Principal
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("⚔️ Estado de la Armadura")
            for _, row in df_adn.iterrows():
                estado_display = f"<span style='color: {color_rango if row['Estado'] != 'Bronce' else '#FF4B4B'};'>Nivel {row['Estado']}</span>"
                st.markdown(f"**{row['Pieza']}** ({row['Área']}): **{row['Puntaje']}** | {estado_display}", unsafe_allow_html=True)
            
            st.divider()
            # Radar Chart con estilo oscuro
            fig = px.line_polar(df_adn, r='Puntaje', theta='Área', line_close=True, range_r=[0,5])
            fig.update_traces(fill='toself', line_color=color_rango, line_width=3)
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 5], gridcolor="#444"),
                    angularaxis=dict(gridcolor="#444")
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="white"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("🧠 Diagnóstico de la IA Titán")
            pieza_debil = df_adn.loc[df_adn['Puntaje'].idxmin()]
            
            st.error(f"⚠️ **BRECHA DETECTADA:** El **{pieza_debil['Pieza']}** está sufriendo daños.")
            st.write(f"Los resultados en **{pieza_debil['Área']}** están por debajo del umbral de excelencia académica.")
            
            st.markdown("---")
            st.subheader("⚒️ Taller de Mentores")
            if st.button("🔥 FORJAR MISIÓN DE REPARACIÓN"):
                st.success(f"¡Misión 'Sabiduría de {pieza_debil['Área']}' forjada! Salvador ha recibido la notificación.")

            st.markdown("---")
            st.subheader("🏆 Incentivo de los Protectores")
            st.markdown("🎯 **Objetivo:** Salida a Cine + Cena")
            progreso_barra = int((promedio_gral / 5.0) * 100)
            st.progress(progreso_barra)
            st.caption(f"El Clan ha completado el {progreso_barra}% de la gesta necesaria.")

else:
    # Pantalla de Bienvenida cuando no hay archivo
    col_inv, col_text = st.columns([1, 2])
    with col_inv:
        st.image("https://cdn-icons-png.flaticon.com/512/11100/11100045.png", width=250)
    with col_text:
        st.header("Esperando el ADN del Guerrero...")
        st.write("Cargue el archivo de notas para generar el avatar dinámico y el análisis de armadura.")
    
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/11100/11100045.png", width=200)
        st.caption("Evolución pendiente de datos...")