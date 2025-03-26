import streamlit as st
from streamlit_calendar import calendar
from datetime import datetime, timedelta
import locale
import os

# Importa os módulos que criamos
from db import init_db
from reservation import reservar_laboratorio, validar_telefone
from admin import verificar_login, resetar_reservas, resetar_reserva_especifica
from export import exportar_reservas_por_tipo_excel, exportar_materiais_por_tipo_excel

# Configura o locale
try:
    os.system("apt-get update && apt-get install -y locales")
    os.system("sed -i '/pt_BR.UTF-8/s/^# //g' /etc/locale.gen && locale-gen")
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except Exception as e:
    locale.setlocale(locale.LC_TIME, '')

# Inicializa o banco de dados
init_db()

# Dicionário com os tipos de laboratórios
tipos_laboratorios = {
    "Laboratórios de Exatas": [
        "A16 - Nutrição / Solos e Sementes",
        "B15 - Multidisciplinar", 
        "C05 - Hidraulica/Elétrica",
        "C04 - Construção Civil/Arquitetura",
        "C03 - Motores"
    ],
    "Laboratórios de Saúde": [
        "A09 - Anatomia",
        "A10 - Enfermagem I",
        "A12 - Enfermagem II",
        "A14 - Microbiologia",
        "A16 - Nutrição / Solos e Sementes",
        "B15 - Multidisciplinar",
        "B17 - Farmácia",
    ],
    "Laboratórios de Informática": [
        "Laboratório de Informática 1",
        "Laboratório de Informática 2",
        "Laboratório de Informática 3"
    ]
}

st.title("Sistema de Reserva de Laboratórios")
opcao = st.sidebar.radio("Escolha uma opção:", ("Reservar laboratório", "Visualizar calendário", "Área Admin"))

if opcao == "Reservar laboratório":
    st.write("### Reservar Laboratório")
    tipo_laboratorio = st.selectbox("Selecione o tipo de laboratório:", list(tipos_laboratorios.keys()))
    laboratorios_filtrados = tipos_laboratorios[tipo_laboratorio]
    lab_escolhido = st.selectbox("Escolha o laboratório:", laboratorios_filtrados)
    
    hoje = datetime.today()
    proxima_semana = hoje + timedelta(days=(7 - hoje.weekday()))
    uma_semana_a_frente = proxima_semana + timedelta(days=4)
    data_reserva = st.date_input("Escolha a data da reserva", min_value=proxima_semana, max_value=uma_semana_a_frente, format="DD/MM/YYYY")
    
    periodo = st.selectbox("Escolha o período:", ["Matutino", "Noturno"])
    professor = st.text_input("Digite seu nome completo e número de telefone:")
    telefone_professor = st.text_input("Número de Celular", placeholder="digite no formato (XX) 9XXXX-XXXX")
    materiais = st.text_input("Digite os materiais necessários:")
    arquivos = st.file_uploader("Envie fotos ou PDFs dos materiais:", accept_multiple_files=True, type=["jpg", "jpeg", "png", "pdf"])
    
    # Adicionar a observação sobre possíveis alterações nas salas
    st.write("""
    **Observação:**O agendamento realizado por meio deste sistema está sujeito a alterações de laboratórios, 
    dependendo da disciplina e da aula aplicada. Todas as mudanças serão comunicadas previamente aos envolvidos.
    """)

    # Adicionar o WhatsApp de contato
    st.write("""
    **Dúvidas?** Entre em contato conosco pelo WhatsApp:\n
    [Técnico Laboratório Engenharias - Clique aqui para enviar uma mensagem](https://wa.me/554232209959)\n
    [Técnico Laboratório Saúde - Clique aqui para enviar uma mensagem](https://wa.me/554232209995)\n
    [Técnico Laboratório Informática - Clique aqui para enviar uma mensagem](https://wa.me/554232209961)
    """)
    
    if st.button("Reservar"):
        if validar_telefone(telefone_professor) == False:
            st.error("Número de celular inválido. Digite no formato (XX) 9XXXX-XXXX.")
        elif (professor and telefone_professor and materiais) or (professor and telefone_professor and arquivos):
            reservar_laboratorio(lab_escolhido, professor, telefone_professor, materiais, data_reserva, periodo, arquivos, tipo_laboratorio)
        else:
            st.warning("Preencha os campos obrigatórios.")

elif opcao == "Visualizar calendário":
    st.write("### Calendário de Reservas por Laboratório")

    # Buscar as reservas ativas no banco de dados
    import sqlite3
    from datetime import datetime
    conn = sqlite3.connect('reservas_labs.db', check_same_thread=False)
    c = conn.cursor()

    c.execute("""
        SELECT tipo_laboratorio, laboratorio, professor, data, periodo, horario_inicio, horario_fim
        FROM reservas 
        WHERE disponivel = 0
    """)
    reservas = c.fetchall()
    conn.close()

    # Agrupar reservas por laboratório
    reservas_por_lab = {}
    for tipo_laboratorio, lab, professor, data, periodo, horario_inicio, horario_fim in reservas:
        if lab not in reservas_por_lab:
            reservas_por_lab[lab] = []
        reservas_por_lab[lab].append({
            "professor": professor,
            "data": data,
            "horario_inicio": horario_inicio,
            "horario_fim": horario_fim
        })

    # Exibir um calendário para cada laboratório
    for lab, reservas_list in reservas_por_lab.items():
        st.write(f"#### {lab}")
        
        # Criar a lista de eventos para o calendário
        eventos = []
        for reserva in reservas_list:
            try:
                # Converter a data do formato DD/MM/YYYY para YYYY-MM-DD
                data_iso = datetime.strptime(reserva['data'], '%d/%m/%Y').strftime('%Y-%m-%d')
            except Exception as e:
                st.error(f"Erro ao converter a data {reserva['data']}: {e}")
                continue

            evento = {
                "title": f"{reserva['professor']} ({reserva['horario_inicio']} - {reserva['horario_fim']})",
                "start": data_iso
            }
            eventos.append(evento)
        
        # Renderiza o calendário interativo
        calendar(
            events=eventos,
            options={
                "initialView": "dayGridMonth",
                "locale": "pt-br",
            },
            key=f"calendar_{lab}"  # Key única para cada calendário
        )


elif opcao == "Área Admin":
    st.write("### Área de Administração")
    if "admin_logado" not in st.session_state:
        st.session_state["admin_logado"] = False

    if not st.session_state["admin_logado"]:
        username = st.text_input("Usuário:")
        password = st.text_input("Senha:", type="password")
        if st.button("Login"):
            if verificar_login(username, password):
                st.session_state["admin_logado"] = True
                st.success("Login realizado com sucesso!")
            else:
                st.error("Credenciais inválidas.")
    
    if st.session_state["admin_logado"]:
        st.write("### Reservas Ativas")
        
        # Conectar ao banco de dados (supondo que você utilize a função get_connection do seu módulo db)
        from db import get_connection
        conn = get_connection()
        c = conn.cursor()
        
        c.execute("""
            SELECT id, data, tipo_laboratorio, laboratorio, professor, telefone_professor, periodo, materiais, 
                   horario_inicio, horario_fim, fotos 
            FROM reservas 
            WHERE disponivel = 0
        """)
        reservas = c.fetchall()
        
        if reservas:
            for reserva in reservas:
                reserva_id, data, tipo_lab, lab, professor, telefone_professor, periodo, materiais, horario_inicio, horario_fim, fotos = reserva
                st.write(f"**ID: {reserva_id}**")
                st.write(f"**Data:** {data}")
                st.write(f"**Tipo de Laboratório:** {tipo_lab}")
                st.write(f"**Laboratório:** {lab}")
                st.write(f"**Professor:** {professor}")
                st.write(f"**Telefone do Professor:** {telefone_professor}")
                st.write(f"**Período:** {periodo}")
                st.write(f"**Horário:** {horario_inicio} - {horario_fim}")
                st.write(f"**Materiais:** {materiais}")
                
                # Exibir arquivos enviados (imagens e PDFs)
                if fotos:
                    arquivos_list = fotos.split(",")
                    for arquivo in arquivos_list:
                        if arquivo.endswith(".pdf"):
                            with open(arquivo, "rb") as f:
                                st.download_button(
                                    label=f"Baixar PDF: {os.path.basename(arquivo)}",
                                    data=f,
                                    file_name=os.path.basename(arquivo),
                                    mime="application/pdf",
                                    key=f"pdf_{reserva_id}_{arquivo}"
                                )
                        else:
                            st.image(arquivo, width=600, caption=os.path.basename(arquivo))
                
                # Botão para resetar a reserva específica
                if st.button(f"Resetar Reserva {reserva_id}", key=f"reset_{reserva_id}"):
                    resetar_reserva_especifica(reserva_id)
                    st.success(f"Reserva {reserva_id} resetada com sucesso!")
                    st.experimental_rerun()  # Atualiza a página após o reset
                st.write("---")
        else:
            st.info("Nenhuma reserva encontrada.")
        
        # Botão para resetar todas as reservas
        if st.button("Resetar Todas as Reservas"):
            resetar_reservas()
            st.experimental_rerun()  # Atualiza a página após o reset

        # Seção de Exportação para Excel
        st.write("### Exportar Planilhas")
        
        # Importa as funções de exportação do módulo export
        from export import exportar_reservas_por_tipo_excel, exportar_materiais_por_tipo_excel
        
        # Exportar Reservas por Tipo de Laboratório
        st.write("#### Exportar Reservas por Tipo de Laboratório")
        tipo_laboratorio_export = st.selectbox("Selecione o tipo de laboratório para exportar reservas:", 
                                                list(tipos_laboratorios.keys()), key="export_reservas")
        
        if st.button("Atualizar para baixar planilha específica (Excel)", key="btn_export_reservas"):
            reservas_excel = exportar_reservas_por_tipo_excel(tipo_laboratorio_export)
            st.download_button(
                label=f"Baixar Reservas {tipo_laboratorio_export} (Excel)",
                data=reservas_excel,
                file_name=f"reservas_{tipo_laboratorio_export}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_reservas"
            )
        
        # Exportar Materiais por Tipo de Laboratório
        st.write("#### Exportar Materiais por Tipo de Laboratório")
        tipo_laboratorio_export_materiais = st.selectbox("Selecione o tipo de laboratório para exportar materiais:", 
                                                         list(tipos_laboratorios.keys()), key="export_materiais")
        
        if st.button("Atualizar para baixar planilha específica (Excel)", key="btn_export_materiais"):
            materiais_excel = exportar_materiais_por_tipo_excel(tipo_laboratorio_export_materiais)
            st.download_button(
                label=f"Baixar Materiais {tipo_laboratorio_export_materiais} (Excel)",
                data=materiais_excel,
                file_name=f"materiais_{tipo_laboratorio_export_materiais}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_materiais"
            )


