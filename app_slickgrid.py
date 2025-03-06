import streamlit as st
from streamlit_slickgrid import st_slickgrid
from supabase import create_client, Client
import pandas as pd
from config import SUPABASE_URL, SUPABASE_KEY, TABLE_NAME

def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_data_from_supabase(supabase: Client, table_name: str) -> pd.DataFrame:
    response = supabase.table(table_name).select("*").execute()
    data = response.data
    return pd.DataFrame(data)

def main():
    st.title("Streamlit SlickGrid with Supabase")

    # Inicializa el cliente de Supabase
    supabase = init_supabase()

    # Obtén los datos de Supabase
    df = fetch_data_from_supabase(supabase, TABLE_NAME)

    # Muestra los datos usando SlickGrid
    st_slickgrid(df)

if __name__ == "__main__":
    main()
