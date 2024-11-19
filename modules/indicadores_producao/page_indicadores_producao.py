import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px  # Importando Plotly Express
import cohere
# Usado para prever a produção de 2025
from sklearn.linear_model import LinearRegression

# Substitua 'your-cohere-api-key' pela sua chave de API da Cohere
cohere_client = cohere.Client('Sid93B0NN5Vc3luKBnbaD07IYTj93V1HGix5nDEe')

# Geração de dados fictícios
np.random.seed(42)  # Para resultados reproduzíveis
anos = [2022, 2023, 2024]
meses = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]
dados = []

for ano in anos:
    for mes in meses:
        dados.append({
            "Ano": ano,
            "Mês": mes,
            "Mês/Ano": f"{mes[:3]}/{ano}",  # Abreviação do mês para o eixo X
            "Bicicleta A": np.random.randint(500, 1500),
            "Bicicleta B": np.random.randint(300, 1200)
        })

# Transformar os dados em um DataFrame
df = pd.DataFrame(dados)

# Inicializar o histórico de perguntas e respostas no session_state, se ainda não existir
if "historico" not in st.session_state:
    st.session_state.historico = []

# Interface do usuário
st.title("Produção Mensal de Bicicletas - Gráfico Interativo")
st.sidebar.header("Configurações do Gráfico")

# Filtro de ano com múltiplas seleções no dropdown
anos_selecionados = st.sidebar.multiselect(
    "Selecione os anos",
    options=anos,
    default=anos  # Seleciona todos os anos por padrão
)

# Filtrar os dados
df_filtrado = df[df["Ano"].isin(anos_selecionados)]

# Gráfico interativo com Plotly
st.subheader("Produção Mensal Fictícia")

# Reshape dos dados para Plotly (long format)
df_long = df_filtrado.melt(
    id_vars=["Mês/Ano", "Ano", "Mês"],
    value_vars=["Bicicleta A", "Bicicleta B"],
    var_name="Tipo de Bicicleta",
    value_name="Produção"
)

# Criar o gráfico de linhas
fig = px.line(
    df_long,
    x="Mês/Ano",
    y="Produção",
    color="Tipo de Bicicleta",
    markers=True,
    hover_data={
        "Mês/Ano": True,
        "Produção": True,
        "Tipo de Bicicleta": True,
        "Ano": True,
        "Mês": True
    },
    title=f"Produção Mensal de Bicicletas - Anos Selecionados"
)

# Personalizar fontes e linhas
fig.update_traces(line=dict(width=4))  # Linhas mais grossas
fig.update_layout(
    xaxis_title="Mês/Ano",
    yaxis_title="Produção",
    legend_title="Tipo de Bicicleta",
    xaxis_tickangle=-45,
    template="plotly_white",
    font=dict(size=16),  # Aumenta o tamanho da fonte geral
    title=dict(font=dict(size=24)),  # Tamanho maior para o título
    legend=dict(font=dict(size=16)),  # Tamanho maior para a legenda
    xaxis=dict(
        tickfont=dict(size=14)  # Aumenta a fonte dos valores do eixo X
    ),
    yaxis=dict(
        tickfont=dict(size=14)  # Aumenta a fonte dos valores do eixo Y
    )
)

# Exibir o gráfico no Streamlit
st.plotly_chart(fig, use_container_width=True)

# Adicionar um campo de pergunta
st.subheader("Pergunte sobre os dados de produção")

pergunta_usuario = st.text_input("Digite sua pergunta:")

if st.button("Obter resposta"):
    if pergunta_usuario:
        # Gerar a resposta usando a Cohere API
        prompt = (
            f"Considere os seguintes dados de produção de bicicletas:\n\n"
            f"{df.to_string(index=False)}\n\n"
            f"Agora, responda à seguinte pergunta sobre os dados:\n"
            f"{pergunta_usuario}"
        )

        # Gerar a resposta com a Cohere
        try:
            response = cohere_client.generate(
                model='command-xlarge-nightly',  # Use o modelo apropriado
                prompt=prompt,
                max_tokens=150,
                temperature=0.7
            )
            resposta = response.generations[0].text.strip()

            # Adicionar pergunta e resposta ao histórico
            st.session_state.historico.append(
                {"pergunta": pergunta_usuario, "resposta": resposta})

            # Exibir a resposta gerada
            st.write("Resposta da IA:")
            st.write(resposta)

            # Se a resposta indicar uma previsão para 2025, gerar gráfico
            if "previsão" in resposta.lower() or "2025" in resposta:
                st.write("Gerando gráfico de previsão para 2025...")

                # Criação de dados de previsão (exemplo simples de regressão linear)
                # Usaremos a produção dos anos anteriores para prever 2025
                df_previsao = df_filtrado[df_filtrado["Ano"] < 2025]

                # Preparando os dados para regressão linear
                # Ano como variável explicativa
                X = np.array(df_previsao["Ano"]).reshape(-1, 1)
                y_a = df_previsao[df_previsao["Tipo de Bicicleta"]
                                  == "Bicicleta A"]["Produção"].values
                y_b = df_previsao[df_previsao["Tipo de Bicicleta"]
                                  == "Bicicleta B"]["Produção"].values

                # Modelo de regressão linear
                modelo_a = LinearRegression()
                modelo_b = LinearRegression()

                modelo_a.fit(X, y_a)
                modelo_b.fit(X, y_b)

                # Prevendo a produção para 2025
                previsao_a = modelo_a.predict([[2025]])[0]
                previsao_b = modelo_b.predict([[2025]])[0]

                # Adicionando a previsão ao gráfico
                df_previsao_2025 = pd.DataFrame({
                    "Ano": [2025, 2025],
                    "Mês/Ano": ["Jan/2025", "Jan/2025"],
                    "Produção": [previsao_a, previsao_b],
                    "Tipo de Bicicleta": ["Bicicleta A", "Bicicleta B"]
                })

                df_long = pd.concat([df_long, df_previsao_2025])

                # Novo gráfico com a previsão
                fig_previsao = px.line(
                    df_long,
                    x="Mês/Ano",
                    y="Produção",
                    color="Tipo de Bicicleta",
                    markers=True,
                    title=f"Previsão de Produção para 2025"
                )

                # Exibir o gráfico da previsão
                st.plotly_chart(fig_previsao, use_container_width=True)

        except Exception as e:
            st.error(f"Erro ao gerar a resposta: {e}")
    else:
        st.warning("Por favor, digite uma pergunta.")

# Exibir o histórico de perguntas e respostas
if st.session_state.historico:
    st.subheader("Histórico de Perguntas e Respostas")
    for entry in st.session_state.historico:
        st.write(f"**Pergunta:** {entry['pergunta']}")
        st.write(f"**Resposta:** {entry['resposta']}")
        st.markdown("---")
