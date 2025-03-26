import pandas as pd
import io
from db import get_connection

conn = get_connection()
c = conn.cursor()

def exportar_reservas_por_tipo_excel(tipo_laboratorio):
    c.execute('''
        SELECT data, laboratorio, professor, periodo, horario_inicio, horario_fim 
        FROM reservas 
        WHERE tipo_laboratorio = ? AND disponivel = 0
    ''', (tipo_laboratorio,))
    reservas = c.fetchall()
    df_reservas = pd.DataFrame(reservas, columns=["Data", "Laboratório", "Professor", "Periodo", "Horário Início", "Horário Fim"])
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_reservas.to_excel(writer, index=False, sheet_name="Reservas", startrow=2)
        workbook = writer.book
        worksheet = writer.sheets["Reservas"]
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'bg_color': '#FFFFFF',
        })
        worksheet.merge_range('A1:F1', f"Reservas - {tipo_laboratorio}", title_format)
        
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'align': 'center',
            'valign': 'top',
            'border': 1,
            'bg_color': '#FFFFFF',
        })
        cell_format = workbook.add_format({
            'border': 1,
            'text_wrap': True,
            'align': 'center',
            'valign': 'top',
        })
        for col_num, value in enumerate(df_reservas.columns.values):
            worksheet.write(2, col_num, value, header_format)
        for row in range(len(df_reservas)):
            for col in range(len(df_reservas.columns)):
                worksheet.write(row + 3, col, df_reservas.iloc[row, col], cell_format)
        for i, col in enumerate(df_reservas.columns):
            max_len = max(df_reservas[col].astype(str).apply(len).max(), len(col)) + 2
            worksheet.set_column(i, i, max_len)
        worksheet.set_header(f'&CReservas de Laboratório - {tipo_laboratorio}')
        worksheet.set_footer('&CPágina &P de &N')
        worksheet.set_margins(left=0.7, right=0.7, top=1.0, bottom=0.75)
        worksheet.set_landscape()
        worksheet.freeze_panes(3, 0)
    output.seek(0)
    return output

def exportar_materiais_por_tipo_excel(tipo_laboratorio):
    c.execute('''
        SELECT data, laboratorio, professor, materiais, periodo, horario_inicio, horario_fim 
        FROM reservas 
        WHERE tipo_laboratorio = ? AND disponivel = 0
    ''', (tipo_laboratorio,))
    materiais = c.fetchall()
    df_materiais = pd.DataFrame(materiais, columns=["Data", "Laboratório", "Professor", "Materiais", "Periodo", "Horário Início", "Horário Fim"])
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_materiais.to_excel(writer, index=False, sheet_name="Materiais")
    output.seek(0)
    return output
