import streamlit as st
import time
import json
import os
import base64
from datetime import timedelta

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="POKER CLOCK ELITE", layout="wide", initial_sidebar_state="expanded")

# --- PERSISTENCIA DE DATOS ---
DB_FILE = "poker_data.json"

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f)

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                return json.load(f)
        except: return None
    return None

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');
    .stApp { background-color: #050505; }
    .main-timer {
        font-family: 'Orbitron', sans-serif;
        font-size: 160px !important;
        font-weight: 700;
        color: #00FF41;
        text-align: center;
        text-shadow: 0 0 30px rgba(0, 255, 65, 0.4);
        margin: -20px 0;
    }
    .blind-box {
        background: #111;
        border: 2px solid #333;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
    }
    .label { color: #888; font-size: 24px; font-weight: bold; text-transform: uppercase; }
    .value { color: white; font-size: 60px; font-weight: 900; }
    .next-info { color: #FFA500; font-size: 22px; text-align: center; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN DE ALARMA (ARCHIVO LOCAL) ---
def play_alarm():
    if os.path.exists("alarm.mp3"):
        with open("alarm.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            audio_html = f"""
                <audio autoplay="true">
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
            """
            st.components.v1.html(audio_html, height=0)
    else:
        st.error("Archivo alarm.mp3 no encontrado")

# --- INICIALIZACIÓN ---
if 'data' not in st.session_state:
    db = load_db()
    st.session_state.data = db if db else {
        "levels": [
            {"m": 15, "sb": 100, "bb": 200, "a": 0},
            {"m": 15, "sb": 200, "bb": 400, "a": 0},
            {"m": 15, "sb": 300, "bb": 600, "a": 100}
        ],
        "players": "Jugador 1\nJugador 2\nJugador 3",
        "buyin": 50,
        "curr_idx": 0
    }

if 'running' not in st.session_state: st.session_state.running = False
if 'time_left' not in st.session_state:
    idx = st.session_state.data["curr_idx"]
    st.session_state.time_left = st.session_state.data["levels"][idx]["m"] * 60

# --- SIDEBAR ---
with st.sidebar:
    st.title("♣️ CONTROL")
    mode = st.radio("Sección", ["Proyección", "Configuración"])
    st.divider()
    if st.button("▶️ / ⏸️ INICIAR-PAUSAR", use_container_width=True):
        st.session_state.running = not st.session_state.running
        st.rerun()
    
    if st.button("⏭️ SIGUIENTE NIVEL", use_container_width=True):
        if st.session_state.data["curr_idx"] < len(st.session_state.data["levels"]) - 1:
            st.session_state.data["curr_idx"] += 1
            idx = st.session_state.data["curr_idx"]
            st.session_state.time_left = st.session_state.data["levels"][idx]["m"] * 60
            st.rerun()

# --- VISTA: CONFIGURACIÓN ---
if mode == "Configuración":
    st.header("⚙️ Configuración")
    col_l, col_p = st.columns([2, 1])
    with col_l:
        updated_levels = []
        for i, lvl in enumerate(st.session_state.data["levels"]):
            with st.expander(f"Nivel {i+1}", expanded=True):
                c1, c2, c3, c4 = st.columns(4)
                m = c1.number_input("Minutos", value=lvl["m"], key=f"m{i}")
                s = c2.number_input("SB", value=lvl["sb"], key=f"s{i}")
                b = c3.number_input("BB", value=lvl["bb"], key=f"b{i}")
                a = c4.number_input("Ante", value=lvl["a"], key=f"a{i}")
                updated_levels.append({"m": m, "sb": s, "bb": b, "a": a})
        if st.button("➕ Añadir Nivel"):
            st.session_state.data["levels"].append({"m": 15, "sb": 0, "bb": 0, "a": 0})
            st.rerun()
    with col_p:
        buyin = st.number_input("Buy-in ($)", value=st.session_state.data["buyin"])
        p_list = st.text_area("Lista", value=st.session_state.data["players"], height=250)
    
    if st.button("💾 GUARDAR TODO"):
        st.session_state.data["levels"] = updated_levels
        st.session_state.data["players"] = p_list
        st.session_state.data["buyin"] = buyin
        save_db(st.session_state.data)
        st.success("Guardado.")

# --- VISTA: PROYECCIÓN ---
else:
    idx = st.session_state.data["curr_idx"]
    curr = st.session_state.data["levels"][idx]
    
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="blind-box"><p class="label">Ciega Chica</p><p class="value">{curr["sb"]}</p></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="blind-box"><p class="label">Ciega Grande</p><p class="value">{curr["bb"]}</p></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="blind-box"><p class="label">Ante</p><p class="value">{curr["a"]}</p></div>', unsafe_allow_html=True)

    timer_placeholder = st.empty()
    
    st.divider()
    inf1, inf2, inf3 = st.columns(3)
    inf1.metric("JUGADORES", len([j for j in st.session_state.data["players"].split("\n") if j.strip()]))
    inf2.metric("NIVEL", f"{idx + 1}")
    if idx + 1 < len(st.session_state.data["levels"]):
        nxt = st.session_state.data["levels"][idx+1]
        inf3.markdown(f'<p class="next-info">PRÓXIMO: {nxt["sb"]}/{nxt["bb"]}</p>', unsafe_allow_html=True)

    # --- LÓGICA DE TIEMPO Y AUTO-NIVEL ---
    if st.session_state.running:
        while st.session_state.time_left >= 0:
            m, s = divmod(st.session_state.time_left, 60)
            timer_placeholder.markdown(f'<p class="main-timer">{m:02d}:{s:02d}</p>', unsafe_allow_html=True)
            
            if st.session_state.time_left == 0:
                play_alarm()
                time.sleep(1) # Dejar que suene antes de cambiar
                
                # Pasar al siguiente nivel automáticamente
                if idx + 1 < len(st.session_state.data["levels"]):
                    st.session_state.data["curr_idx"] += 1
                    new_idx = st.session_state.data["curr_idx"]
                    st.session_state.time_left = st.session_state.data["levels"][new_idx]["m"] * 60
                    st.rerun()
                else:
                    st.session_state.running = False
                    st.balloons()
                    st.rerun()
            
            time.sleep(1)
            st.session_state.time_left -= 1

    # Estado pausado
    m, s = divmod(st.session_state.time_left, 60)
    timer_placeholder.markdown(f'<p class="main-timer" style="color: #666;">{m:02d}:{s:02d}</p>', unsafe_allow_html=True)