# =====================================================
# IMPORTAÇÕES
# =====================================================
# streamlit -> biblioteca principal da interface
# executar_query -> função personalizada para executar SQL no banco
import streamlit as st
from database import executar_query


# =====================================================
# FUNÇÃO PRINCIPAL DA PÁGINA
# =====================================================
def render():

    # =====================================================
    # TÍTULO DA PÁGINA
    # =====================================================
    st.title("💄 Procedimentos")

    # Linha visual separadora
    st.divider()

    # =====================================================
    # FORMULÁRIO - CADASTRO DE NOVO PROCEDIMENTO
    # =====================================================
    # Expander permite esconder/mostrar o formulário
    with st.expander("➕ Novo Procedimento"):

        # Campo texto para nome do procedimento
        nome = st.text_input("Nome")

        # Campo numérico para valor
        # min_value evita número negativo
        # format força duas casas decimais
        valor = st.number_input(
            "Valor (R$)",
            min_value=0.0,
            format="%.2f"
        )

        # Campo duração em minutos
        duracao = st.number_input(
            "Duração (minutos)",
            min_value=0,
            step=10
        )

        # Campo descrição (área de texto grande)
        descricao = st.text_area("Descrição")

        # Checkbox define se o procedimento já nasce ativo
        ativo = st.checkbox("Procedimento Ativo", value=True)

        # Botão salvar
        if st.button("Salvar Procedimento"):

            # Validação básica
            if nome and valor > 0:

                # Inserção no banco
                executar_query("""
                    INSERT INTO procedimentos 
                    (nome, valor, duracao, descricao, ativo)
                    VALUES (%s, %s, %s, %s, %s)
                """, (nome, valor, duracao, descricao, int(ativo)))

                st.success("Procedimento cadastrado com sucesso!")

                # Atualiza a tela
                st.rerun()

            else:
                st.warning("Preencha nome e valor corretamente.")

    st.divider()

    # =====================================================
    # LISTAGEM DE PROCEDIMENTOS CADASTRADOS
    # =====================================================
    st.subheader("📋 Procedimentos Cadastrados")
    # =====================================================
    # CAMPO DE BUSCA
    # =====================================================
    # Campo para pesquisar por nome do procedimento
    busca = st.text_input(
        "🔎 Buscar procedimento pelo nome",
        placeholder="Digite parte do nome..."
    )

    # Busca todos os procedimentos no banco
    # Se o usuário digitou algo na busca
    if busca:

        procedimentos = executar_query(
            """
            SELECT id, nome, valor, duracao, descricao, ativo 
            FROM procedimentos 
            WHERE nome LIKE %s
            ORDER BY nome
            """,
            (f"%{busca}%",),
            fetch=True
        )

    else:
        # Se não digitou nada → mostra todos
        procedimentos = executar_query(
            """
            SELECT id, nome, valor, duracao, descricao, ativo 
            FROM procedimentos 
            ORDER BY nome
            """,
            fetch=True
        )

    # Se não houver registros
    if not procedimentos:
        st.info("Nenhum procedimento cadastrado.")
        return

    # =====================================================
    # LOOP PARA EXIBIR CADA PROCEDIMENTO
    # =====================================================
    for proc in procedimentos:

        # Desempacota tupla retornada do banco
        id_proc, nome, valor, duracao, descricao, ativo = proc

        # Container agrupa visualmente cada procedimento
        with st.container():

            # Criação de 3 colunas:
            # 1 -> Informações
            # 2 -> Botão editar
            # 3 -> Ativar / Inativar
            col1, col2, col3 = st.columns([4, 1, 1])

            # =====================================================
            # COLUNA 1 - INFORMAÇÕES DO PROCEDIMENTO
            # =====================================================
            with col1:

                # Nome em destaque
                st.write(f"**{nome}**")

                # Valor formatado
                st.write(f"💰 R$ {valor}")

                # Duração
                st.write(f"⏱ {duracao} min")

                # Status visual
                if ativo:
                    st.success("Status: Ativo")
                else:
                    st.error("Status: Inativo")

                # Exibe descrição se existir
                if descricao:
                    st.caption(descricao)

            # =====================================================
            # COLUNA 2 - BOTÃO EDITAR
            # =====================================================
            with col2:

                # Key única evita conflito interno do Streamlit
                if st.button("✏", key=f"edit_{id_proc}"):

                    # Guarda no session_state qual procedimento está sendo editado
                    st.session_state["editar_proc"] = id_proc

                    # Atualiza tela
                    st.rerun()

            # =====================================================
            # COLUNA 3 - ATIVAR / INATIVAR
            # =====================================================
            with col3:

                if ativo:
                    # Se ativo -> botão inativar
                    if st.button("🚫", key=f"inativar_{id_proc}"):

                        executar_query("""
                            UPDATE procedimentos
                            SET ativo = 0
                            WHERE id = %s
                        """, (id_proc,))

                        st.success("Procedimento inativado.")
                        st.rerun()

                else:
                    # Se inativo -> botão ativar
                    if st.button("✅", key=f"ativar_{id_proc}"):

                        executar_query("""
                            UPDATE procedimentos
                            SET ativo = 1
                            WHERE id = %s
                        """, (id_proc,))

                        st.success("Procedimento ativado.")
                        st.rerun()

        # =====================================================
        # FORMULÁRIO DE EDIÇÃO (APARECE LOGO ABAIXO)
        # =====================================================
        # Só aparece se o ID atual for o que está salvo no session_state
        if st.session_state.get("editar_proc") == id_proc:

            st.subheader("✏ Editar Procedimento")

            # Campos com keys únicas
            novo_nome = st.text_input(
                "Nome",
                value=nome,
                key=f"nome_{id_proc}"
            )

            novo_valor = st.number_input(
                "Valor (R$)",
                value=float(valor),
                format="%.2f",
                key=f"valor_{id_proc}"
            )

            nova_duracao = st.number_input(
                "Duração (minutos)",
                value=int(duracao),
                key=f"duracao_{id_proc}"
            )

            nova_descricao = st.text_area(
                "Descrição",
                value=descricao,
                key=f"descricao_{id_proc}"
            )

            novo_ativo = st.checkbox(
                "Procedimento Ativo",
                value=bool(ativo),
                key=f"ativo_{id_proc}"
            )

            col_edit1, col_edit2 = st.columns(2)

            # =====================================================
            # SALVAR ALTERAÇÕES
            # =====================================================
            with col_edit1:
                if st.button("Salvar Alterações", key=f"salvar_{id_proc}"):

                    executar_query("""
                        UPDATE procedimentos
                        SET nome = %s,
                            valor = %s,
                            duracao = %s,
                            descricao = %s,
                            ativo = %s
                        WHERE id = %s
                    """, (
                        novo_nome,
                        novo_valor,
                        nova_duracao,
                        nova_descricao,
                        int(novo_ativo),
                        id_proc
                    ))

                    st.success("Procedimento atualizado!")

                    # Remove controle de edição
                    del st.session_state["editar_proc"]

                    st.rerun()

            # =====================================================
            # CANCELAR EDIÇÃO
            # =====================================================
            with col_edit2:
                if st.button("Cancelar", key=f"cancelar_{id_proc}"):

                    # Remove controle de edição
                    del st.session_state["editar_proc"]

                    st.rerun()

        # Linha divisória entre procedimentos
        st.divider()