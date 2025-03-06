import streamlit as st
import pandas as pd
import altair as alt

# Datos de ejemplo
data = [
    {"ID": 1, "Nombre": "Ana", "Edad": 25, "Ciudad": "Madrid"},
    {"ID": 2, "Nombre": "Luis", "Edad": 30, "Ciudad": "Barcelona"},
    {"ID": 3, "Nombre": "Marta", "Edad": 28, "Ciudad": "Valencia"},
    {"ID": 4, "Nombre": "Pedro", "Edad": 35, "Ciudad": "Sevilla"},
]

df = pd.DataFrame(data)

# Título
st.title("📊 Streamlit: Edición de Datos + Gráfico")

# Muestra la tabla editable
st.subheader("📝 Edita los datos:")
edited_data = st.data_editor(df, num_rows="dynamic")

# Mostrar datos actualizados
st.subheader("📌 Datos actualizados:")
st.dataframe(edited_data)

# Generar gráfico dinámico de edades
st.subheader("📈 Distribución de Edades")

if not edited_data.empty:
    chart = alt.Chart(edited_data).mark_bar().encode(
        x=alt.X("Nombre", sort=None),
        y="Edad",
        color="Ciudad"
    ).properties(width=600, height=400)

    st.altair_chart(chart, use_container_width=True)
