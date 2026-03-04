# Importa o Streamlit (framework web)
import streamlit as st

# Importa módulo para trabalhar com datas e horários
import datetime

# Importa função personalizada que executa queries no banco
from database import executar_query


def render():

    # =====================================================
    # TÍTULO DA PÁGINA
    # =====================================================
    st.header("📅 Criar novo agendamento")

    # =====================================================
    # CARREGAR DADOS DO BANCO
    # =====================================================

    # Busca todos os clientes ordenados por nome
    # Retorna: id, nome e sobrenome
    clientes = executar_query(
        "SELECT id, nome, sobrenome FROM clientes ORDER BY nome",
        fetch=True  # fetch=True indica que queremos retorno da consulta
    )

    # Busca apenas procedimentos que estão ATIVOS
    # Isso evita que procedimentos inativos apareçam para agendamento
    procedimentos = executar_query(
        """
        SELECT id, nome, duracao 
        FROM procedimentos
        WHERE ativo = 1
        ORDER BY nome
        """,
        fetch=True
    )

    # =====================================================
    # PREPARAÇÃO DAS OPÇÕES PARA OS SELECTBOX
    # =====================================================

    # Monta lista de opções de clientes
    # Inclui opção padrão e opção para criar novo cliente
    clientes_options = ["-- Selecione um cliente --", "➕ Novo cliente"] + [
        # Formata cada cliente como:
        # Nome Sobrenome (ID X)
        f"{c[1]} {c[2]} (ID {c[0]})" for c in clientes
    ]

    # Monta lista de opções de procedimentos
    # Formato: Nome - duração min (ID X)
    procedimentos_options = [
        f"{p[1]} - {p[2]} min (ID {p[0]})"
        for p in procedimentos
    ]

    # =====================================================
    # SELECT DE CLIENTE
    # =====================================================

    # Selectbox para escolher cliente
    cliente_selecionado = st.selectbox(
        "Cliente",
        clientes_options
    )

    # =====================================================
    # FORMULÁRIO PARA NOVO CLIENTE
    # =====================================================

    # Se o usuário escolher "Novo cliente"
    if cliente_selecionado == "➕ Novo cliente":

        st.subheader("👤 Cadastrar novo cliente")

        # Cria formulário separado
        # clear_on_submit limpa os campos após salvar
        with st.form("form_novo_cliente", clear_on_submit=True):

            # Campos do cliente
            nome = st.text_input("Nome")
            sobrenome = st.text_input("Sobrenome")
            telefone = st.text_input("Telefone")

            # Campo de data de nascimento
            # Define limite mínimo e máximo permitido
            data_nasc = st.date_input(
                "Data de nascimento",
                min_value=datetime.date(1900, 1, 1),
                max_value=datetime.date.today()
            )

            endereco = st.text_input("Endereço")
            bairro = st.text_input("Bairro")
            numero = st.text_input("Número")
            cidade = st.text_input("Cidade")
            estado = st.text_input("Estado")

            # Botão de salvar cliente
            salvar_novo = st.form_submit_button("Salvar cliente")

            # =====================================================
            # PROCESSAMENTO DO NOVO CLIENTE
            # =====================================================
            if salvar_novo:

                # Validação básica
                if nome.strip() == "" or sobrenome.strip() == "":
                    st.error("Nome e sobrenome são obrigatórios.")
                else:
                    # Insere novo cliente no banco
                    executar_query("""
                        INSERT INTO clientes (
                            nome, sobrenome, telefone, data_nascimento,
                            endereco, bairro, numero, cidade, estado
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        nome, sobrenome, telefone, data_nasc,
                        endereco, bairro, numero, cidade, estado
                    ))

                    st.success("Cliente cadastrado com sucesso!")

                    # Atualiza tela para novo cliente aparecer na lista
                    st.rerun()

        st.divider()

    # =====================================================
    # FORMULÁRIO PRINCIPAL DE AGENDAMENTO
    # =====================================================
    with st.form("form_agendamento", clear_on_submit=True):

        # Campo para selecionar data
        # Não permite datas anteriores a hoje
        data_agendamento = st.date_input(
            "Data do agendamento",
            value=datetime.date.today(),
            min_value=datetime.date.today()
        )

        # =====================================================
        # GERAÇÃO AUTOMÁTICA DOS HORÁRIOS
        # =====================================================

        lista_horarios = []

        # Define horário inicial (07:00)
        inicio = datetime.datetime.combine(
            data_agendamento,
            datetime.time(7, 0)
        )

        # Define horário final (22:00)
        fim = datetime.datetime.combine(
            data_agendamento,
            datetime.time(22, 0)
        )

        # Cria horários de 30 em 30 minutos
        atual = inicio
        while atual <= fim:
            lista_horarios.append(atual.time())
            atual += datetime.timedelta(minutes=30)

        # Selectbox com formatação de hora
        horario_agendamento = st.selectbox(
            "Horário",
            lista_horarios,
            format_func=lambda t: t.strftime("%H:%M")
        )

        # Selectbox para escolher procedimento
        procedimento_selecionado = st.selectbox(
            "Procedimento",
            procedimentos_options
        )

        # Botão salvar agendamento
        salvar = st.form_submit_button("Salvar agendamento")

    # =====================================================
    # PROCESSAMENTO DO AGENDAMENTO
    # =====================================================
    if salvar:

        # Data e hora atual
        agora = datetime.datetime.now()

        # Combina data escolhida + horário escolhido
        escolhido_datetime = datetime.datetime.combine(
            data_agendamento,
            horario_agendamento
        )

        # Impede agendamento no passado
        if escolhido_datetime < agora:
            st.error("❌ Horário inválido.")
            return

        # Impede salvar sem cliente válido
        if cliente_selecionado in [
            "-- Selecione um cliente --",
            "➕ Novo cliente"
        ]:
            st.error("❌ Selecione um cliente válido.")
            return

        try:
            # Extrai ID do cliente do texto selecionado
            cliente_id = int(
                cliente_selecionado.split("ID ")[1].strip(")")
            )

            # Extrai ID do procedimento
            proc_id = int(
                procedimento_selecionado.split("ID ")[1].strip(")")
            )

            # Busca duração do procedimento
            duracao = next(
                p[2] for p in procedimentos if p[0] == proc_id
            )

            # Calcula horário final do agendamento
            fim_agendamento = escolhido_datetime + datetime.timedelta(
                minutes=duracao
            )

            # =====================================================
            # VERIFICAÇÃO DE CONFLITO DE HORÁRIO
            # =====================================================

            # Busca todos agendamentos do mesmo dia
            agendamentos_existentes = executar_query("""
                SELECT a.data_agend, a.hora_agend, p.duracao
                FROM agendamentos a
                JOIN procedimentos p ON a.procedimento_id = p.id
                WHERE a.data_agend = %s
            """, (data_agendamento,), fetch=True)

            # Percorre cada agendamento existente
            for (a_data, a_hora, a_dur) in agendamentos_existentes:

                # Converte TIME do MySQL para horas/minutos
                total = a_hora.total_seconds()
                hora_int = int(total // 3600)
                minuto_int = int((total % 3600) // 60)

                # Define início do agendamento já existente
                inicio_exist = datetime.datetime.combine(
                    a_data,
                    datetime.time(hora_int, minuto_int)
                )

                # Calcula fim do agendamento já existente
                fim_exist = inicio_exist + datetime.timedelta(
                    minutes=a_dur
                )

                # Verifica sobreposição de horário
                if (escolhido_datetime < fim_exist) and \
                   (fim_agendamento > inicio_exist):

                    st.error("❌ Já existe agendamento nesse período.")
                    return

            # =====================================================
            # INSERE AGENDAMENTO NO BANCO
            # =====================================================
            executar_query("""
                INSERT INTO agendamentos
                (cliente_id, procedimento_id, data_agend, hora_agend)
                VALUES (%s, %s, %s, %s)
            """, (
                cliente_id,
                proc_id,
                data_agendamento,
                horario_agendamento
            ))

            st.success("✅ Agendamento salvo com sucesso!")

        except Exception as e:
            # Captura qualquer erro inesperado
            st.error(f"Erro ao salvar: {e}")