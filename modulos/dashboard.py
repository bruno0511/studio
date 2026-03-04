import streamlit as st
from database import executar_query
import datetime
import pandas as pd
import plotly.express as px

def render():

    # =====================================================
    # TÍTULO DO DASHBOARD
    # =====================================================
    st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🎯 Dashboard do Estúdio</h1>", unsafe_allow_html=True)
    st.markdown("---")

    # Data de hoje e primeiro dia do mês
    hoje = datetime.date.today()
    primeiro_dia_mes = hoje.replace(day=1)

    # =====================================================
    # 1️⃣ LEMBRETE DE AGENDAMENTOS DO DIA (CARDS COLORIDOS)
    # =====================================================
    st.subheader("⏰ Agendamentos de Hoje")

    # Busca agendamentos de hoje
    agendamentos_hoje = executar_query("""
        SELECT a.hora_agend, c.nome, c.sobrenome, p.nome
        FROM agendamentos a
        JOIN clientes c ON a.cliente_id = c.id
        JOIN procedimentos p ON a.procedimento_id = p.id
        WHERE a.data_agend = %s
        ORDER BY a.hora_agend
    """, (hoje,), fetch=True)

    if agendamentos_hoje:
        for ag in agendamentos_hoje:
            hora, nome, sobrenome, procedimento = ag

            # >>> Converte timedelta para string "HH:MM"
            horas = hora.seconds // 3600
            minutos = (hora.seconds % 3600) // 60
            hora_str = f"{horas:02d}:{minutos:02d}"

            # Exibe cada agendamento como card colorido
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #FF9A8B, #FF6A88);
                padding: 15px;
                border-radius: 10px;
                color: white;
                margin-bottom: 10px;
            ">
                <h4 style='margin:0;'>{hora_str} - {nome} {sobrenome}</h4>
                <p style='margin:0;'>Procedimento: {procedimento}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Nenhum agendamento para hoje.")

    st.markdown("---")

    # =====================================================
    # 2️⃣ MÉTRICAS PRINCIPAIS (CARDS COLORIDOS)
    # =====================================================
    st.subheader("📌 Métricas do Mês")

    # Total de agendamentos no mês
    total_agend = executar_query("""
        SELECT COUNT(*) 
        FROM agendamentos
        WHERE data_agend >= %s
    """, (primeiro_dia_mes,), fetch=True)[0][0]

    # Faturamento do mês
    faturamento = executar_query("""
        SELECT SUM(p.valor)
        FROM agendamentos a
        JOIN procedimentos p ON a.procedimento_id = p.id
        WHERE a.data_agend >= %s
    """, (primeiro_dia_mes,), fetch=True)[0][0] or 0

    # Procedimento mais vendido
    mais_vendido = executar_query("""
        SELECT p.nome, COUNT(*) as total
        FROM agendamentos a
        JOIN procedimentos p ON a.procedimento_id = p.id
        WHERE a.data_agend >= %s
        GROUP BY p.nome
        ORDER BY total DESC
        LIMIT 1
    """, (primeiro_dia_mes,), fetch=True)

    # Layout com 3 cards coloridos
    col1, col2, col3 = st.columns(3)
    col1.markdown(f"""
    <div style="
        background-color:#4ADE80;
        padding:20px;
        border-radius:15px;
        text-align:center;
        color:white;">
        <h3>Agendamentos</h3>
        <h2>{total_agend}</h2>
    </div>
    """, unsafe_allow_html=True)

    col2.markdown(f"""
    <div style="
        background-color:#22D3EE;
        padding:20px;
        border-radius:15px;
        text-align:center;
        color:white;">
        <h3>Faturamento</h3>
        <h2>R$ {faturamento:.2f}</h2>
    </div>
    """, unsafe_allow_html=True)

    col3.markdown(f"""
    <div style="
        background-color:#FBBF24;
        padding:20px;
        border-radius:15px;
        text-align:center;
        color:white;">
        <h3>Mais Vendido</h3>
        <h2>{mais_vendido[0][0] if mais_vendido else 'Nenhum'}</h2>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # =====================================================
    # 3️⃣ GRÁFICOS INTERATIVOS (CORES VIVAS)
    # =====================================================
    st.subheader("📈 Performance por Procedimento (Mês)")

    # Busca dados de faturamento e quantidade por procedimento
    dados_procedimentos = executar_query("""
        SELECT p.nome, COUNT(*) as qtd, SUM(p.valor) as total
        FROM agendamentos a
        JOIN procedimentos p ON a.procedimento_id = p.id
        WHERE a.data_agend >= %s
        GROUP BY p.nome
        ORDER BY qtd DESC
    """, (primeiro_dia_mes,), fetch=True)

    if dados_procedimentos:
        df_proc = pd.DataFrame(dados_procedimentos, columns=["Procedimento", "Quantidade", "Faturamento"])

        # Gráfico de barras - quantidade
        fig_qtd = px.bar(
            df_proc,
            x="Procedimento",
            y="Quantidade",
            color="Quantidade",
            text="Quantidade",
            title="Quantidade de Agendamentos por Procedimento",
            color_continuous_scale=px.colors.sequential.Plasma
        )
        fig_qtd.update_layout(xaxis_title="Procedimento", yaxis_title="Quantidade")
        st.plotly_chart(fig_qtd, use_container_width=True)

        # Gráfico de barras - faturamento
        fig_fat = px.bar(
            df_proc,
            x="Procedimento",
            y="Faturamento",
            color="Faturamento",
            text="Faturamento",
            title="Faturamento por Procedimento (R$)",
            color_continuous_scale=px.colors.sequential.Viridis
        )
        fig_fat.update_layout(xaxis_title="Procedimento", yaxis_title="Faturamento (R$)")
        st.plotly_chart(fig_fat, use_container_width=True)
    else:
        st.info("Nenhum procedimento registrado neste mês.")