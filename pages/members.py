import streamlit as st
import pandas as pd
from database import get_all_users, create_user
from utils import check_monitor_access
import bcrypt

def show():
    # Verificar acceso de monitor
    check_monitor_access()

    st.title("👥 Gestión de Miembros")

    tab1, tab2 = st.tabs(["Lista de Miembros", "Añadir Miembro"])

    with tab1:
        # Obtener lista de usuarios
        users = get_all_users()
        if not users.empty:
            # Añadir columna de tipo de usuario
            users['tipo'] = users['is_monitor'].apply(lambda x: "Monitor" if x else "Miembro")
            # Mostrar tabla de usuarios
            st.dataframe(
                users[['username', 'email', 'full_name', 'tipo', 'join_date']],
                column_config={
                    'username': 'Usuario',
                    'email': 'Email',
                    'full_name': 'Nombre completo',
                    'tipo': 'Tipo',
                    'join_date': 'Fecha de registro'
                },
                hide_index=True
            )
        else:
            st.info("No hay usuarios registrados")

    with tab2:
        st.subheader("Añadir nuevo miembro")
        with st.form("add_member_form"):
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            email = st.text_input("Email")
            full_name = st.text_input("Nombre completo")
            is_monitor = st.checkbox("¿Es monitor?")
            submitted = st.form_submit_button("Añadir miembro")
            if submitted:
                if not username or not password or not email or not full_name:
                    st.error("Por favor, completa todos los campos")
                elif len(password) < 6:
                    st.error("La contraseña debe tener al menos 6 caracteres")
                else:
                    success = create_user(username, password, email, full_name, is_monitor)
                    if success:
                        st.success(f"Usuario {username} creado correctamente")
                        st.experimental_rerun()
                    else:
                        st.error("El nombre de usuario o email ya está en uso")
