import streamlit as st
from db import get_connection

conn = get_connection()
c = conn.cursor()

def resetar_reservas():
    c.execute("DELETE FROM reservas")
    conn.commit()
    st.success("Todas as reservas foram resetadas!")

def resetar_reserva_especifica(reserva_id):
    c.execute("DELETE FROM reservas WHERE id = ?", (reserva_id,))
    conn.commit()
    st.success(f"Reserva {reserva_id} resetada com sucesso!")

def verificar_login(username, password):
    admin_username = "admin"
    admin_password = "senha123"  # Substitua por uma senha segura
    return username == admin_username and password == admin_password
