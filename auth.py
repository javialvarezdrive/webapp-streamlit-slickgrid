import streamlit as st
import bcrypt
from database import get_user, create_user

def check_password(username, password):
    user = get_user(username)
    if not user:
        return False, False
    stored_password = user['password'].encode()
    if bcrypt.checkpw(password.encode(), stored_password):
        return True, user['is_monitor']
    return False, False

def login():
    st.title("🏋️ Gestión de Gimnasio - Iniciar Sesión")
    with st.form("login_form"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Iniciar Sesión")
        if submitted:
            if not username or not password:
                st.error("Por favor, completa todos los campos")
            else:
                authenticated, is_monitor = check_password(username, password)
                if authenticated:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.is_monitor = is_monitor
                    st.success("¡Inicio de sesión exitoso!")
                    st.experimental_rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")

    st.write("---")
    st.write("¿No tienes una cuenta?")
    if st.button("Registrarse"):
        st.session_state.show_register = True

def register():
    st.title("🏋️ Gestión de Gimnasio - Registro")
    with st.form("register_form"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        confirm_password = st.text_input("Confirmar Contraseña", type="password")
        email = st.text_input("Email")
        full_name = st.text_input("Nombre Completo")
        submitted = st.form_submit_button("Registrarse")
        if submitted:
            if not username or not password or not confirm_password or not email or not full_name:
                st.error("Por favor, completa todos los campos")
            elif password != confirm_password:
                st.error("Las contraseñas no coinciden")
            elif len(password) < 6:
                st.error("La contraseña debe tener al menos 6 caracteres")
            else:
                success = create_user(username, password, email, full_name)
                if success:
                    st.success("Registro exitoso. Ahora puedes iniciar sesión.")
                    st.session_state.show_register = False
                    st.experimental_rerun()
                else:
                    st.error("El nombre de usuario o email ya está en uso")

    st.write("---")
    if st.button("Volver a Iniciar Sesión"):
        st.session_state.show_register = False
        st.experimental_rerun()

def check_auth():
    if not st.session_state.logged_in:
        if 'show_register' not in st.session_state:
            st.session_state.show_register = False
        if st.session_state.show_register:
            register()
        else:
            login()
        st.stop()
