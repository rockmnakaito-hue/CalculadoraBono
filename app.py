# archivo: calculadora_bono_streamlit.py
import streamlit as st
import requests
from datetime import datetime
import time

# -----------------------
# Configuración de página
# -----------------------
st.set_page_config(page_title="Calculadora de Bono", layout="centered")
st.markdown("""
<style>
body {background-color: #121212; color:white; font-family: 'Segoe UI', sans-serif;}
h1 {color: #00e676;}
button {background-color:#333; color:white; border-radius:8px; padding:10px 15px; margin:5px; font-weight:bold;}
button:hover {background-color:#00e676; color:black;}
.progress-bar {height:25px; width:0%; background:#00e676; border-radius:12px; text-align:center; line-height:25px; font-weight:bold; color:black; transition:width 1s;}
.progress-container {width:80%; background:#333; border-radius:12px; margin:20px auto; height:25px; overflow:hidden; position:relative;}
.progress-text {margin-top:5px; font-size:18px;}
.estado {font-size:22px; margin-top:20px; font-weight:bold;}
</style>
""", unsafe_allow_html=True)

# -----------------------
# Variables
# -----------------------
META_BASE = 760_000
META_ALTA = 775_000
DIAS_MES = 31
API_URL = "https://nwb6jfmrkbburyc2o3fzstvngu0nxloq.lambda-url.us-east-1.on.aws"

# -----------------------
# Selector Meta
# -----------------------
st.title("💰 Calculadora de Bono")
meta_opcion = st.radio("Selecciona la meta:", ["Meta base", "Meta alta"])
total = META_BASE if meta_opcion == "Meta base" else META_ALTA
st.markdown(f"<p style='font-size:20px;'>Meta total: <strong>${total:,.0f}</strong></p>", unsafe_allow_html=True)

# -----------------------
# Barra de progreso
# -----------------------
barra_container = st.empty()
texto_container = st.empty()
estado_container = st.empty()

# -----------------------
# Obtener monto actual
# -----------------------
def obtener_monto_actual():
    try:
        res = requests.get(API_URL, timeout=5)
        data = res.json()
        monto_str = data.get("Month to date", "$0")
        monto_num = float(monto_str.replace("$","").replace(",",""))
        return monto_num
    except:
        return 363_775.4

# -----------------------
# Actualizar barra y comparativa
# -----------------------
def actualizar_progreso():
    monto_actual = obtener_monto_actual()
    porcentaje = min((monto_actual/total)*100,100)
    
    barra_container.markdown(f"""
    <div class="progress-container">
      <div class="progress-bar" style="width:{porcentaje}%">{porcentaje:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Monto encima de barra
    texto_container.markdown(f"<div class='progress-text'>Monto actual: <strong>${monto_actual:,.2f}</strong></div>", unsafe_allow_html=True)
    
    # Diferencia con esperado
    hoy = datetime.now().day
    meta_diaria = total / DIAS_MES
    esperado = meta_diaria * hoy
    diferencia = monto_actual - esperado

    if diferencia>=0:
        estado_text = f"<span style='color:#00e676;'>Llevas +${abs(diferencia):,.0f} por encima</span>"
    else:
        estado_text = f"<span style='color:#ff4c4c;'>Te faltan -${abs(diferencia):,.0f}</span>"

    # Comparativa días
    dia_calculado = monto_actual/meta_diaria
    dias_ventaja = int(dia_calculado) - hoy
    if dias_ventaja>2: emoji="🔥"
    elif dias_ventaja>0: emoji="🚀"
    elif dias_ventaja==0: emoji="⏱️"
    else: emoji="🐢"

    if dias_ventaja>0:
        mensaje = f"📅 Hoy es el día {hoy} — {emoji} Vas {dias_ventaja} día(s) adelantado."
    elif dias_ventaja<0:
        mensaje = f"📅 Hoy es el día {hoy} — {emoji} Vas {abs(dias_ventaja)} día(s) atrasado."
    else:
        mensaje = f"📅 Hoy es el día {hoy} — {emoji} Estás justo al día."

    estado_container.markdown(f"<div class='estado'>{estado_text}<br>{mensaje}</div>", unsafe_allow_html=True)

# -----------------------
# Ejecutar automáticamente
# -----------------------
actualizar_progreso()
st.markdown("<small>Se actualizará automáticamente cada 2 minutos.</small>", unsafe_allow_html=True)

# Auto-refresh cada 2 minutos
st_autorefresh = st.experimental_data_editor if hasattr(st, "experimental_data_editor") else None
if st_autorefresh:
    st_autorefresh(interval=120*1000)  # cada 120 segundos

