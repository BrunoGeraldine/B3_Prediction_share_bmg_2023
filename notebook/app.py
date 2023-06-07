import streamlit as st
import yfinance as yf
from datetime import date
import pandas as pd
from prophet import Prophet
from prophet.plot import plot_plotly, plot_components_plotly
from plotly import graph_objects as go

DATA_INICIO = '2017-01-01'
DATA_FIM = date.today().strftime('%Y-%m-%d')

st.title('Análise de ações')

#criando a side bar
st.sidebar.header('Escolha a ação')

n_dias = st.slider('Quantidade de dias a ser prevista', 30, 365)

#Coletando o nome e sigla da ação escolhida
def pegar_dados_acao():
    path = '/home/bruno/repos/B3_Prediction_share_bmg_2023/dataset/acao_nome.csv'
    return pd.read_csv(path)

df = pegar_dados_acao()

acao = df['snome']
nome_acao_escolhida = st.sidebar.selectbox('Escolha uma ação', acao)

# Capturando apenas as siglas
df_acao = df[df['snome'] == nome_acao_escolhida]
acao_escolhida = df_acao.iloc[1]['sigla_acao']
acao_escolhida = acao_escolhida + '.SA'

@st.cache_data
def pegar_valores_online(sigla_acao):
    df = yf.download(sigla_acao, DATA_INICIO, DATA_FIM)
    df.reset_index(inplace=True)
    return df

df_valores = pegar_valores_online(acao_escolhida)

st.subheader('Tabela de Valores - ' + nome_acao_escolhida)
st.write(df_valores.tail(11))


#Criando grafico
st.subheader('Grafico de preços')
fig = go.Figure()
fig.add_trace(go.Scatter(x=df_valores['Date'],
                         y=df_valores['Close'],
                         name='Preço Fechamento',
                         line_color='orange'))


fig.add_trace(go.Scatter(x=df_valores['Date'],
                         y=df_valores['Open'],
                         name='Preço Abertura',
                         line_color='blue'))
st.plotly_chart(fig)

#Previsão
df_treino = df_valores[['Date', 'Close']]

#Renomear colunas (set do prophet)
df_treino = df_treino.rename(columns={'Date': 'ds', 'Close': 'y'})

#Modelo
modelo = Prophet()
modelo.fit(df_treino)

#Info das previsões
futuro = modelo.make_future_dataframe(periods=n_dias, freq='B')
#obs: n-dias é o slider criado acima e freq=B refere-se a dias uteis

previsao = modelo.predict(futuro)

st.subheader('Previsão')
st.write(previsao[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(n_dias))

#Grafico da Previsao
grafico1 = plot_plotly(modelo, previsao)
st.plotly_chart(grafico1)

grafico2 = plot_components_plotly(modelo, previsao)
st.plotly_chart(grafico2)
