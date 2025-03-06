import streamlit as st
from streamlit_slickgrid import st_slickgrid
from supabase import create_client, Client
import pandas as pd
from config import SUPABASE_URL, SUPABASE_KEY

def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_user_activities(supabase: Client) -> pd.DataFrame:
    query = """
    SELECT 
        u.first_name || ' ' || u.last_name1 || ' ' || u.last_name2 AS usuario,
        a.name AS actividad,
        a.date AS fecha,
        a.start_time AS inicio,
        a.end_time AS fin,
        ap.attendance_status AS estado_asistencia
    FROM 
        public.activity_participants ap
    JOIN 
        public.users u ON ap.user_id = u.id
    JOIN 
        public.activities a ON ap.activity_id = a.id
    """
    response = supabase.rpc('execute_sql', {'sql': query}).execute()
    data = response.data
    return pd.DataFrame(data)

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
