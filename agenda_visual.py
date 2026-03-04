# =====================================================
# IMPORTAÇÕES
# =====================================================
import streamlit as st
from database import executar_query
import datetime


# =====================================================
# FUNÇÃO PRINCIPAL
# =====================================================
def render():

    # =====================================================
    # TÍTULO
    # =====================================================
    st.title("📆 Agenda Profissional")

    # Seleção da data
    data_escolhida = st.date_input(
        "Selecione a data",
        value=datetime.date.today()
    )

    st.divider()

    # =====================================================
    # BUSCA AGENDAMENTOS DO DIA
    # =====================================================
    agendamentos = executar_query("""
        SELECT a.hora_agend, c.nome, p.nome, p.duracao
        FROM agendamentos a
        JOIN clientes c ON a.cliente_id = c.id
        JOIN procedimentos p ON a.procedimento_id = p.id
        WHERE a.data_agend = %s
        ORDER BY a.hora_agend
    """, (data_escolhida,), fetch=True)

    # =====================================================
    # CONVERTE RESULTADO PARA DICIONÁRIO SEGURO
    # Usa string HH:MM como chave para evitar erro de comparação
    # =====================================================
    agenda_dict = {}

    for ag in agendamentos:

        hora_db = ag[0]

        # Converte hora do banco para string HH:MM
        if isinstance(hora_db, datetime.timedelta):
            total_seconds = int(hora_db.total_seconds())
            hora = total_seconds // 3600
            minuto = (total_seconds % 3600) // 60
            hora_str = f"{hora:02d}:{minuto:02d}"
        else:
            hora_str = str(hora_db)[:5]

        agenda_dict[hora_str] = {
            "cliente": ag[1],
            "procedimento": ag[2],
            "duracao": ag[3]
        }

    # =====================================================
    # GERA HORÁRIOS PADRÃO DO DIA (07:00 até 22:00)
    # =====================================================
    horarios = []
    inicio = datetime.datetime.combine(data_escolhida, datetime.time(7, 0))
    fim = datetime.datetime.combine(data_escolhida, datetime.time(22, 0))

    atual = inicio

    while atual <= fim:
        horarios.append(atual.strftime("%H:%M"))
        atual += datetime.timedelta(minutes=30)

    # =====================================================
    # EXIBE EM FORMATO DE "CARDS"
    # =====================================================
    for horario in horarios:

        with st.container():

            # Cria 2 colunas: horário | conteúdo
            col1, col2 = st.columns([1, 4])

            # -----------------------------
            # COLUNA HORÁRIO
            # -----------------------------
            with col1:
                st.markdown(f"### 🕒 {horario}")

            # -----------------------------
            # COLUNA STATUS
            # -----------------------------
            with col2:

                if horario in agenda_dict:

                    dados = agenda_dict[horario]

                    # Card vermelho = ocupado
                    st.markdown(
                        f"""
                        <div style="
                            background-color:#2b1b1b;
                            padding:15px;
                            border-radius:10px;
                            border-left:6px solid #ff4b4b;
                        ">
                            <b>👤 Cliente:</b> {dados['cliente']}<br>
                            <b>💄 Procedimento:</b> {dados['procedimento']}<br>
                            <b>⏱ Duração:</b> {dados['duracao']} min
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                else:

                    # Card verde = disponível
                    st.markdown(
                        """
                        <div style="
                            background-color:#1e2b1e;
                            padding:15px;
                            border-radius:10px;
                            border-left:6px solid #00c853;
                        ">
                            Horário disponível
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        st.markdown("<br>", unsafe_allow_html=True)