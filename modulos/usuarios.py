import streamlit as st
from database import executar_query

def render():

    # =====================================
    # TÍTULO DA PÁGINA
    # =====================================
    st.header("👥 Gerenciar Usuários")

    # =====================================
    # PESQUISA DE USUÁRIOS
    # =====================================
    pesquisa = st.text_input("🔎 Pesquisar por nome ou email")

    # ===========================
    # BUSCA DE USUÁRIOS NO BANCO
    # ===========================
    if pesquisa:
        # Filtra pelo nome ou email
        usuarios = executar_query("""
            SELECT id, nome, email, nivel, ativo
            FROM usuarios
            WHERE nome LIKE %s OR email LIKE %s
            ORDER BY nome
        """, (f"%{pesquisa}%", f"%{pesquisa}%"), fetch=True)
    else:
        # Lista todos
        usuarios = executar_query("""
            SELECT id, nome, email, nivel, ativo
            FROM usuarios
            ORDER BY nome
        """, fetch=True)

    # =====================================
    # BOTÃO DE NOVO USUÁRIO (apenas admin)
    # =====================================
    if st.session_state.get("nivel") == "admin":
        with st.expander("➕ Novo Usuário"):
            with st.form("form_novo_usuario", clear_on_submit=True):
                novo_nome = st.text_input("Nome")
                novo_email = st.text_input("Email")
                nova_senha = st.text_input("Senha", type="password")
                novo_nivel = st.selectbox("Nível", ["admin", "atendente"])
                novo_ativo = st.checkbox("Usuário Ativo", value=True)

                salvar = st.form_submit_button("Salvar Usuário")
                if salvar:
                    if not novo_nome or not novo_email or not nova_senha:
                        st.error("Nome, Email e Senha são obrigatórios.")
                    else:
                        executar_query("""
                            INSERT INTO usuarios (nome, email, senha, nivel, ativo)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (novo_nome, novo_email, nova_senha, novo_nivel, int(novo_ativo)))
                        st.success("✅ Usuário cadastrado com sucesso!")
                        st.rerun()

    st.divider()

    # =====================================
    # LISTAGEM DE USUÁRIOS
    # =====================================
    if not usuarios:
        st.info("Nenhum usuário encontrado.")
        return

    for usuario in usuarios:
        id_usuario, nome, email, nivel, ativo = usuario

        with st.container():
            # Colunas para informações + editar + excluir
            col1, col2, col3 = st.columns([4, 1, 1])

            # ---------------------------
            # COLUNA 1 - INFORMAÇÕES
            # ---------------------------
            with col1:
                st.write(f"**{nome}** ({nivel})")
                st.write(f"📧 {email}")
                status = "Ativo ✅" if ativo else "Inativo 🚫"
                st.caption(f"Status: {status}")

            # ---------------------------
            # COLUNA 2 - EDITAR (apenas admin)
            # ---------------------------
            if st.session_state.get("nivel") == "admin":
                with col2:
                    if st.button("✏", key=f"editar_{id_usuario}"):
                        st.session_state["editar_usuario"] = id_usuario
                        st.rerun()

            # ---------------------------
            # COLUNA 3 - EXCLUIR / ATIVAR/INATIVAR
            # ---------------------------
            with col3:
                if st.session_state.get("nivel") == "admin":
                    # Ativar/Inativar
                    if ativo:
                        if st.button("🚫", key=f"inativar_{id_usuario}"):
                            executar_query("""
                                UPDATE usuarios
                                SET ativo = 0
                                WHERE id = %s
                            """, (id_usuario,))
                            st.success("Usuário inativado.")
                            st.rerun()
                    else:
                        if st.button("✅", key=f"ativar_{id_usuario}"):
                            executar_query("""
                                UPDATE usuarios
                                SET ativo = 1
                                WHERE id = %s
                            """, (id_usuario,))
                            st.success("Usuário ativado.")
                            st.rerun()

                    # Botão excluir
                    if st.button("🗑", key=f"excluir_{id_usuario}"):
                        executar_query("DELETE FROM usuarios WHERE id = %s", (id_usuario,))
                        st.success("Usuário excluído.")
                        st.rerun()

        st.divider()

    # =====================================
    # FORMULÁRIO DE EDIÇÃO
    # =====================================
    if "editar_usuario" in st.session_state:
        id_editar = st.session_state["editar_usuario"]

        # Busca dados atuais
        usuario = executar_query("""
            SELECT nome, email, senha, nivel, ativo
            FROM usuarios
            WHERE id = %s
        """, (id_editar,), fetch=True)

        if usuario:
            nome_atual, email_atual, senha_atual, nivel_atual, ativo_atual = usuario[0]

            st.subheader("✏ Editar Usuário")

            # Campos de edição com chave única para evitar conflito de IDs
            novo_nome = st.text_input("Nome", value=nome_atual, key=f"nome_{id_editar}")
            novo_email = st.text_input("Email", value=email_atual, key=f"email_{id_editar}")
            nova_senha = st.text_input("Senha", value=senha_atual, type="password", key=f"senha_{id_editar}")
            novo_nivel = st.selectbox("Nível", ["admin", "atendente"], index=0 if nivel_atual=="admin" else 1, key=f"nivel_{id_editar}")
            novo_ativo = st.checkbox("Usuário Ativo", value=bool(ativo_atual), key=f"ativo_{id_editar}")

            col1, col2 = st.columns(2)

            # ---------------------------
            # SALVAR ALTERAÇÕES
            # ---------------------------
            with col1:
                if st.button("Salvar Alterações", key=f"salvar_{id_editar}"):
                    executar_query("""
                        UPDATE usuarios
                        SET nome=%s, email=%s, senha=%s, nivel=%s, ativo=%s
                        WHERE id=%s
                    """, (novo_nome, novo_email, nova_senha, novo_nivel, int(novo_ativo), id_editar))
                    st.success("✅ Usuário atualizado com sucesso!")
                    del st.session_state["editar_usuario"]
                    st.rerun()

            # ---------------------------
            # CANCELAR EDIÇÃO
            # ---------------------------
            with col2:
                if st.button("Cancelar", key=f"cancelar_{id_editar}"):
                    del st.session_state["editar_usuario"]
                    st.rerun()