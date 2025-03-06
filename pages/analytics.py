import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import get_activity_stats, get_daily_stats, get_all_users
from utils import check_monitor_access

def show():
    # Verificar acceso de monitor
    check_monitor_access()

    st.title("📊 Análisis y Estadísticas")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Actividad por Día")
        # Obtener estadísticas por día
        daily_stats = get_daily_stats()
        if not daily_stats.empty:
            # Reordenar días de la semana correctamente
            day_order = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
            daily_stats['day'] = pd.Categorical(daily_stats['day'], categories=day_order, ordered=True)
            daily_stats = daily_stats.sort_values('day')

            # Crear gráfico
            fig = px.bar(
                daily_stats, x='day', y='total_bookings',
                title='Número de Reservas por Día',
                labels={'day': 'Día', 'total_bookings': 'Número de Reservas'}
            )
            st.plotly_chart(fig)
        else:
            st.info("No hay suficientes datos para mostrar estadísticas por día")

    with col2:
        st.subheader("Actividades Más Populares")
        # Obtener estadísticas por actividad
        activity_stats = get_activity_stats()
        if not activity_stats.empty:
            # Ordenar por reservas totales
            activity_stats = activity_stats.sort_values('total_bookings', ascending=False)

            # Crear gráfico
            fig = px.pie(
                activity_stats, values='total_bookings', names='activity_name',
                title='Distribución de Reservas por Actividad'
            )
            st.plotly_chart(fig)
        else:
            st.info("No hay suficientes datos para mostrar estadísticas de actividades")

    # Estadística de asistencia
    st.subheader("Tasa de Asistencia")
    # Obtener estadísticas de asistencia
    attendance_stats = get_activity_stats()
    if not attendance_stats.empty and attendance_stats['total_bookings'].sum() > 0:
        # Añadir columna de tasa de asistencia
        attendance_stats['attendance_rate'] = (attendance_stats['attended_count'] / attendance_stats['total_bookings']).fillna(0)
        attendance_stats = attendance_stats.sort_values('attendance_rate', ascending=False)

        # Crear gráfico
        fig = px.bar(
            attendance_stats, x='activity_name', y='attendance_rate',
            title='Tasa de Asistencia por Actividad',
            labels={'activity_name': 'Actividad', 'attendance_rate': 'Tasa de Asistencia'},
            range_y=[0, 1]
        )
        # Añadir línea promedio
        fig.add_shape(
            type='line', x0=-0.5, y0=attendance_stats['attendance_rate'].mean(),
            x1=len(attendance_stats)-0.5, y1=attendance_stats['attendance_rate'].mean(),
            line=dict(color='red', dash='dash')
        )
        fig.update_yaxes(tickformat=".0%")
        st.plotly_chart(fig)
    else:
        st.info("No hay suficientes datos para mostrar estadísticas de asistencia")

    # Tabla de usuarios nuevos
    st.subheader("Nuevos Usuarios")
    # Obtener usuarios
    users = get_all_users()
    if not users.empty:
        # Ordenar por fecha de registro
        users = users.sort_values('join_date', ascending=False).head(10)
        # Modificar la presentación
        users['tipo'] = users['is_monitor'].apply(lambda x: "Monitor" if x else "Miembro")
        st.dataframe(
            users[['username', 'email', 'full_name', 'tipo', 'join_date']],
            column_config={
                'username': 'Usuario',
                'email': 'Email',
                'full_name': 'Nombre completo',
                'tipo': 'Tipo',
                'join_date': 'Fecha de registro'
            },
            hide_index=True
        )
    else:
        st.info("No hay usuarios registrados")
