import streamlit as st
from modules.login.page_login import show_login
st.set_page_config(layout="wide")


indicadores_producao_page = st.Page(
    "modules/indicadores_producao/page_indicadores_producao.py",
    title="Indicadores de Produção",
    icon='⚙️'
)
indicadores_venda_page = st.Page(
    "modules/indicadores_venda/page_indicadores_venda.py",
    title="Indicadores de Vendas",
    icon='🪙'
)
login_page = st.Page(
    "modules/login/page_login.py",
    title="Login",
    icon='🔑'
)
informacoes_page = st.Page(
    "modules/informacoes/page_informacoes.py",
    title="Informações",
    icon='📒'
)


if 'username' not in st.session_state:
    st.session_state.username = None

if 'password' not in st.session_state:
    st.session_state.password = None


def main():
    modules = {
        'Login': [login_page, informacoes_page],
        'Indicadores': [indicadores_producao_page, indicadores_venda_page]
    }

    if st.session_state.username == 'admin':
        modules.pop('Login')
    else:
        modules.pop('Indicadores')

    pg = st.navigation(modules)
    pg.run()


if __name__ == '__main__':
    main()
