import streamlit as st
from streamlit_slickgrid import st_slickgrid
import pandas as pd
import random

st.title("Streamlit SlickGrid Demo (Sencillo) - Corregido") # Title updated to indicate it's the corrected version
st.write("Esta es una aplicación Streamlit sencilla que muestra datos usando `streamlit-slickgrid`.")

# 1. Generar datos inventados
num_filas = 20
categorias = ["Electrónicos", "Ropa", "Hogar", "Libros", "Deportes"]
productos = [
    "Laptop", "Smartphone", "Camiseta", "Pantalones", "Mesa", "Silla", "Novela", "Poesía", "Balón", "Raqueta"
]

data = []
for i in range(1, num_filas + 1):
    categoria = random.choice(categorias)
    producto_base = random.choice(productos)
    nombre_producto = f"{categoria} {producto_base} {i}" # Nombre un poco más descriptivo
    precio = round(random.uniform(10, 500), 2)
    stock = random.randint(0, 100)

    data.append({
        "ID": i,
        "Nombre del Producto": nombre_producto,
        "Categoría": categoria,
        "Precio": precio,
        "Stock": stock,
        "Fecha de Creación": pd.to_datetime('today') - pd.to_timedelta(random.randint(1, 30), unit='D') # Fechas aleatorias
    })

df = pd.DataFrame(data)

st.subheader("Tabla de Productos (Interactiva con SlickGrid)")
st.write("Puedes interactuar con esta tabla: ordenar columnas, redimensionar, etc.")

# 2. Mostrar la tabla con st_slickgrid (configuración básica)
grid_options = {
    "enableCellNavigation": True,
    "enableColumnReorder": True,
    "fullWidthRows": True,
    "syncColumnCellResize": True,
    "forceFitColumns": False, # Para permitir el scroll horizontal si las columnas no caben
    "defaultColumnWidth": 120,
    "rowHeight": 35,
}

grid_response = st_slickgrid(
    df,
    grid_options=grid_options,
    height=350, # Altura fija para la tabla
)

# Opcional: Mostrar información de la interacción (por ejemplo, datos seleccionados)
if grid_response['selected_rows']:
    st.subheader("Filas Seleccionadas:")
    selected_df = pd.DataFrame(grid_response['selected_rows'])
    st.dataframe(selected_df)

st.info("Esta es una demo básica. `streamlit-slickgrid` tiene muchas más opciones de configuración y personalización.")
