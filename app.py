import streamlit as st
import time
import json
import os
from datetime import timedelta

# --- PERSISTENCIA ---
DB_FILE = "poker_pro_config.json"

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f)

def load_db():
    if os.path.exists(DB_FILE):
        return json.load(f) if (f := open(DB_FILE, 'r')) else None
    return None

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="POKER CLOCK PRO", layout="wide", initial_sidebar_state="collapsed")

# --- ESTILOS CSS PARA PROYECCIÓN ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    .main { background-color: #0E1117; }
    .stApp { background-color: #0E1117; }
    
    .big-timer {
        font-family: 'Orbitron', sans-serif;
        font-size: 180px !important;
        font-weight: 700;
        color: #00FF41;
        text-align: center;
        text-shadow: 0 0 20px rgba(0, 255, 65, 0.5);
        line-height: 1;
        margin: 20px 0;
    }
    .blind-label { font-size: 30px; color: #888; text-transform: uppercase; margin-bottom: -10px; }
    .blind-value { font-size: 70px; font-weight: bold; color: white; }
    .next-lvl { color: #FFA500; font-size: 20px; border-top: 1px solid #333; padding-top: 10px; }
    .prizepool-card {
        background: linear-gradient(135deg, #1e1e1e 0%, #111 100%);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #333;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN DE ESTADO ---
if 'data' not in st.session_state:
    db = load_db()
    st.session_state.data = db if db else {
        "levels": [{"m": 15, "sb": 100, "bb": 200, "a": 0}],
        "players": [],
        "buyin": 50,
        "curr_idx": 0
    }

if 'running' not in st.session_state: st.session_state.running = False
if 'time_left' not in st.session_state: 
    st.session_state.time_left = st.session_state.data["levels"][0]["m"] * 60

# --- LÓGICA DE NAVEGACIÓN ---
menu = st.sidebar.radio("Navegación", ["📺 Pantalla Principal", "🛠️ Configuración", "👥 Jugadores y Premios"])

# --- SECCIÓN 1: PANTALLA PRINCIPAL (LA QUE SE PROYECTA) ---
if menu == "📺 Pantalla Principal":
    idx = st.session_state.data["curr_idx"]
    lvl = st.session_state.data["levels"][idx]
    
    # Fila Superior: Info de Ciegas
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<p class="blind-label">Ciega Chica</p><p class="blind-value">{lvl["sb"]}</p>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<p class="blind-label" style="text-align:center">Ciega Grande</p><p class="blind-value" style="text-align:center">{lvl["bb"]}</p>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<p class="blind-label" style="text-align:right">Ante</p><p class="blind-value" style="text-align:right">{lvl["a"]}</p>', unsafe_allow_html=True)

    # Reloj Central
    timer_place = st.empty()
    
    # Fila Inferior: Siguiente Nivel y Stats
    st.markdown("<br>", unsafe_allow_html=True)
    inf1, inf2, inf3 = st.columns(3)
    
    with inf1:
        total_p = len(st.session_state.data["players"])
        st.subheader(f"👥 Jugadores: {total_p}")
    
    with inf2:
        if st.button("▶️/⏸️", use_container_width=True):
            st.session_state.running = not st.session_state.running
            st.rerun()

    with inf3:
        if idx + 1 < len(st.session_state.data["levels"]):
            nxt = st.session_state.data["levels"][idx+1]
            st.markdown(f'<p class="next-lvl">PRÓXIMO: {nxt["sb"]}/{nxt["bb"]} (Ante {nxt["a"]})</p>', unsafe_allow_html=True)

    # Bucle del Timer
    while st.session_state.running and st.session_state.time_left > 0:
        st.session_state.time_left -= 1
        m, s = divmod(st.session_state.time_left, 60)
        timer_place.markdown(f'<p class="big-timer">{m:02d}:{s:02d}</p>', unsafe_allow_html=True)
        time.sleep(1)
        if st.session_state.time_left <= 0:
            st.session_state.running = False
            st.rerun()

    if not st.session_state.running:
        m, s = divmod(st.session_state.time_left, 60)
        color = "#666" if st.session_state.time_left > 0 else "#FF4B4B"
        timer_place.markdown(f'<p class="big-timer" style="color: {color}">{m:02d}:{s:02d}</p>', unsafe_allow_html=True)

# --- SECCIÓN 2: CONFIGURACIÓN ---
elif menu == "🛠️ Configuración":
    st.header("🛠️ Estructura del Torneo")
    
    if st.button("💾 Guardar Configuración"):
        save_db(st.session_state.data)
        st.success("¡Configuración guardada!")

    # Editar Niveles
    new_levels = []
    for i, l in enumerate(st.session_state.data["levels"]):
        with st.expander(f"Nivel {i+1}", expanded=True):
            col = st.columns(4)
            m = col[0].number_input("Minutos", value=l["m"], key=f"m{i}")
            sb = col[1].number_input("SB", value=l["sb"], key=f"sb{i}")
            bb = col[2].number_input("BB", value=l["bb"], key=f"bb{i}")
            a = col[3].number_input("Ante", value=l["a"], key=f"a{i}")
            new_levels.append({"m": m, "sb": sb, "bb": bb, "a": a})
    st.session_state.data["levels"] = new_levels

    if st.button("➕ Añadir"):
        st.session_state.data["levels"].append({"m": 15, "sb": 0, "bb": 0, "a": 0})
        st.rerun()

    st.divider()
    if st.button("⏭️ Saltar al Siguiente Nivel"):
        if st.session_state.data["curr_idx"] < len(st.session_state.data["levels"]) - 1:
            st.session_state.data["curr_idx"] += 1
            idx = st.session_state.data["curr_idx"]
            st.session_state.time_left = st.session_state.data["levels"][idx]["m"] * 60
            st.rerun()

# --- SECCIÓN 3: JUGADORES Y PREMIOS ---
else:
    st.header("👥 Gestión de Mesa")
    
    col_j, col_p = st.columns(2)
    
    with col_j:
        st.subheader("Lista de Inscritos")
        raw_names = st.text_area("Pega nombres (uno por línea)", 
                                value="\n".join(st.session_state.data["players"]), height=200)
        if st.button("Actualizar Lista"):
            st.session_state.data["players"] = [n.strip() for n in raw_names.split("\n") if n.strip()]
            st.rerun()

    with col_p:
        st.subheader("💰 Prizepool")
        buyin = st.number_input("Buy-in ($)", value=st.session_state.data["buyin"])
        st.session_state.data["buyin"] = buyin
        
        total_pot = len(st.session_state.data["players"]) * buyin
        st.markdown(f"""
            <div class="prizepool-card">
                <h3>Total: ${total_pot}</h3>
                <p>🥇 1º (50%): ${total_pot * 0.5:,.0f}</p>
                <p>🥈 2º (30%): ${total_pot * 0.3:,.0f}</p>
                <p>🥉 3º (20%): ${total_pot * 0.2:,.0f}</p>
            </div>
        """, unsafe_allow_html=True)