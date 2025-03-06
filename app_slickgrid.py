import streamlit as st
import pandas as pd

# Datos de ejemplo
data = [
    {"ID": 1, "Nombre": "Ana", "Edad": 25, "Ciudad": "Madrid"},
    {"ID": 2, "Nombre": "Luis", "Edad": 30, "Ciudad": "Barcelona"},
    {"ID": 3, "Nombre": "Marta", "Edad": 28, "Ciudad": "Valencia"},
    {"ID": 4, "Nombre": "Pedro", "Edad": 35, "Ciudad": "Sevilla"},
]

df = pd.DataFrame(data)

# Título
st.title("Ejemplo de Streamlit con Edición de Datos")

# Muestra la tabla editable usando st.data_editor
edited_data = st.data_editor(df, num_rows="dynamic")

# Mostrar datos actualizados después de la edición
st.subheader("Datos actualizados")
st.dataframe(edited_data)
