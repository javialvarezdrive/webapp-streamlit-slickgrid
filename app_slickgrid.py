import streamlit as st
import pandas as pd
import sqlite3
import altair as alt

DB_FILE = "database.db"

# Función para conectar a la base de datos
def get_connection():
    return sqlite3.connect(DB_FILE)

# Función para crear la tabla si no existe Y AÑADIR DATOS INICIALES
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

    # --- AÑADIR DATOS INICIALES AQUÍ ---
    # Comprobar si la tabla ya tiene datos (para no duplicar al reiniciar la app)
    cursor.execute("SELECT COUNT(*) FROM personas")
    count = cursor.fetchone()[0]
    if count == 0: # Si la tabla está vacía, insertar datos iniciales
        print("Insertando datos iniciales en la base de datos...") # Mensaje en la consola
        initial_data = [
            ('Ana', 30, 'Madrid'),
            ('Juan', 25, 'Barcelona'),
            ('Sofía', 35, 'Valencia'),
            ('Carlos', 28, 'Sevilla')
        ]
        cursor.executemany("INSERT INTO personas (Nombre, Edad, Ciudad) VALUES (?, ?, ?)", initial_data)
        conn.commit()
        print("Datos iniciales insertados.")
    else:
        print("La tabla 'personas' ya contiene datos, no se insertan datos iniciales.") # Mensaje si ya hay datos

    conn.close()

# Función para cargar datos desde la BD
def load_data():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM personas", conn)
    conn.close()
    return df

# Función para guardar datos en la BD
def save_data(df):
    conn = get_connection()
    df.to_sql("personas", conn, if_exists="replace", index=False)
    conn.close()

# Función para insertar un nuevo registro en la BD
def insert_data(nombre, edad, ciudad):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO personas (Nombre, Edad, Ciudad) VALUES (?, ?, ?)", (nombre, edad, ciudad))
    conn.commit()
    conn.close()

# Crear la tabla y añadir datos iniciales (si es necesario)
create_table()

# 📌 **Sección de la App**
st.title("📊 Streamlit + SQLite con Datos Iniciales") # Título actualizado
st.info("Cargando datos iniciales a la base de datos (solo la primera vez)...") # Mensaje informativo en la app

# 📥 **Formulario para agregar nuevos datos**
st.subheader("➕ Agregar nueva persona")
with st.form("insert_form"):
    nombre = st.text_input("Nombre")
    edad = st.number_input("Edad", min_value=1, max_value=100, step=1)
    ciudad = st.text_input("Ciudad")
    submitted = st.form_submit_button("Agregar")

    if submitted:
        if nombre and ciudad:
            insert_data(nombre, edad, ciudad)
            st.success(f"✅ {nombre} agregado a la base de datos")
            st.experimental_rerun()
        else:
            st.error("❌ Por favor, completa todos los campos")

# 📋 **Mostrar y editar datos**
st.subheader("📝 Editar Datos")
df = load_data()
edited_data = st.data_editor(df, num_rows="dynamic")

# Guardar cambios en la base de datos
if not edited_data.empty:
    save_data(edited_data)

# 📊 **Gráfico de Edades**
st.subheader("📈 Distribución de Edades")
if not edited_data.empty:
    chart = alt.Chart(edited_data).mark_bar().encode(
        x=alt.X("Nombre", sort=None),
        y="Edad",
        color="Ciudad"
    ).properties(width=600, height=400)

    st.altair_chart(chart, use_container_width=True)
