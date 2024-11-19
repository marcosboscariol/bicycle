import streamlit as st
from modules.login.login_service import login


def show_login():
    st.title('Login')

    username = st.text_input('Usuário')
    password = st.text_input(
        label='Senha', type='password'
    )

    if st.button('Login'):
        login(
            username=username,
            password=password
        )


show_login()
