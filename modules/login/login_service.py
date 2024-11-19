import streamlit as st


def login(username, password):
    if username != 'admin' or password != 'admin':
        st.error(f'Falha ao realizar o login do usuário {username}')
    else:
        st.session_state.username = username
        st.session_state.password = password
        st.rerun()
