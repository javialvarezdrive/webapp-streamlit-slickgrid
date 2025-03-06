import streamlit as st
import pandas as pd
import sqlite3
import altair as alt

DB_FILE = "database.db"

# Función para conectar a la base de datos
def get_connection():
    conn = sqlite3.connect(DB_FILE)
    return conn

# Función para crear la tabla si no existe
def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS personas (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Nombre TEXT,
            Edad INTEGER,
            Ciudad TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Función para carga
