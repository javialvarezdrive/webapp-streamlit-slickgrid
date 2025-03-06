import streamlit as st
import pandas as pd
from database import (
    get_schedules, create_schedule, update_schedule, delete_schedule,
    get_activities, get_monitors
)
from utils import days_map, format_time, check_monitor_access

def show():
    st.title("🗓️ Horario de Actividades")

    # Obtener horarios
    schedules = get_schedules()

    # Crear pestañas
    tab1, tab2 = st.tabs(["Ver Horario", "Gestionar Horario"])

    with tab1:
        # Mostrar horarios en formato calendario
        if not schedules.empty:
            # Crear un DataFrame para el calendario
            calendar_df = pd.DataFrame(index=range(7, 22), columns=range(7))

            # Llenar el calendario con actividades
            for _, schedule in schedules.iterrows():
                day = schedule['day_of_week']
                hour = int(schedule['start_time'].split(':')[0])
                # Si ya hay una actividad a esa hora, añadir un salto de línea
                if not pd.isna(calendar_df.loc[hour, day]):
                    calendar_df.loc[hour, day] += f"\n{schedule['activity_name']}"
                else:
                    calendar_df.loc[hour, day] = schedule['activity_name']

            # Renombrar columnas y filas
            calendar_df.columns = [days_map[i] for i in range(7)]
            calendar_df.index = [f"{i}:00" for i in range(7, 22)]

            # Mostrar calendario
            st.dataframe(
                calendar_df,
                height=600
            )
        else:
            st.info("No hay horarios programados")

    with tab2:
        # Verificar si el usuario es monitor
        if not st.session_state.is_monitor:
            st.warning("Solo los monitores pueden gestionar los horarios")
        else:
            # Agregar nuevo horario
            st.subheader("Agregar/Editar Horario")

            # Obtener actividades y monitores
            activities = get_activities()
            monitors = get_monitors()

            if activities.empty:
                st.warning("No hay actividades disponibles. Por favor, crea algunas primero.")
            elif monitors.empty:
                st.warning("No hay monitores disponibles.")
            else:
                # Formulario para agregar/editar horario
                with st.form("schedule_form"):
                    # Si estamos editando, cargar datos existentes
                    editing_id = st.session_state.get('editing_schedule_id', None)
                    if editing_id:
                        schedule_data = schedules[schedules['id'] == editing_id].iloc[0]
                        st.subheader("Editar Horario")
                    else:
                        schedule_data = None
                        st.subheader("Nuevo Horario")

                    # Campos del formulario
                    activity_options = {row['name']: row['id'] for _, row in activities.iterrows()}
                    selected_activity = st.selectbox(
                        "Actividad",
                        options=list(activity_options.keys()),
                        index=list(activity_options.keys()).index(schedule_data['activity_name']) if schedule_data is not None else 0
                    )
                    day_options = {v: k for k, v in days_map.items()}
                    selected_day = st.selectbox(
                        "Día de la semana",
                        options=list(day_options.keys()),
                        index=schedule_data['day_of_week'] if schedule_data is not None else 0
                    )
                    hour = st.number_input(
                        "Hora (0-23)", min_value=7, max_value=21,
                        value=int(schedule_data['start_time'].split(':')[0]) if schedule_data is not None else 8
                    )
                    minute = st.selectbox(
                        "Minutos",
                        options=[0, 15, 30, 45],
                        index=["0", "15", "30", "45"].index(schedule_data['start_time'].split(':')[1]) if schedule_data is not None else 0
                    )
                    monitor_options = {row['username']: row['id'] for _, row in monitors.iterrows()}
                    selected_monitor = st.selectbox(
                        "Monitor",
                        options=list(monitor_options.keys()),
                        index=list(monitor_options.keys()).index(schedule_data['monitor_name']) if schedule_data is not None else 0
                    )

                    col1, col2 = st.columns(2)
                    with col1:
                        submitted = st.form_submit_button("Guardar")
                    with col2:
                        cancel = st.form_submit_button("Cancelar")

                    if submitted:
                        activity_id = activity_options[selected_activity]
                        day_of_week = day_options[selected_day]
                        start_time = f"{hour:02d}:{minute:02d}"
                        monitor_id = monitor_options[selected_monitor]
                        if editing_id:
                            update_schedule(editing_id, activity_id, day_of_week, start_time, monitor_id)
                            st.success("Horario actualizado correctamente")
                        else:
                            create_schedule(activity_id, day_of_week, start_time, monitor_id)
                            st.success("Horario creado correctamente")

                        # Resetear el estado de edición
                        if 'editing_schedule_id' in st.session_state:
                            del st.session_state.editing_schedule_id
                        st.experimental_rerun()
                    if cancel:
                        if 'editing_schedule_id' in st.session_state:
                            del st.session_state.editing_schedule_id
                        st.experimental_rerun()

                # Mostrar lista de horarios para editar/eliminar
                st.subheader("Horarios Programados")
                if not schedules.empty:
                    schedules['day_name'] = schedules['day_of_week'].apply(lambda x: days_map[x])
                    schedules_sorted = schedules.sort_values(['day_of_week', 'start_time'])
                    for _, schedule in schedules_sorted.iterrows():
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            st.write(f"**{schedule['activity_name']}** - {schedule['day_name']} a las {format_time(schedule['start_time'])}")
                        with col2:
                            if st.button("✏️ Editar", key=f"edit_schedule_{schedule['id']}"):
                                st.session_state.editing_schedule_id = schedule['id']
                                st.experimental_rerun()
                        with col3:
                            if st.button("❌ Eliminar", key=f"delete_schedule_{schedule['id']}"):
                                delete_schedule(schedule['id'])
                                st.success("Horario eliminado correctamente")
                                st.experimental_rerun()
                else:
                    st.info("No hay horarios programados")
