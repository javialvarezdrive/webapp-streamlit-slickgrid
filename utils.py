import streamlit as st
from datetime import datetime, timedelta

# Mapeo de días de la semana
days_map = {
    0: "Lunes",
    1: "Martes",
    2: "Miércoles",
    3: "Jueves",
    4: "Viernes",
    5: "Sábado",
    6: "Domingo"
}

def format_time(time_str):
    """Formatea una hora en formato HH:MM a un formato más amigable."""
    try:
        hour, minute = time_str.split(':')
        return f"{int(hour):02d}:{int(minute):02d}"
    except:
        return time_str

def get_current_week_dates():
    """Retorna las fechas de la semana actual."""
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    dates = [(start_of_week + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
    return dates

def get_user_id(username):
    """Obtiene el ID de usuario desde la base de datos."""
    from database import get_user
    user = get_user(username)
    if user:
        return user['id']
    return None

def check_monitor_access():
    """Verifica si el usuario actual tiene acceso de monitor."""
    if not st.session_state.is_monitor:
        st.error("No tienes permiso para acceder a esta página")
        st.stop()
