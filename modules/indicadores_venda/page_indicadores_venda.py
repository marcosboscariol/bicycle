import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# CSS personalizado para alterar a cor do título, da barra lateral e dos botões
# st.markdown(
#     """
#     <style>
#     /* Alterar a cor do título */
#     h1 {
#         color: #FF8C00; /* Laranja mais escuro */
#         font-weight: bold;
#         font-family: 'Consolas', monospace;
#     }

#     /* Alterar a cor de fundo da barra lateral */
#     .css-1d391kg {
#         background-color: #FF8C00;  /* Laranja escuro */
#     }

#     /* Alterar a cor de fundo da sidebar do Streamlit */
#     .css-1v3fvcr {
#         background-color: #FF8C00;  /* Laranja escuro */
#     }

#     /* Alterar a cor do texto dos filtros */
#     .css-1ab2c4f {
#         color: white;  /* Cor do texto */
#     }

#     /* Alterar a cor de fundo dos botões de filtro */
#     .css-18e3p6a {
#         background-color: #FF8C00;  /* Laranja escuro */
#         color: white;  /* Cor do texto do botão */
#     }

#     /* Alterar a cor do botão de filtro específico (com a classe st-ax) */
#     .st-ax {
#         background-color: #FF8C00 !important;  /* Laranja escuro */
#         color: white !important;  /* Cor do texto do botão */
#         border-radius: 5px;
#     }

#     /* Alterar a cor de hover (quando o usuário passa o mouse sobre o botão) */
#     .st-ax:hover {
#         background-color: #FF7F00 !important;  /* Laranja mais claro */
#     }

#     /* Alterar a cor do ícone de delete no botão */
#     .st-ax svg {
#         fill: white !important;  /* Cor branca para o ícone */
#     }

#     </style>
#     """,
#     unsafe_allow_html=True
# )

# Dados simulados para 2022, 2023 e 2024
np.random.seed(42)
estados = ["SP", "RJ", "MG", "BA", "PR", "RS", "SC", "PE", "CE", "MA"]

# Simulação de vendas por estado e ano (2022, 2023, 2024)
anos = [2022, 2023, 2024]
df_vendas = []

for estado in estados:
    for ano in anos:
        for mes in range(1, 13):
            vendas_bicicleta_a = np.random.randint(100, 500)
            vendas_bicicleta_b = np.random.randint(100, 500)
            df_vendas.append({
                "Estado": estado,
                "Ano": ano,
                "Mes": mes,
                "Vendas Bicicleta A": vendas_bicicleta_a,
                "Vendas Bicicleta B": vendas_bicicleta_b
            })

df_vendas = pd.DataFrame(df_vendas)

# Adicionar coordenadas (latitude, longitude) para cada estado brasileiro
coordenadas = {
    "SP": (-23.5505, -46.6333),
    "RJ": (-22.9068, -43.1729),
    "MG": (-19.8157, -43.9542),
    "BA": (-12.9714, -38.5014),
    "PR": (-25.4284, -49.2733),
    "RS": (-30.0346, -51.2177),
    "SC": (-27.5954, -48.5480),
    "PE": (-8.0476, -34.8770),
    "CE": (-3.7172, -38.5437),
    "MA": (-2.5391, -44.2820)
}

df_vendas["Latitude"] = df_vendas["Estado"].map(lambda x: coordenadas[x][0])
df_vendas["Longitude"] = df_vendas["Estado"].map(lambda x: coordenadas[x][1])

# Filtro interativo
st.title("Dashboard de Vendas de Bicicletas")

# Filtro de Ano (permitir múltiplos anos)
ano_filtro = st.sidebar.multiselect(
    'Selecione os Anos', df_vendas['Ano'].unique(), default=df_vendas['Ano'].unique())

# Filtro de Estado (permitir múltiplos estados)
estado_filtro = st.sidebar.multiselect(
    'Selecione os Estados', df_vendas['Estado'].unique(), default=df_vendas['Estado'].unique())

# Aplicar filtro nos dados
df_vendas_filtrado = df_vendas[df_vendas['Ano'].isin(ano_filtro)]
df_vendas_filtrado = df_vendas_filtrado[df_vendas_filtrado['Estado'].isin(
    estado_filtro)]

# Cálculos para os Cards
# 1. Total de Vendas
total_vendas = df_vendas_filtrado["Vendas Bicicleta A"].sum(
) + df_vendas_filtrado["Vendas Bicicleta B"].sum()

# 2. Mês com Maior Número de Vendas
df_vendas_mes = df_vendas_filtrado.groupby(['Ano', 'Mes'])[
    ['Vendas Bicicleta A', 'Vendas Bicicleta B']].sum().reset_index()
df_vendas_mes['Total Vendas'] = df_vendas_mes['Vendas Bicicleta A'] + \
    df_vendas_mes['Vendas Bicicleta B']
mes_maior_venda = df_vendas_mes.loc[df_vendas_mes['Total Vendas'].idxmax()]

# 3. Mês com Menor Número de Vendas
mes_menor_venda = df_vendas_mes.loc[df_vendas_mes['Total Vendas'].idxmin()]

# Layout para exibir os Cards
st.subheader("Indicadores de Vendas")
col1, col2, col3 = st.columns(3)

# Exibir o Card de Total de Vendas
col1.metric("Total de Vendas", f"R${total_vendas:,.2f}")

# Exibir o Card com o Mês com Maior Número de Vendas
col2.metric(f"Mês com Maior Vendas ({mes_maior_venda['Mes']}/{mes_maior_venda['Ano']})",
            f"R${mes_maior_venda['Total Vendas']:,.2f}")

# Exibir o Card com o Mês com Menor Número de Vendas
col3.metric(f"Mês com Menor Vendas ({mes_menor_venda['Mes']}/{mes_menor_venda['Ano']})",
            f"R${mes_menor_venda['Total Vendas']:,.2f}")

# Layout com duas colunas para gráficos
col1, col2 = st.columns(2)

# Gerar uma paleta de cores para os estados
color_scale = px.colors.qualitative.Set1
num_estados = len(estados)
if num_estados > len(color_scale):
    # Se houver mais estados que cores, usar uma paleta contínua
    color_scale = px.colors.sample_colorscale("Viridis", num_estados)

# Criar um dicionário de cores para os estados
estado_color_map = {estado: color_scale[i] for i, estado in enumerate(estados)}

# Gráfico de barras horizontais (Vendas por estado)
fig_barras = px.bar(df_vendas_filtrado.groupby('Estado')['Vendas Bicicleta A'].sum().reset_index(),
                    x="Vendas Bicicleta A", y="Estado", orientation="h",
                    title=f"Vendas Totais por Estado para Bicicleta A ({
    ', '.join(map(str, ano_filtro))})",
    labels={"Estado": "Estado",
            "Vendas Bicicleta A": "Vendas"},
    color="Estado",  # Diferencia as cores por estado
    color_discrete_map=estado_color_map)  # Usar o mapa de cores gerado
col1.plotly_chart(fig_barras)

# Gráfico de linha (Vendas ao longo do tempo)
df_vendas_filtrado['MesAno'] = df_vendas_filtrado['Mes'].astype(
    str) + "/" + df_vendas_filtrado['Ano'].astype(str)
fig_linha = px.line(df_vendas_filtrado.groupby('MesAno', as_index=False).agg({'Vendas Bicicleta A': 'sum'}),
                    x='MesAno', y='Vendas Bicicleta A',
                    title=f"Vendas de Bicicleta A ao Longo do Tempo ({
    ', '.join(map(str, ano_filtro))})",
    labels={"MesAno": "Mês/Ano", "Vendas Bicicleta A": "Vendas"})
col2.plotly_chart(fig_linha)

# Mapa de vendas por estado
fig_mapa = px.scatter_geo(df_vendas_filtrado.groupby('Estado').agg({
    'Latitude': 'first',
    'Longitude': 'first',
    'Vendas Bicicleta A': 'sum'
}).reset_index(),
    lat="Latitude",
    lon="Longitude",
    size="Vendas Bicicleta A",  # Tamanho do ponto proporcional às vendas
    color="Estado",  # Agora, usamos o nome do estado para colorir os pontos
    hover_name="Estado",  # Exibir o estado ao passar o mouse
    title=f"Mapa de Vendas por Estado (Bicicleta A) - ({
    ', '.join(map(str, ano_filtro))})",
    color_discrete_map=estado_color_map,  # Usar o mesmo mapa de cores
    template="plotly",  # Tema do gráfico
    projection="mercator",  # Tipo de projeção do mapa
)
st.plotly_chart(fig_mapa)
