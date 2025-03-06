import streamlit as st
import pandas as pd
from database import get_user, get_schedules, get_user_bookings
from utils import days_map, format_time, get_user_id

def show():
    st.title("🏠 Inicio")

    # Obtener ID de usuario
    user_id = get_user_id(st.session_state.username)

    # Mostrar tarjetas informativas
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Mis actividades hoy")
        # Obtener día de la semana actual (0 = lunes, 6 = domingo)
        current_day = pd.Timestamp.now().weekday()
        # Obtener reservas del usuario
        user_bookings = get_user_bookings(user_id)
        # Filtrar horarios para hoy
        schedules = get_schedules()
        today_schedules = schedules[schedules['day_of_week'] == current_day]

        if not today_schedules.empty:
            booked_today = user_bookings[
                user_bookings['schedule_id'].isin(today_schedules['id'])
            ]
            if not booked_today.empty:
                for _, booking in booked_today.iterrows():
                    with st.container():
                        st.markdown(f"""
                        **{booking['activity_name']}**
                        🕒 {format_time(booking['start_time'])}
                        👤 Monitor: {booking['monitor_name']}
                        """)
                        st.write("---")
            else:
                st.info("No tienes actividades programadas para hoy")
        else:
            st.info("No hay actividades disponibles hoy")

    with col2:
        st.subheader("Próximas actividades")
        # Obtener reservas futuras
        user_bookings = get_user_bookings(user_id)
        # Filtrar para días futuros
        future_days = [(current_day + i) % 7 for i in range(1, 7)]
        schedules = get_schedules()
        future_schedules = schedules[schedules['day_of_week'].isin(future_days)]

        if not future_schedules.empty:
            booked_future = user_bookings[
                user_bookings['schedule_id'].isin(future_schedules['id'])
            ]
            if not booked_future.empty:
                # Mostrar las 3 próximas actividades
                for _, booking in booked_future.head(3).iterrows():
                    with st.container():
                        st.markdown(f"""
                        **{booking['activity_name']}**
                        📅 {booking['day']}
                        🕒 {format_time(booking['start_time'])}
                        """)
                        st.write("---")
            else:
                st.info("No tienes actividades futuras programadas")
        else:
            st.info("No hay actividades disponibles en los próximos días")

    # Mostrar actividades disponibles
    st.subheader("Actividades disponibles esta semana")
    schedules = get_schedules()
    if not schedules.empty:
        # Añadimos una columna con el espacio disponible
        schedules['available_spots'] = schedules['max_capacity'] - schedules['current_bookings']
        schedules['day_name'] = schedules['day_of_week'].map(days_map)

        # Filtrar para mostrar solo los que tienen espacio disponible
        available_schedules = schedules[schedules['available_spots'] > 0]
        if not available_schedules.empty:
            # Agrupamos por actividad
            for activity_name, activity_group in available_schedules.groupby('activity_name'):
                with st.expander(f"🔸 {activity_name}"):
                    for _, schedule in activity_group.iterrows():
                        st.markdown(f"""
                        **{days_map[schedule['day_of_week']]} - {format_time(schedule['start_time'])}**
                        👤 Monitor: {schedule['monitor_name']}
                        🔢 Plazas disponibles: {schedule['available_spots']} de {schedule['max_capacity']}
                        """)
                        st.write("---")
        else:
            st.info("No hay actividades con plazas disponibles esta semana")
    else:
        st.info("No hay actividades programadas esta semana")
