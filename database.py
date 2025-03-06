import sqlite3
import streamlit as st
import pandas as pd
import bcrypt
from datetime import datetime

# Configuración de la base de datos
def get_connection():
    return sqlite3.connect('gym.db', check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Crear tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            is_monitor BOOLEAN DEFAULT FALSE,
            join_date TEXT DEFAULT CURRENT_DATE
        )
    ''')

    # Crear tabla de actividades
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            max_capacity INTEGER NOT NULL,
            duration INTEGER NOT NULL,
            monitor_id INTEGER,
            FOREIGN KEY (monitor_id) REFERENCES users(id)
        )
    ''')

    # Crear tabla de horarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_id INTEGER NOT NULL,
            day_of_week INTEGER NOT NULL,
            start_time TEXT NOT NULL,
            monitor_id INTEGER NOT NULL,
            FOREIGN KEY (activity_id) REFERENCES activities(id),
            FOREIGN KEY (monitor_id) REFERENCES users(id)
        )
    ''')

    # Crear tabla de reservas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            schedule_id INTEGER NOT NULL,
            booking_date TEXT DEFAULT CURRENT_DATE,
            attended BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (schedule_id) REFERENCES schedules(id),
            UNIQUE(user_id, schedule_id)
        )
    ''')

    # Insertar un usuario administrador por defecto si no existe
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        hashed_password = bcrypt.hashpw('admin123'.encode(), bcrypt.gensalt()).decode()
        cursor.execute(
            "INSERT INTO users (username, password, email, full_name, is_monitor) VALUES (?, ?, ?, ?, ?)",
            ('admin', hashed_password, 'admin@gym.com', 'Administrador', True)
        )

    conn.commit()
    conn.close()

# Funciones para los usuarios
def get_user(username):
    conn = get_connection()
    user = pd.read_sql(
        "SELECT id, username, password, email, full_name, is_monitor FROM users WHERE username = ?",
        conn, params=(username,)
    )
    conn.close()
    if not user.empty:
        return user.iloc[0].to_dict()
    return None

def create_user(username, password, email, full_name, is_monitor=False):
    conn = get_connection()
    cursor = conn.cursor()
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        cursor.execute(
            "INSERT INTO users (username, password, email, full_name, is_monitor) VALUES (?, ?, ?, ?, ?)",
            (username, hashed_password, email, full_name, is_monitor)
        )
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

def update_user(user_id, email, full_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET email = ?, full_name = ? WHERE id = ?",
        (email, full_name, user_id)
    )
    conn.commit()
    conn.close()

def change_password(user_id, new_password):
    conn = get_connection()
    cursor = conn.cursor()
    hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    cursor.execute(
        "UPDATE users SET password = ? WHERE id = ?",
        (hashed_password, user_id)
    )
    conn.commit()
    conn.close()

# Funciones para actividades
def get_activities():
    conn = get_connection()
    activities = pd.read_sql(
        """
        SELECT a.id, a.name, a.description, a.max_capacity, a.duration, u.username as monitor_name, a.monitor_id
        FROM activities a
        LEFT JOIN users u ON a.monitor_id = u.id
        """,
        conn
    )
    conn.close()
    return activities

def get_activity(activity_id):
    conn = get_connection()
    activity = pd.read_sql(
        """
        SELECT a.id, a.name, a.description, a.max_capacity, a.duration, u.username as monitor_name, a.monitor_id
        FROM activities a
        LEFT JOIN users u ON a.monitor_id = u.id
        WHERE a.id = ?
        """,
        conn, params=(activity_id,)
    )
    conn.close()
    if not activity.empty:
        return activity.iloc[0].to_dict()
    return None

def create_activity(name, description, max_capacity, duration, monitor_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO activities (name, description, max_capacity, duration, monitor_id) VALUES (?, ?, ?, ?, ?)",
        (name, description, max_capacity, duration, monitor_id)
    )
    activity_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return activity_id

def update_activity(activity_id, name, description, max_capacity, duration, monitor_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE activities
        SET name = ?, description = ?, max_capacity = ?, duration = ?, monitor_id = ?
        WHERE id = ?
        """,
        (name, description, max_capacity, duration, monitor_id, activity_id)
    )
    conn.commit()
    conn.close()

def delete_activity(activity_id):
    conn = get_connection()
    cursor = conn.cursor()
    # Borrar horarios y reservas asociadas
    cursor.execute("DELETE FROM bookings WHERE schedule_id IN (SELECT id FROM schedules WHERE activity_id = ?)", (activity_id,))
    cursor.execute("DELETE FROM schedules WHERE activity_id = ?", (activity_id,))
    cursor.execute("DELETE FROM activities WHERE id = ?", (activity_id,))
    conn.commit()
    conn.close()

# Funciones para horarios
def get_schedules():
    conn = get_connection()
    schedules = pd.read_sql(
        """
        SELECT s.id, s.activity_id, a.name as activity_name, s.day_of_week, s.start_time, u.username as monitor_name, s.monitor_id,
               (SELECT COUNT(*) FROM bookings WHERE schedule_id = s.id) as current_bookings, a.max_capacity
        FROM schedules s
        JOIN activities a ON s.activity_id = a.id
        JOIN users u ON s.monitor_id = u.id
        ORDER BY s.day_of_week, s.start_time
        """,
        conn
    )
    conn.close()
    return schedules

def create_schedule(activity_id, day_of_week, start_time, monitor_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO schedules (activity_id, day_of_week, start_time, monitor_id) VALUES (?, ?, ?, ?)",
        (activity_id, day_of_week, start_time, monitor_id)
    )
    schedule_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return schedule_id

def update_schedule(schedule_id, activity_id, day_of_week, start_time, monitor_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE schedules
        SET activity_id = ?, day_of_week = ?, start_time = ?, monitor_id = ?
        WHERE id = ?
        """,
        (activity_id, day_of_week, start_time, monitor_id, schedule_id)
    )
    conn.commit()
    conn.close()

def delete_schedule(schedule_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bookings WHERE schedule_id = ?", (schedule_id,))
    cursor.execute("DELETE FROM schedules WHERE id = ?", (schedule_id,))
    conn.commit()
    conn.close()

# Funciones para reservas
def get_user_bookings(user_id):
    conn = get_connection()
    bookings = pd.read_sql(
        """
        SELECT b.id, s.id as schedule_id, a.name as activity_name,
               CASE s.day_of_week
                   WHEN 0 THEN 'Lunes'
                   WHEN 1 THEN 'Martes'
                   WHEN 2 THEN 'Miércoles'
                   WHEN 3 THEN 'Jueves'
                   WHEN 4 THEN 'Viernes'
                   WHEN 5 THEN 'Sábado'
                   WHEN 6 THEN 'Domingo'
               END as day,
               s.start_time, u.username as monitor_name, b.booking_date, b.attended
        FROM bookings b
        JOIN schedules s ON b.schedule_id = s.id
        JOIN activities a ON s.activity_id = a.id
        JOIN users u ON s.monitor_id = u.id
        WHERE b.user_id = ?
        ORDER BY b.booking_date DESC
        """,
        conn, params=(user_id,)
    )
    conn.close()
    return bookings

def create_booking(user_id, schedule_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO bookings (user_id, schedule_id) VALUES (?, ?)",
            (user_id, schedule_id)
        )
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

def cancel_booking(booking_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
    conn.commit()
    conn.close()

def mark_attendance(booking_id, attended):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE bookings SET attended = ? WHERE id = ?",
        (attended, booking_id)
    )
    conn.commit()
    conn.close()

# Funciones para monitores
def get_monitors():
    conn = get_connection()
    monitors = pd.read_sql(
        "SELECT id, username, email, full_name, join_date FROM users WHERE is_monitor = 1",
        conn
    )
    conn.close()
    return monitors

def get_all_users():
    conn = get_connection()
    users = pd.read_sql(
        "SELECT id, username, email, full_name, is_monitor, join_date FROM users ORDER BY join_date DESC",
        conn
    )
    conn.close()
    return users

# Funciones para análisis
def get_activity_stats():
    conn = get_connection()
    stats = pd.read_sql(
        """
        SELECT a.name as activity_name, COUNT(b.id) as total_bookings,
               SUM(CASE WHEN b.attended = 1 THEN 1 ELSE 0 END) as attended_count
        FROM activities a
        LEFT JOIN schedules s ON a.id = s.activity_id
        LEFT JOIN bookings b ON s.id = b.schedule_id
        GROUP BY a.id
        """,
        conn
    )
    conn.close()
    return stats

def get_daily_stats():
    conn = get_connection()
    stats = pd.read_sql(
        """
        SELECT
            CASE s.day_of_week
                WHEN 0 THEN 'Lunes'
                WHEN 1 THEN 'Martes'
                WHEN 2 THEN 'Miércoles'
                WHEN 3 THEN 'Jueves'
                WHEN 4 THEN 'Viernes'
                WHEN 5 THEN 'Sábado'
                WHEN 6 THEN 'Domingo'
            END as day,
            COUNT(b.id) as total_bookings
        FROM schedules s
        LEFT JOIN bookings b ON s.id = b.schedule_id
        GROUP BY s.day_of_week
        """,
        conn
    )
    conn.close()
    return stats
