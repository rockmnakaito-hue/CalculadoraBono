# archivo: calculadora_bono.py
import streamlit as st
import requests
from datetime import datetime
import time

st.set_page_config(page_title="Calculadora de Bono", layout="centered")

# -----------------------
# Configuración inicial
# -----------------------
META_BASE = 760_000
META_ALTA = 775_000
DIAS_MES = 31
API_URL = "https://nwb6jfmrkbburyc2o3fzstvngu0nxloq.lambda-url.us-east-1.on.aws"

# -----------------------
# Selección de meta
# -----------------------
st.title("💰 Calculadora de Bono")
meta_opcion = st.radio("Selecciona la meta:", ["Meta base", "Meta alta"])
total = META_BASE if meta_opcion == "Meta base" else META_ALTA
st.write(f"Meta total: **${total:,.0f}**")

# -----------------------
# Función para obtener monto actual
# -----------------------
def obtener_monto_actual():
    try:
        res = requests.get(API_URL, timeout=5)
        data = res.json()
        monto_str = data.get("Month to date", "$0")
        monto_num = float(monto_str.replace("$","").replace(",",""))
        return monto_num
    except Exception as e:
        st.warning(f"No se pudo obtener monto actualizado, usando valor por defecto. Error: {e}")
        return 363_775.4  # fallback

# -----------------------
# Barra de progreso y comparativa
# -----------------------
def actualizar_barra():
    monto_actual = obtener_monto_actual()
    porcentaje = min((monto_actual / total) * 100, 100)
    
    # Barra de progreso
    st.progress(porcentaje / 100)
    
    # Mostrar monto actual encima de la barra
    st.markdown(f"### Monto actual: **${monto_actual:,.2f}**")
    
    # Diferencia con el esperado
    hoy = datetime.now().day
    meta_diaria = total / DIAS_MES
    esperado = meta_diaria * hoy
    diferencia = monto_actual - esperado

    if diferencia >= 0:
        st.markdown(f"<span style='color:#00e676;'>Llevas +${abs(diferencia):,.0f} por encima</span>", unsafe_allow_html=True)
    else:
        st.markdown(f"<span style='color:#ff4c4c;'>Te faltan -${abs(diferencia):,.0f}</span>", unsafe_allow_html=True)

    # Comparativa de días
    dia_calculado = monto_actual / meta_diaria
    dias_ventaja = int(dia_calculado) - hoy
    if dias_ventaja > 2:
        emoji = "🔥"
    elif dias_ventaja > 0:
        emoji = "🚀"
    elif dias_ventaja == 0:
        emoji = "⏱️"
    else:
        emoji = "🐢"

    if dias_ventaja > 0:
        st.markdown(f"📅 Hoy es el día {hoy} — {emoji} Vas {dias_ventaja} día(s) adelantado.")
    elif dias_ventaja < 0:
        st.markdown(f"📅 Hoy es el día {hoy} — {emoji} Vas {abs(dias_ventaja)} día(s) atrasado.")
    else:
        st.markdown(f"📅 Hoy es el día {hoy} — {emoji} Estás justo al día.")

# -----------------------
# Ejecutar actualización
# -----------------------
actualizar_barra()

# -----------------------
# Auto-refresh cada 2 minutos
# -----------------------
st.experimental_rerun()  # Streamlit recarga la página para refrescar
