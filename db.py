import sqlite3
import os

DB_NAME = 'reservas_labs.db'

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Primeiro: cria a tabela, se ela ainda não existir
    c.execute('''
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_laboratorio TEXT NOT NULL,
            laboratorio TEXT NOT NULL,
            professor TEXT,
            telefone_professor TEXT,
            materiais TEXT,
            data TEXT NOT NULL,
            periodo TEXT NOT NULL,
            horario_inicio TEXT,
            horario_fim TEXT,
            disponivel INTEGER DEFAULT 1,
            fotos TEXT
        )
    ''')
    conn.commit()
    
    # Verifica se a tabela já existe e se possui as colunas necessárias
    c.execute("PRAGMA table_info(reservas)")
    colunas = [col[1] for col in c.fetchall()]
    if "tipo_laboratorio" not in colunas:
        c.execute("ALTER TABLE reservas ADD COLUMN tipo_laboratorio TEXT")
    if "data" not in colunas:
        c.execute("ALTER TABLE reservas ADD COLUMN data TEXT")
    if "telefone_professor" not in colunas:
        c.execute("ALTER TABLE reservas ADD COLUMN telefone_professor TEXT")
    if "materiais" not in colunas:
        c.execute("ALTER TABLE reservas ADD COLUMN materiais TEXT")
    if "periodo" not in colunas:
        c.execute("ALTER TABLE reservas ADD COLUMN periodo TEXT")
    if "horario_inicio" not in colunas:
        c.execute("ALTER TABLE reservas ADD COLUMN horario_inicio TEXT")
    if "horario_fim" not in colunas:
        c.execute("ALTER TABLE reservas ADD COLUMN horario_fim TEXT")
    if "fotos" not in colunas:
        c.execute("ALTER TABLE reservas ADD COLUMN fotos TEXT")
    
    # Cria a tabela se não existir
    c.execute('''
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_laboratorio TEXT NOT NULL,
            laboratorio TEXT NOT NULL,
            professor TEXT,
            telefone_professor TEXT,
            materiais TEXT,
            data TEXT NOT NULL,
            periodo TEXT NOT NULL,
            horario_inicio TEXT,
            horario_fim TEXT,
            disponivel INTEGER DEFAULT 1,
            fotos TEXT
        )
    ''')
    conn.commit()
    conn.close()
