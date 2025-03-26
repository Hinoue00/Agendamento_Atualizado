from datetime import datetime, timedelta
import os
import re
from PIL import Image
import streamlit as st
from db import get_connection

conn = get_connection()
c = conn.cursor()

def validar_data_reserva(data_reserva, professor):
    hoje = datetime.today().date()
    proxima_semana = hoje + timedelta(days=(7 - hoje.weekday()))
    uma_semana_a_frente = proxima_semana + timedelta(days=4)

    if data_reserva < proxima_semana:
        return False, "A reserva deve ser feita para a próxima semana."
    elif data_reserva >= uma_semana_a_frente:
        return False, "A reserva não pode ser feita para mais de uma semanas à frente."
    
    semana_anterior = data_reserva - timedelta(days=7)
    c.execute('SELECT COUNT(*) FROM reservas WHERE professor = ? AND data = ?', (professor, semana_anterior.strftime('%d/%m/%Y')))
    if c.fetchone()[0] > 0:
        return False, "Você já tem uma reserva na semana anterior. Não é possível marcar para a semana seguinte."
    
    return True, ""

def reservar_laboratorio(lab_escolhido, professor, telefone_professor, materiais, data, periodo, arquivos, tipo_laboratorio):
    valido, mensagem = validar_data_reserva(data, professor)
    if not valido:
        st.error(mensagem)
        return

    if periodo == "Matutino":
        horario_inicio = "08:00"
        horario_fim = "12:00"
    elif periodo == "Noturno":
        horario_inicio = "19:00"
        horario_fim = "22:00"
    else:
        st.error("Período inválido.")
        return

    # Verifica se já existe uma reserva para o mesmo laboratório, data e período
    c.execute('''
        SELECT COUNT(*) FROM reservas 
        WHERE laboratorio = ? AND data = ? AND periodo = ? AND disponivel = 0
    ''', (lab_escolhido, data.strftime('%d/%m/%Y'), periodo))
    if c.fetchone()[0] > 0:
        st.error(f"O laboratório {lab_escolhido} já está reservado para o período {periodo} nesta data.")
        return

    # Processa o upload de arquivos
    fotos_dir = "fotos"
    if not os.path.exists(fotos_dir):
        os.makedirs(fotos_dir)

    arquivos_paths = []
    if arquivos:
        for arquivo in arquivos:
            nome_arquivo = f"{data.strftime('%Y%m%d')}_{lab_escolhido}_{arquivo.name}"
            nome_arquivo = nome_arquivo.replace("/", "_").replace("\\", "_").replace(":", "_")
            caminho_arquivo = os.path.join(fotos_dir, nome_arquivo)
            try:
                with open(caminho_arquivo, "wb") as f:
                    f.write(arquivo.getbuffer())
                arquivos_paths.append(caminho_arquivo)
                
                if arquivo.type.startswith("image/"):
                    img = Image.open(arquivo)
                    st.image(img, caption=nome_arquivo, width=600)
                elif arquivo.type == "application/pdf":
                    st.write(f"**PDF enviado:** {nome_arquivo}")
            except Exception as e:
                st.error(f"Erro ao processar o arquivo {arquivo.name}: {e}")
                return

    arquivos_str = ",".join(arquivos_paths)

    c.execute('''
        INSERT INTO reservas (laboratorio, professor, telefone_professor, materiais, data, periodo, horario_inicio, horario_fim, disponivel, fotos, tipo_laboratorio)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
    ''', (lab_escolhido, professor, telefone_professor, materiais, data.strftime('%d/%m/%Y'), periodo, horario_inicio, horario_fim, arquivos_str, tipo_laboratorio))
    conn.commit()
    st.success(f"Laboratório {lab_escolhido} reservado com sucesso para {professor} no dia {data.strftime('%d/%m/%Y')} no período {periodo} das {horario_inicio} às {horario_fim}.")

def validar_telefone(numero):
    #Valida o número de telefone no formato (DDD) 9XXXX-XXXX
    padrao = r"^\(\d{2}\) 9\d{4}-\d{4}$"
    return bool(re.match(padrao, numero))

