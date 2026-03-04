import streamlit as st
from database import executar_query
import datetime

def render():

    st.title("💰 Relatório Financeiro")

    col1, col2 = st.columns(2)

    with col1:
        data_inicio = st.date_input("Data início", value=datetime.date.today().replace(day=1))

    with col2:
        data_fim = st.date_input("Data fim", value=datetime.date.today())

    if st.button("Gerar Relatório"):

        resultados = executar_query("""
            SELECT a.data_agend, c.nome, p.nome, p.valor
            FROM agendamentos a
            JOIN clientes c ON a.cliente_id = c.id
            JOIN procedimentos p ON a.procedimento_id = p.id
            WHERE a.data_agend BETWEEN %s AND %s
            ORDER BY a.data_agend
        """, (data_inicio, data_fim), fetch=True)

        if resultados:

            total = 0

            for r in resultados:
                st.write(f"{r[0]} | {r[1]} | {r[2]} | R$ {r[3]}")
                total += float(r[3])

            st.divider()
            st.success(f"Total no período: R$ {total:.2f}")

        else:
            st.warning("Nenhum registro encontrado.")