import streamlit as st
import pandas as pd
from database import get_user, update_user, change_password, get_user_bookings
from utils import get_user_id

def show():
    st.title("👤 Perfil de Usuario")

    # Obtener información del usuario
    user = get_user(st.session_state.username)
    if user:
        col1, col2 = st.columns([1, 2])
        with col1:
            # Mostrar información del usuario
            st.markdown("### Información Personal")
            st.markdown(f"**Usuario:** {user['username']}")
            st.markdown(f"**Nombre:** {user['full_name']}")
            st.markdown(f"**Email:** {user['email']}")
            st.markdown(f"**Tipo de usuario:** {'Monitor' if user['is_monitor'] else 'Miembro'}")

        with col2:
            # Formulario para actualizar perfil
            st.markdown("### Actualizar Perfil")
            with st.form("update_profile"):
                new_email = st.text_input("Email", user['email'])
                new_full_name = st.text_input("Nombre completo", user['full_name'])
                submitted = st.form_submit_button("Actualizar perfil")
                if submitted:
                    update_user(user['id'], new_email, new_full_name)
                    st.success("Perfil actualizado correctamente")
                    st.experimental_rerun()

        # Cambiar contraseña
        st.markdown("---")
        st.markdown("### Cambiar Contraseña")
        with st.form("change_password"):
            current_password = st.text_input("Contraseña actual", type="password")
            new_password = st.text_input("Nueva contraseña", type="password")
            confirm_password = st.text_input("Confirmar nueva contraseña", type="password")
            submitted = st.form_submit_button("Cambiar contraseña")
            if submitted:
                if not current_password or not new_password or not confirm_password:
                    st.error("Por favor, completa todos los campos")
                elif new_password != confirm_password:
                    st.error("Las contraseñas no coinciden")
                elif len(new_password) < 6:
                    st.error("La contraseña debe tener al menos 6 caracteres")
                else:
                    import bcrypt
                    if bcrypt.checkpw(current_password.encode(), user['password'].encode()):
                        change_password(user['id'], new_password)
                        st.success("Contraseña actualizada correctamente")
                    else:
                        st.error("La contraseña actual es incorrecta")

        # Historial de reservas
        st.markdown("---")
        st.markdown("### Historial de Reservas")
        user_id = get_user_id(st.session_state.username)
        bookings = get_user_bookings(user_id)
        if not bookings.empty:
            # Crear una tabla más amigable para mostrar
            bookings_display = bookings[['activity_name', 'day', 'start_time', 'monitor_name', 'booking_date']]
            bookings_display.columns = ['Actividad', 'Día', 'Hora', 'Monitor', 'Fecha de reserva']
            st.dataframe(bookings_display)
        else:
            st.info("No tienes reservas registradas")
