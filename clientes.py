import streamlit as st
from database import executar_query

def render():

    # =====================================================
    # TÍTULO DA PÁGINA
    # =====================================================
    st.header("👥 Gerenciar Clientes")

    # =====================================================
    # CAMPO DE PESQUISA
    # Permite pesquisar por nome ou sobrenome
    # =====================================================
    pesquisa = st.text_input("🔎 Pesquisar cliente por nome")

    # =====================================================
    # BUSCA NO BANCO DE DADOS
    # =====================================================
    if pesquisa:
        # Se digitou algo, filtra usando LIKE
        clientes = executar_query("""
            SELECT id, nome, sobrenome, telefone
            FROM clientes
            WHERE nome LIKE %s OR sobrenome LIKE %s
            ORDER BY nome
        """, (f"%{pesquisa}%", f"%{pesquisa}%"), fetch=True)
    else:
        # Se não digitou nada, lista todos
        clientes = executar_query("""
            SELECT id, nome, sobrenome, telefone
            FROM clientes
            ORDER BY nome
        """, fetch=True)

    # =====================================================
    # LISTAGEM DOS CLIENTES
    # =====================================================
    for cliente in clientes:

        # Desempacota os dados vindos do banco
        id_cliente, nome, sobrenome, telefone = cliente

        # Cria 3 colunas:
        # 1 - Nome
        # 2 - Botão editar
        # 3 - Botão deletar
        col1, col2, col3 = st.columns([4,1,1])

        # Mostra nome e telefone
        col1.write(f"{nome} {sobrenome} - 📞 {telefone}")

        # =====================================================
        # BOTÃO EDITAR
        # Salva o ID na session_state para abrir o formulário
        # =====================================================
        if col2.button("✏️", key=f"editar_{id_cliente}"):
            st.session_state["editar_cliente"] = id_cliente
            st.rerun()

        # =====================================================
        # BOTÃO DELETAR
        # Antes de deletar verifica se existe agendamento
        # =====================================================
        if col3.button("🗑", key=f"deletar_{id_cliente}"):

            try:
                # Verifica se existe agendamento vinculado
                agendamentos = executar_query("""
                    SELECT id
                    FROM agendamentos
                    WHERE cliente_id = %s
                """, (id_cliente,), fetch=True)

                # Se existir agendamento → bloqueia exclusão
                if agendamentos:
                    st.error(
                        "❌ Não é possível excluir este cliente, "
                        "pois ele possui agendamento(s) vinculado(s).\n"
                        "Exclua primeiro os agendamentos deste cliente."
                    )

                else:
                    # Se não existir vínculo → pode deletar
                    executar_query(
                        "DELETE FROM clientes WHERE id = %s",
                        (id_cliente,)
                    )

                    st.success("✅ Cliente deletado com sucesso.")
                    st.rerun()

            except Exception as e:
                # Captura qualquer erro inesperado
                st.error(f"Erro ao excluir cliente: {e}")

    # =====================================================
    # FORMULÁRIO DE EDIÇÃO (FORA DO FOR)
    # Só aparece se existir cliente selecionado
    # =====================================================
    if "editar_cliente" in st.session_state:

        id_editar = st.session_state["editar_cliente"]

        st.divider()
        st.subheader("✏️ Editar Cliente")

        # Busca todos os dados do cliente
        cliente = executar_query("""
            SELECT nome, sobrenome, telefone,
                   data_nascimento, endereco,
                   bairro, numero, cidade, estado
            FROM clientes
            WHERE id = %s
        """, (id_editar,), fetch=True)

        # Verifica se encontrou o cliente
        if cliente:

            dados = cliente[0]

            # Formulário de edição
            with st.form("form_editar_cliente"):

                # Campos já preenchidos com dados atuais
                nome = st.text_input("Nome", value=dados[0])
                sobrenome = st.text_input("Sobrenome", value=dados[1])
                telefone = st.text_input("Telefone", value=dados[2])
                data_nasc = st.date_input("Data de nascimento", value=dados[3])
                endereco = st.text_input("Endereço", value=dados[4])
                bairro = st.text_input("Bairro", value=dados[5])
                numero = st.text_input("Número", value=dados[6])
                cidade = st.text_input("Cidade", value=dados[7])
                estado = st.text_input("Estado", value=dados[8])

                # Botões do formulário
                salvar = st.form_submit_button("Salvar Alterações")
                cancelar = st.form_submit_button("Cancelar")

                # =====================================================
                # SALVAR ALTERAÇÕES
                # =====================================================
                if salvar:

                    executar_query("""
                        UPDATE clientes
                        SET nome = %s,
                            sobrenome = %s,
                            telefone = %s,
                            data_nascimento = %s,
                            endereco = %s,
                            bairro = %s,
                            numero = %s,
                            cidade = %s,
                            estado = %s
                        WHERE id = %s
                    """, (
                        nome, sobrenome, telefone, data_nasc,
                        endereco, bairro, numero, cidade, estado,
                        id_editar
                    ))

                    st.success("✅ Cliente atualizado com sucesso!")

                    # Remove da sessão para fechar formulário
                    del st.session_state["editar_cliente"]

                    st.rerun()

                # =====================================================
                # CANCELAR EDIÇÃO
                # =====================================================
                if cancelar:
                    del st.session_state["editar_cliente"]
                    st.rerun()