import streamlit as st
import datetime
from database import executar_query


def render():

    # =========================
    # TÍTULO DA PÁGINA
    # =========================
    st.header("📋 Visualizar Agendamentos")

    # =========================
    # FILTROS
    # =========================

    st.subheader("🔎 Filtros")

    col1, col2 = st.columns(2)

    with col1:
        # Filtro por data
        data_filtro = st.date_input(
            "Filtrar por data",
            value=datetime.date.today()
        )

    with col2:
        # Carrega lista de clientes para filtro
        clientes = executar_query(
            "SELECT id, nome, sobrenome FROM clientes",
            fetch=True
        )

        clientes_dict = {
            f"{c[1]} {c[2]}": c[0]
            for c in clientes
        }

        cliente_filtro = st.selectbox(
            "Filtrar por cliente (opcional)",
            ["Todos"] + list(clientes_dict.keys())
        )

    # =========================
    # MONTA QUERY DINÂMICA
    # =========================

    query = """
        SELECT 
            a.id,
            c.nome,
            c.sobrenome,
            p.nome,
            a.data_agend,
            a.hora_agend,
            p.duracao
        FROM agendamentos a
        JOIN clientes c ON a.cliente_id = c.id
        JOIN procedimentos p ON a.procedimento_id = p.id
        WHERE a.data_agend = %s
    """

    params = [data_filtro]

    # Se cliente específico for escolhido, adiciona filtro
    if cliente_filtro != "Todos":
        query += " AND a.cliente_id = %s"
        params.append(clientes_dict[cliente_filtro])

    query += " ORDER BY a.hora_agend ASC"

    agendamentos = executar_query(
        query,
        tuple(params),
        fetch=True
    )

    # =========================
    # RESULTADOS
    # =========================

    st.divider()

    if not agendamentos:
        st.info("Nenhum agendamento encontrado.")
        return

    for ag in agendamentos:

        (
            ag_id,
            nome,
            sobrenome,
            procedimento,
            data_ag,
            hora_ag,
            duracao
        ) = ag

        # Converte hora (timedelta) para HH:MM
        total = hora_ag.total_seconds()
        hora_int = int(total // 3600)
        minuto_int = int((total % 3600) // 60)

        inicio = datetime.datetime.combine(
            data_ag,
            datetime.time(hora_int, minuto_int)
        )

        fim = inicio + datetime.timedelta(minutes=duracao)

        with st.container():

            col1, col2 = st.columns([6, 1])

            with col1:
                st.write(f"👤 **{nome} {sobrenome}**")
                st.write(f"💄 {procedimento}")
                st.write(
                    f"⏰ {inicio.strftime('%H:%M')} - {fim.strftime('%H:%M')}"
                )

            with col2:
                # Botão excluir
                if st.button("🗑", key=f"del_ag_{ag_id}"):

                    executar_query(
                        "DELETE FROM agendamentos WHERE id = %s",
                        (ag_id,)
                    )

                    st.success("Agendamento excluído.")
                    st.rerun()

        st.divider()