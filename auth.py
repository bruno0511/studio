import streamlit as st
from database import executar_query, get_connection

# =========================
# FUNÇÃO DE VALIDAÇÃO DE LOGIN
# =========================
def validar_login_db(email, senha):
    """Valida o login no banco de dados"""
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT id, nome, nivel 
        FROM usuarios 
        WHERE email = %s AND senha = %s
    """
    cursor.execute(query, (email, senha))
    resultado = cursor.fetchone()
    cursor.close()
    conn.close()
    return resultado  # retorna None se inválido ou tupla (id, nome, nivel)

# =========================
# INICIALIZAÇÃO DE SESSÃO
# =========================
def inicializar_sessao():
    """Cria variáveis de sessão se não existirem"""
    if "logado" not in st.session_state:
        st.session_state["logado"] = False
    if "usuario_id" not in st.session_state:
        st.session_state["usuario_id"] = None
    if "usuario_nome" not in st.session_state:
        st.session_state["usuario_nome"] = None
    if "nivel" not in st.session_state:
        st.session_state["nivel"] = None

# =========================
# TELA DE LOGIN MODERNA
# =========================
def tela_login():
    """Exibe a tela de login estilizada"""
    st.markdown(
        """
        <style>
        .login-container {
            background: linear-gradient(135deg, #f48fb1, #ce93d8);
            padding: 40px;
            border-radius: 15px;
            color: white;
            max-width: 450px;
            margin: auto;
        }
        .login-title {
            font-size: 36px;
            font-weight: bold;
            text-align: center;
        }
        .login-input input {
            border-radius: 8px;
            padding: 8px;
        }
        .login-btn button {
            background-color: #ff4081;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            width: 100%;
            padding: 10px;
        }
        </style>
        """, unsafe_allow_html=True
    )

    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">🎀 Tamires Studio</div>', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)

    email = st.text_input("📧 Email")
    senha = st.text_input("🔒 Senha", type="password")

    if st.button("Entrar", key="login_btn"):
        usuario = validar_login_db(email, senha)
        if usuario:
            st.session_state["logado"] = True
            st.session_state["usuario_id"] = usuario[0]
            st.session_state["usuario_nome"] = usuario[1]
            st.session_state["nivel"] = usuario[2]  # salva nível
            st.success("Login realizado com sucesso!")
            st.rerun()
        else:
            st.error("Email ou senha inválidos.")

    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# LOGOUT
# =========================
def logout():
    """Limpa a sessão e força rerun"""
    st.session_state["logado"] = False
    st.session_state["usuario_id"] = None
    st.session_state["usuario_nome"] = None
    st.session_state["nivel"] = None
    st.rerun()

# =========================
# VERIFICA LOGIN
# =========================
def verificar_login():
    """Verifica se o usuário está logado, senão exibe login"""
    inicializar_sessao()
    if not st.session_state["logado"]:
        tela_login()
        st.stop()