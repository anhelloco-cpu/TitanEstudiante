import streamlit as st
import pandas as pd
import plotly.express as px

# 1. --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Titán Estudiante - Dashboard", layout="wide", page_icon="🛡️")

# Inicializar el estado de navegación para el Simulador
if 'view' not in st.session_state:
    st.session_state['view'] = 'dashboard'

# --- 2. ESTILOS VISUALES (Fondo Blanco Moderno) ---
st.markdown("""
    <style>
    /* Fondo principal Blanco */
    .stApp { 
        background-color: #ffffff; 
        color: #2b2d33; 
    }
    
    /* Barra lateral Gris muy claro */
    [data-testid="stSidebar"] { 
        background-color: #f0f2f6; 
    }
    
    /* Tarjetas de métricas blancas con borde gris */
    .stMetric { 
        background-color: #ffffff; 
        border: 1px solid #d1d5db; 
        padding: 10px; 
        border-radius: 12px; 
        color: #2b2d33;
    }

    /* Alerta de daño parpadeante en Rojo */
    .alerta-daño { 
        color: #ff4b4b; 
        font-weight: bold; 
        animation: pulse 1.5s infinite; 
    }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    
    /* Estilo Pergamino para la Misión */
    .pergamino { 
        background-color: #fff9eb; 
        color: #2b2d33; 
        padding: 25px; 
        border-radius: 10px; 
        border: 1px solid #d4af37; 
        border-left: 8px solid #d4af37;
        margin-bottom: 20px; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LÓGICA DE PROCESAMIENTO (ADN) ---
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

# --- 4. FUNCIÓN DEL SIMULADOR DE EXAMEN ---
def mostrar_simulador_mision():
    st.markdown("## ⚒️ Misión de Reparación: Lectura Crítica")
    st.write("Demuestra tu sabiduría para restaurar la integridad del Yelmo.")
    
    st.markdown("""
    <div class="pergamino">
        <h4>TEXTO DE APOYO (ICFES 2025)</h4>
        <p>"El 7 de agosto de 1819 se libró en el Puente de Boyacá una de las batallas de mayor importancia para la gesta libertadora. 
        Este espacio, más que una estructura física, se erige como un <b>patrimonio inmaterial</b> que permite la cohesión de la identidad nacional."</p>
        <hr>
        <b>PREGUNTA:</b> Según el texto, cuando el autor menciona que el Puente es un 'patrimonio inmaterial', se refiere a que:
    </div>
    """, unsafe_allow_html=True)
    
    respuesta = st.radio("Selecciona la opción correcta:", [
        "A. El puente ya no existe físicamente y solo vive en los libros.",
        "B. Su valor histórico y simbólico trasciende la construcción de piedra.",
        "C. Fue construido con materiales invisibles para la época.",
        "D. No tiene ninguna importancia para el departamento del Boyacá."
    ])
    
    if st.button("ENTREGAR RESPUESTA"):
        if "B." in respuesta:
            st.success("✨ ¡FORJA EXITOSA! Has reparado la pieza con éxito.")
            if st.button("VOLVER AL DASHBOARD"):
                st.session_state['view'] = 'dashboard'
                st.rerun()
        else:
            st.error("❌ RESPUESTA INCORRECTA. Tu Yelmo sigue agrietado. Analiza mejor el concepto de 'Simbólico'.")

# --- 5. LÓGICA DE NAVEGACIÓN ---
if st.session_state['view'] == 'mision':
    mostrar_simulador_mision()
else:
    # --- INTERFAZ DASHBOARD ---
    st.title("🛡️ TITÁN ESTUDIANTE: El Despertar")
    st.markdown("---")

    archivo = st.file_uploader("Cargue el Excel de Notas para despertar al Titán", type=["xlsx"])

    if archivo:
        df_adn = procesar_adn(archivo)
        if df_adn is not None:
            promedio_gral = df_adn['Puntaje'].mean()
            
            # --- LÓGICA DE AVATAR ---
            if promedio_gral >= 4.5: rango, color_rango = "TITÁN LEGENDARIO", "#d4af37" # Dorado Oscuro
            elif promedio_gral >= 3.8: rango, color_rango = "GUERRERO VETERANO", "#7f8c8d" # Gris Plata
            else: rango, color_rango = "RECLUTA EN FORJA", "#a0522d" # Bronce

            img_url = "https://www.freepik.com/premium-psd/ornate-medieval-armor-knights-cuirass_412654456.htm"

            with st.sidebar:
                st.markdown(f"<h1 style='text-align: center; color: {color_rango};'>{rango}</h1>", unsafe_allow_html=True)
                st.image(img_url, use_column_width=True)
                st.metric("PODER TOTAL", round(promedio_gral, 2))
                st.divider()
                st.write("📍 **Clan:** Grado 10-A")

            col1, col2 = st.columns([1, 1])

            with col1:
                st.subheader("⚔️ Inventario de Armadura")
                for _, row in df_adn.iterrows():
                    if row['Estado'] == "Bronce":
                        # Texto oscuro con alerta roja
                        st.markdown(f"<span style='color: #2b2d33;'>**{row['Pieza']}** ({row['Área']}): **{row['Puntaje']}**</span> | <span class='alerta-daño'>¡PIEZA DAÑADA!</span>", unsafe_allow_html=True)
                    else:
                        # Texto azul marino/oscuro para mayor legibilidad en blanco
                        st.markdown(f"<span style='color: #00262e;'>**{row['Pieza']}** ({row['Área']}): **{row['Puntaje']}** | Nivel {row['Estado']}</span>", unsafe_allow_html=True)
                    st.progress(row['Salud'] / 100)
                
                st.divider()
                # Gráfico Radar
                fig = px.line_polar(df_adn, r='Puntaje', theta='Área', line_close=True, range_r=[0,5])
                fig.update_traces(fill='toself', line_color=color_rango)
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#2b2d33", polar=dict(bgcolor="white"))
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("🧠 Diagnóstico de la IA")
                piezas_vulnerables = df_adn[df_adn['Puntaje'] < 3.8]
                if not piezas_vulnerables.empty:
                    for _, row in piezas_vulnerables.iterrows():
                        st.error(f"⚠️ **Punto de Quiebre:** Tu {row['Pieza']} ({row['Área']}) está vulnerable.")
                    
                    st.markdown("---")
                    st.subheader("⚒️ Taller de Mentores")
                    mas_critica = piezas_vulnerables.loc[piezas_vulnerables['Puntaje'].idxmin()]
                    if st.button(f"🔥 Forjar Reparación: {mas_critica['Área']}"):
                        st.session_state['view'] = 'mision'
                        st.rerun()
                else:
                    st.success("✅ **Integridad Total:** La armadura resiste.")

                st.markdown("---")
                st.subheader("🏆 Gesta del Clan")
                st.write("**Meta Grupal:** Salida a Cine")
                st.progress(65)

    else:
        st.info("Esperando el ADN Académico...")
        st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1144/1144760.png", width=200)