import streamlit as st
import sqlite3
import pandas as pd

# Conectar a la base de datos
def conectar_db():
    return sqlite3.connect('gimnasio.db')

# Función para agregar un nuevo usuario
def agregar_usuario(nombre, email, monitor):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Usuarios (nombre, email, monitor)
        VALUES (?, ?, ?)
    ''', (nombre, email, monitor))
    conn.commit()
    conn.close()

# Función para agregar una nueva actividad
def agregar_actividad(nombre, monitor_id, fecha, hora):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Actividades (nombre, monitor_id, fecha, hora)
        VALUES (?, ?, ?, ?)
    ''', (nombre, monitor_id, fecha, hora))
    conn.commit()
    conn.close()

# Función para obtener la lista de usuarios
def obtener_usuarios():
    conn = conectar_db()
    df = pd.read_sql_query("SELECT * FROM Usuarios", conn)
    conn.close()
    return df

# Función para obtener la lista de actividades
def obtener_actividades():
    conn = conectar_db()
    df = pd.read_sql_query("SELECT * FROM Actividades", conn)
    conn.close()
    return df

# Interfaz de la aplicación
st.title("Gestión de Gimnasio")

# Menú lateral
menu = st.sidebar.selectbox("Menú", ["Usuarios", "[<img alt="GitHub Workflow" src="https://img.shields.io/github/actions/workflow/status/propensive/sirkle/main.yml?style=for-the-badge" height="24">](https://github.com/propensive/sirkle/actions)
[<img src="https://img.shields.io/d
