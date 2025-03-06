import streamlit as st
import pandas as pd
from streamlit_slickgrid import st_slickgrid

# Datos de ejemplo
data = [
    {"ID": 1, "Nombre": "Ana", "Edad": 25, "Ciudad": "Madrid"},
    {"ID": 2, "Nombre": "Luis", "Edad": 30, "Ciudad": "Barcelona"},
    {"ID": 3, "Nombre": "Marta", "Edad": 28, "Ciudad": "Valencia"},
    {"ID": 4, "Nombre": "Pedro", "Edad": 35, "Ciudad": "Sevilla"},
]

df = pd.DataFrame(data)

# Título
st.title("Ejemplo de Streamlit con SlickGrid")

# Muestra la tabla interactiva
edited_data = st_slickgrid(df, key="slickgrid")

# Mostrar datos actualizados después de la edición
if edited_data is not None:
    st.subheader("Datos actualizados")
    st.dataframe(edited_data)
