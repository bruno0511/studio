import streamlit as st
import datetime
from modulos import (
    clientes, procedimentos, agendamentos, criar_agendamento,
    dashboard, relatorios, agenda_visual, usuarios
)
import auth
import plotly.express as px
from database import executar_query

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="Studio Manager",
    page_icon="💄",
    layout="wide"
)

# =========================
# VERIFICA LOGIN
# =========================
auth.verificar_login()  # se não estiver logado, exibe tela de login

# =========================
# PEGAR NÍVEL DO USUÁRIO
# =========================
nivel_usuario = st.session_state.get("nivel", "atendente")

# =========================
# CABEÇALHO MODERNO
# =========================
st.markdown(
    f"""
    <div style="background-color:#f48fb1; padding:20px; border-radius:10px; color:white;">
        <h1 style="margin:0;">💄 Studio Manager</h1>
        <p style="margin:0;">Usuário: {st.session_state.get('usuario_nome','')} ({nivel_usuario})</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Botão de logout
if st.button("🚪 Sair"):
    auth.logout()

st.markdown("<br>", unsafe_allow_html=True)

# =========================
# MENU RESPONSIVO EM CARDS
# =========================
menu_icons = {
    "Dashboard": "📊",
    "Agendamentos": "📅",
    "Criar Agendamento": "➕",
    "Clientes": "👥",
    "Procedimentos": "💄",
    "Relatórios": "📈",
    "Agenda Visual": "🗓",
    "Usuários": "👤"
}

# Menu por nível de acesso
if nivel_usuario == "admin":
    menu = [
        "Dashboard","Agendamentos","Criar Agendamento","Clientes",
        "Procedimentos","Relatórios","Agenda Visual","Usuários"
    ]
else:
    menu = ["Agendamentos","Criar Agendamento","Clientes","Procedimentos","Agenda Visual"]

# Layout responsivo: cards horizontais
colunas = st.columns(len(menu))
escolha = None

for idx, item in enumerate(menu):
    with colunas[idx]:
        cor_card = "#f06292" if item in ["Dashboard","Clientes","Procedimentos"] else "#81d4fa"
        if st.button(f"{menu_icons.get(item,'')} {item}", key=f"menu_{idx}"):
            escolha = item

# Seleção padrão caso não clique em nenhum
if escolha is None:
    escolha = menu[0]

# =========================
# ROTEAMENTO
# =========================
if escolha == "Dashboard":
    # =========================
    # DASHBOARD COMPLETO COM LEMBRETES E GRÁFICOS
    # =========================
    st.header("📊 Dashboard")

    hoje = datetime.date.today()
    primeiro_dia_mes = hoje.replace(day=1)

    # -------------------------
    # LEMBRETES DO DIA
    # -------------------------
    agendamentos_hoje = executar_query("""
        SELECT a.hora_agend, c.nome, c.sobrenome, p.nome
        FROM agendamentos a
        JOIN clientes c ON a.cliente_id = c.id
        JOIN procedimentos p ON a.procedimento_id = p.id
        WHERE a.data_agend = %s
        ORDER BY a.hora_agend
    """, (hoje,), fetch=True)

    if agendamentos_hoje:
        st.subheader("🔔 Agendamentos de Hoje")
        for hora, nome_cliente, sobrenome_cliente, proc in agendamentos_hoje:
            # CONVERSÃO DO TIME / timedelta PARA HORA:MINUTO
            total_segundos = hora.total_seconds()
            horas = int(total_segundos // 3600)
            minutos = int((total_segundos % 3600) // 60)
            hora_formatada = f"{horas:02d}:{minutos:02d}"

            st.markdown(f"- ⏰ {hora_formatada} → **{nome_cliente} {sobrenome_cliente}** ({proc})")
    else:
        st.info("Nenhum agendamento para hoje.")

    st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------
    # MÉTRICAS DO MÊS
    # -------------------------
    total_agend = executar_query("""
        SELECT COUNT(*) FROM agendamentos WHERE data_agend >= %s
    """, (primeiro_dia_mes,), fetch=True)[0][0]

    faturamento = executar_query("""
        SELECT SUM(p.valor)
        FROM agendamentos a
        JOIN procedimentos p ON a.procedimento_id = p.id
        WHERE a.data_agend >= %s
    """, (primeiro_dia_mes,), fetch=True)[0][0] or 0

    mais_vendido = executar_query("""
        SELECT p.nome, COUNT(*) as total
        FROM agendamentos a
        JOIN procedimentos p ON a.procedimento_id = p.id
        GROUP BY p.nome
        ORDER BY total DESC
        LIMIT 1
    """, fetch=True)

    # Cards coloridos
    col1, col2, col3 = st.columns(3)
    col1.metric("Agendamentos no mês", total_agend)
    col2.metric("Faturamento no mês", f"R$ {faturamento:.2f}")
    if mais_vendido:
        col3.metric("Mais vendido", mais_vendido[0][0])
    else:
        col3.metric("Mais vendido", "Nenhum")

    # -------------------------
    # GRÁFICOS INTERATIVOS
    # -------------------------
    # Faturamento por dia do mês
    dados_faturamento = executar_query("""
        SELECT data_agend, SUM(p.valor) 
        FROM agendamentos a
        JOIN procedimentos p ON a.procedimento_id = p.id
        WHERE data_agend >= %s
        GROUP BY data_agend
        ORDER BY data_agend
    """, (primeiro_dia_mes,), fetch=True)

    if dados_faturamento:
        datas = [d[0] for d in dados_faturamento]
        valores = [float(d[1]) for d in dados_faturamento]
        df_fat = {"Data": datas, "Faturamento": valores}
        fig_fat = px.bar(df_fat, x="Data", y="Faturamento", title="Faturamento do mês", color="Faturamento",
                         color_continuous_scale="pinkyl", text="Faturamento")
        st.plotly_chart(fig_fat, use_container_width=True)

elif escolha == "Agendamentos":
    agendamentos.render()
elif escolha == "Criar Agendamento":
    criar_agendamento.render()
elif escolha == "Clientes":
    clientes.render()
elif escolha == "Procedimentos":
    procedimentos.render()
elif escolha == "Relatórios":
    relatorios.render()
elif escolha == "Agenda Visual":
    agenda_visual.render()
elif escolha == "Usuários" and nivel_usuario == "admin":
    usuarios.render()