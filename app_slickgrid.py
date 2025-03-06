import streamlit as st
from streamlit_slickgrid import st_slickgrid
from supabase import create_client, Client
import pandas as pd
from config import SUPABASE_URL, SUPABASE_KEY

def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_user_activities(supabase: Client) -> pd.DataFrame:
    # Obtener datos de participantes
    participants_response = supabase.from_('activity_participants').select(
        'user_id, activity_id, attendance_status'
    ).execute()

    participants_data = participants_response.data

    # Obtener datos de usuarios
    users_response = supabase.from_('users').select('id, first_name, last_name1, last_name2').execute()
    users_data = users_response.data

    # Obtener datos de actividades
    activities_response = supabase.from_('activities').select('id, name, date, start_time, end_time').execute()
    activities_data = activities_response.data

    # Convertir a DataFrames
    participants_df = pd.DataFrame(participants_data)
    users_df = pd.DataFrame(users_data)
    activities_df = pd.DataFrame(activities_data)

    # Unir los DataFrames
    merged_df = participants_df.merge(users_df, left_on='user_id', right_on='id', suffixes=('', '_user'))
    merged_df = merged_df.merge(activities_df, left_on='activity_id', right_on='id', suffixes=('', '_activity'))

    # Seleccionar y renombrar columnas
    final_df = merged_df[['first_name', 'last_name1', 'last_name2', 'name', 'date', 'start_time', 'end_time', 'attendance_status']]
    final_df.columns = ['Nombre', 'Apellido1', 'Apellido2', 'Actividad', 'Fecha', 'Inicio', 'Fin', 'Estado Asistencia']

    return final_df

def main():
    st.title("Actividades por Usuario")

    # Inicializa el cliente de Supabase
    supabase = init_supabase()

    # Obtén las actividades por usuario
    df = fetch_user_activities(supabase)

    # Muestra los datos usando SlickGrid
    st_slickgrid(df)

if __name__ == "__main__":
    main()
