#Importando as Libs Necessárias
import pandas as pd
import streamlit as st
import altair as alt
from PIL import Image
import datetime as dt
import plotly_express as px
#Fazendo as primeiras alterações necessárias
@st.cache_data
def gerar_df():
    df = pd.read_excel(
        io='Case - Queiroz Cartões (2) 1.xlsx',
        engine= 'openpyxl',
        sheet_name='BASE',
        usecols='A:M',
        nrows=509,        
        )
    return df
st.set_page_config(layout="wide")


df = gerar_df()
colunas_Uteis = ["REMESSA","DATA PEDIDO","DATA RECEBIMENTO","DATA DE EXPEDIÇÃO","TIPO DE PLASTICO","QTD PLÁSTICO"]
df = df[colunas_Uteis]

df['Mes'] = df['DATA PEDIDO'].dt.month
logopng = "Sicoob.png"

#Cabeçalho
col1, col2 = st.columns([1, 10])
with col1:
    st.image(logopng, width=80)
with col2:
    st.title("Dashboard Análise Semestral SICOOB")

#PRIMEIRO GRÁFICO
start_date = dt.datetime(2022, 4, 1)
end_date = dt.datetime(2022,9,20)

# Agrupando os dados por 'Mês' e 'TIPO DE PLASTICO'
df_agregado = df.groupby(['Mes', 'TIPO DE PLASTICO'], as_index=False).agg({'QTD PLÁSTICO':'sum'})

with st.container():
    st.header("Insira os Filtros que Deseja Aplicar:")
    coll1, coll2 = st.columns(2)
    with coll1:
        Plastico_Selecionado = st.multiselect("Slecione o Tipo de Plástico Desejado:",options=df_agregado['TIPO DE PLASTICO'].unique(),
                                              default=df_agregado['TIPO DE PLASTICO'].unique())
    with coll2:
        Mes_Selecionado = st.multiselect("Selecione o Mês:",options= df_agregado['Mes'].unique(),
                                         default=df_agregado['Mes'].unique())

# Agrupando os dados por 'Mês' e 'TIPO DE PLASTICO'
df_agregado1 = df.groupby(['Mes', 'TIPO DE PLASTICO'], as_index=False).agg({'QTD PLÁSTICO':'sum'})

df_filtrado = df_agregado1[(df_agregado1['TIPO DE PLASTICO'].isin(Plastico_Selecionado)) & 
                          (df_agregado['Mes'].isin(Mes_Selecionado))]

# Agora, criando o gráfico de barras com os dados agregados
colll1, colll2 = st.columns(2)
with colll1:
    color_discrete_map = {'black': '#FAFF00', 'gold': '#20FF0D', 'platinum': "#006400"}
    #color_discrete_map = {'black': '#FAFF00', 'gold': '#006400', 'platinum': '#20FF0D'}
    fig = px.bar(df_filtrado, x='Mes', y='QTD PLÁSTICO', color='TIPO DE PLASTICO', 
             barmode='group', title='Volume de Plástico Consumido por Mês e Tipo de Plástico',
             color_discrete_map=color_discrete_map)
    fig.update_traces(texttemplate='%{y}', textposition='outside')
    fig.update_yaxes(visible=False)

    st.plotly_chart(fig)


######SEGUNDO GRÁFICO##################
df_filtrado2 = df[df['TIPO DE PLASTICO'].isin(Plastico_Selecionado) & df['Mes'].isin(Mes_Selecionado)]
df_filtrado2['TIPO DE PLASTICO'] = df_filtrado2['TIPO DE PLASTICO'].str.lower()

# Calculando o custo de personalização
personalizacao_precos = {
    'platinum': 1.80,
    'gold': 1.90,
    'black': 2.20
}
df_filtrado2['CUSTO DE PERSONALIZACAO'] = df_filtrado2.apply(
    lambda row: row['QTD PLÁSTICO'] * personalizacao_precos[row['TIPO DE PLASTICO']],
    axis=1
)

# Agrupando os dados filtrados e calculando o custo acumulado
df_agregado_filtrado2 = df_filtrado2.groupby(df_filtrado2['DATA PEDIDO'].dt.to_period('M'))['CUSTO DE PERSONALIZACAO'].sum().reset_index()
df_agregado_filtrado2['CUSTO DE PERSONALIZACAO ACUMULADO'] = df_agregado_filtrado2['CUSTO DE PERSONALIZACAO'].cumsum()
df_agregado_filtrado2['DATA PEDIDO'] = df_agregado_filtrado2['DATA PEDIDO'].dt.strftime('%Y-%m')

# Criando o gráfico com os dados filtrados
fig2 = px.bar(df_agregado_filtrado2, x='CUSTO DE PERSONALIZACAO ACUMULADO', y='DATA PEDIDO',
             orientation='h',
             title='Custo de Personalização Acumulado por Mês',
             color_discrete_sequence=["#20FF0D"])
fig2.update_traces(texttemplate='%{x}', textposition='outside')

with colll2:
    st.plotly_chart(fig2)


#previsão para os próximos 6 meses:
base_previsao = pd.read_excel('Case - Queiroz Cartões (2) 1.xlsx', sheet_name='BASE')

# Ordenar os dados por DATA PEDIDO
base_previsao_sorted = base_previsao.sort_values(by='DATA PEDIDO', ascending=False)

# Agrupandor os dados por mês e tipo de plástico e somar as quantidades
Consumo_por_mes = base_previsao_sorted.groupby([base_previsao_sorted['DATA PEDIDO'].dt.to_period('M'), 'TIPO DE PLASTICO'])['QTD PLÁSTICO'].sum().unstack(fill_value=0)
Consumo_por_mes.index = Consumo_por_mes.index.to_timestamp()

# Excluir os valores de junho
Consumo_por_mes_sem_junho = Consumo_por_mes.drop(pd.Timestamp('2022-06-01'))

# Calcular a média dos outros meses
media_sem_junho = Consumo_por_mes_sem_junho.mean()

# Substituir os valores de junho pela média dos outros meses
Consumo_por_mes.loc[pd.Timestamp('2022-06-01')] = media_sem_junho

from statsmodels.tsa.holtwinters import ExponentialSmoothing

#Holt's Linear Trend
previsao_holt_linear = {}

# Configurar os modelos e fazer as previsões para cada tipo de plástico
num_meses = 6  # Número de períodos para prever
for tipo_plastico in Consumo_por_mes.columns:
    modelo = ExponentialSmoothing(Consumo_por_mes[tipo_plastico], 
                              trend='add', 
                              seasonal="mul",  # ou 'mul' para sazonalidade multiplicativa
                              seasonal_periods=3,  # ajuste para o número de períodos por temporada
                              damped_trend=True)

    modelo_fit = modelo.fit(optimized=True)
    previsao = modelo_fit.forecast(num_meses)
    previsao_holt_linear[tipo_plastico] = previsao

# Criar um DataFrame a partir das previsões de Holt's Linear Trend
previsao_df_holt_linear = pd.DataFrame(previsao_holt_linear, 
                                       index=pd.date_range(start=Consumo_por_mes.index[-1] + pd.offsets.MonthBegin(1),
                                                           periods=num_meses, 
                                                           freq='MS'))
# Arredondar os valores do DataFrame para o inteiro mais próximo
previsao_df_holt_linear = previsao_df_holt_linear.round(0).astype(int)

previsao_df_holt_linear = previsao_df_holt_linear.reset_index().rename(columns={'index': 'Data'})
color_discrete_map = {'black': '#FAFF00', 'gold': '#20FF0D', 'platinum': "#089e0f"}
fig3= px.line(previsao_df_holt_linear, x='Data', y=previsao_df_holt_linear.columns,
              title='Previsões 6 meses de Consumo por Plástico',
              labels={'value': 'Previsão de Consumo', 'variable': 'Tipo de Plástico'},
              markers=True,
              color_discrete_map= color_discrete_map)

# Melhorar o layout
fig3.update_layout(
    xaxis_title='Data',
    yaxis_title='Consumo Previsto',
    legend_title='Tipo de Plástico',
     title_x=0.4
)
cores_hex = ['#FF5733', '#33FF57', '#3357FF']

#Calculando os custos
previsao_df_holt_linear["Custo de Personalizacao Black"] = previsao_df_holt_linear["black"] * 2.2 
previsao_df_holt_linear["Custo de Personalizacao Platinum"] = previsao_df_holt_linear["platinum"] * 1.8 
previsao_df_holt_linear["Custo de Personalizacao Gold"] = previsao_df_holt_linear["gold"] * 1.9

# Somar os custos de personalização para cada tipo de plástico
SomaPersonalizacaoBlack = previsao_df_holt_linear["Custo de Personalizacao Black"].sum()
SomaPersonalizacaoPlatinum = previsao_df_holt_linear["Custo de Personalizacao Platinum"].sum()
SomaPersonalizacaoGold = previsao_df_holt_linear["Custo de Personalizacao Gold"].sum()

# Calcular os custos totais do plástico com base nas previsões de consumo
CustoPlasticoBlack = previsao_df_holt_linear['black'].sum() * 5.85
CustoPlasticoGold = previsao_df_holt_linear['gold'].sum() * 5.1
CustoPlasticoPlatinum = previsao_df_holt_linear['platinum'].sum() * 5.5

# Calcular o custo total por tipo de plástico, incluindo personalização e custo do plástico
total_Custo_Por_Plastico = {
    "Platinum": SomaPersonalizacaoPlatinum + CustoPlasticoPlatinum,
    "Gold": SomaPersonalizacaoGold + CustoPlasticoGold,
    "Black": SomaPersonalizacaoBlack + CustoPlasticoBlack
}

# Criar um DataFrame para exibir os custos totais
df_custoPlastico = pd.DataFrame(total_Custo_Por_Plastico, index=["Custo Total"])

#VARIAVEIS PARA CARTOES

CustoTotal_6Meses = df_custoPlastico["Platinum"]+df_custoPlastico["Gold"]+df_custoPlastico["Black"]
CustoPersonalizacao_6Meses = SomaPersonalizacaoBlack + SomaPersonalizacaoGold+ SomaPersonalizacaoPlatinum
CustoPlastico_6Meses = CustoPlasticoBlack + CustoPlasticoGold + CustoPlasticoPlatinum
CustoPersonalizacao_6Meses = previsao_df_holt_linear[["Custo de Personalizacao Black", "Custo de Personalizacao Platinum", "Custo de Personalizacao Gold"]].sum().sum()
CustoPlastico_6Meses = (previsao_df_holt_linear['black'].sum() * 5.85) + (previsao_df_holt_linear['gold'].sum() * 5.1) + (previsao_df_holt_linear['platinum'].sum() * 5.5)
CustoTotal_6Meses = CustoPersonalizacao_6Meses + CustoPlastico_6Meses


col1, col2 = st.columns([3, 1])

with col1:
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.caption("")
    st.caption("")
    st.caption("")
    st.caption("")
    st.caption("")
    st.metric("Custo Total 6 meses", f"R$ {CustoTotal_6Meses:,.0f}".replace(',', '.'))
    st.metric("Custo Personalização 6 Meses", f"R$ {CustoPersonalizacao_6Meses:,.0f}".replace(',', '.'))
    st.metric("Custo Plástico 6 Meses", f"R$ {CustoPlastico_6Meses:,.0f}".replace(',', '.'))


#Previsao para 12 Meses

previsao_holt_linear = {}

# Configurar os modelos e fazer as previsões para cada tipo de plástico
num_meses = 12  # Número de períodos para prever
for tipo_plastico in Consumo_por_mes.columns:
    modelo = ExponentialSmoothing(Consumo_por_mes[tipo_plastico], 
                              trend='add', 
                              seasonal="mul",  # ou 'mul' para sazonalidade multiplicativa
                              seasonal_periods=3,  # ajuste para o número de períodos por temporada
                              damped_trend=True)

    modelo_fit = modelo.fit(optimized=True)
    previsao = modelo_fit.forecast(num_meses)
    previsao_holt_linear[tipo_plastico] = previsao

# Criar um DataFrame a partir das previsões de Holt's Linear Trend
previsao_df_holt_linear = pd.DataFrame(previsao_holt_linear, 
                                       index=pd.date_range(start=Consumo_por_mes.index[-1] + pd.offsets.MonthBegin(1),
                                                           periods=num_meses, 
                                                           freq='MS'))
# Arredondar os valores do DataFrame para o inteiro mais próximo
previsao_df_holt_linear = previsao_df_holt_linear.round(0).astype(int)

previsao_df_holt_linear = previsao_df_holt_linear.reset_index().rename(columns={'index': 'Data'})

fig4= px.line(previsao_df_holt_linear, x='Data', y=previsao_df_holt_linear.columns,
              title='Previsões 12 meses de Consumo por Plástico',
              labels={'value': 'Previsão de Consumo', 'variable': 'Tipo de Plástico'},
              markers=True,
              color_discrete_map = color_discrete_map)
# Melhorando o layout
fig4.update_layout(
    xaxis_title='Data',
    yaxis_title='Consumo Previsto',
    legend_title='Tipo de Plástico',
      title_x=0.40
)



#Calculando os custos
previsao_df_holt_linear["Custo de Personalizacao Black"] = previsao_df_holt_linear["black"] * 2.2 
previsao_df_holt_linear["Custo de Personalizacao Platinum"] = previsao_df_holt_linear["platinum"] * 1.8 
previsao_df_holt_linear["Custo de Personalizacao Gold"] = previsao_df_holt_linear["gold"] * 1.9

# Somar os custos de personalização para cada tipo de plástico
SomaPersonalizacaoBlack = previsao_df_holt_linear["Custo de Personalizacao Black"].sum()
SomaPersonalizacaoPlatinum = previsao_df_holt_linear["Custo de Personalizacao Platinum"].sum()
SomaPersonalizacaoGold = previsao_df_holt_linear["Custo de Personalizacao Gold"].sum()

# Calcular os custos totais do plástico com base nas previsões de consumo
CustoPlasticoBlack = previsao_df_holt_linear['black'].sum() * 5.85
CustoPlasticoGold = previsao_df_holt_linear['gold'].sum() * 5.1
CustoPlasticoPlatinum = previsao_df_holt_linear['platinum'].sum() * 5.5

# Calcular o custo total por tipo de plástico, incluindo personalização e custo do plástico
total_Custo_Por_Plastico = {
    "Platinum": SomaPersonalizacaoPlatinum + CustoPlasticoPlatinum,
    "Gold": SomaPersonalizacaoGold + CustoPlasticoGold,
    "Black": SomaPersonalizacaoBlack + CustoPlasticoBlack
}

# Criar um DataFrame para exibir os custos totais
df_custoPlastico = pd.DataFrame(total_Custo_Por_Plastico, index=["Custo Total"])

#VARIAVEIS PARA CARTOES

CustoTotal_6Meses = df_custoPlastico["Platinum"]+df_custoPlastico["Gold"]+df_custoPlastico["Black"]
CustoPersonalizacao_6Meses = SomaPersonalizacaoBlack + SomaPersonalizacaoGold+ SomaPersonalizacaoPlatinum
CustoPlastico_6Meses = CustoPlasticoBlack + CustoPlasticoGold + CustoPlasticoPlatinum
CustoPersonalizacao_6Meses = previsao_df_holt_linear[["Custo de Personalizacao Black", "Custo de Personalizacao Platinum", "Custo de Personalizacao Gold"]].sum().sum()
CustoPlastico_6Meses = (previsao_df_holt_linear['black'].sum() * 5.85) + (previsao_df_holt_linear['gold'].sum() * 5.1) + (previsao_df_holt_linear['platinum'].sum() * 5.5)
CustoTotal_6Meses = CustoPersonalizacao_6Meses + CustoPlastico_6Meses


col1, col2 = st.columns([3, 1])

with col1:
    st.plotly_chart(fig4, use_container_width=True)

with col2:
    st.caption("")
    st.caption("")
    st.caption("")
    st.caption("")
    st.caption("")
    st.metric("Custo Total 12 meses", f"R$ {CustoTotal_6Meses:,.0f}".replace(',', '.'))
    st.metric("Custo Personalização 12 Meses", f"R$ {CustoPersonalizacao_6Meses:,.0f}".replace(',', '.'))
    st.metric("Custo Plástico 12 Meses", f"R$ {CustoPlastico_6Meses:,.0f}".replace(',', '.'))



### % de SLA
coluna_Datas = ["DATA RECEBIMENTO","DATA DE EXPEDIÇÃO"]
df_datas = df[coluna_Datas]
df_datas['DATA RECEBIMENTO'] = pd.to_datetime(df['DATA RECEBIMENTO'])
df_datas['DATA DE EXPEDIÇÃO'] = pd.to_datetime(df['DATA DE EXPEDIÇÃO'])
df_datas["Diferenca de Dias"] = df_datas["DATA DE EXPEDIÇÃO"] - df_datas["DATA RECEBIMENTO"]
df_datas["Está Atrasado?"] = df_datas["Diferenca de Dias"].apply(lambda x: "Sim" if x > pd.Timedelta(days=3) else "Não")
atrasos = df_datas['Está Atrasado?'].value_counts().get('Sim', 0)
Certos = df_datas['Está Atrasado?'].value_counts().get('Não', 0)
total_pedidos = Certos+ atrasos
df_datas['Mês'] = df_datas['DATA RECEBIMENTO'].dt.month
def calculate_sla(group):
    certos = group['Está Atrasado?'].value_counts().get('Não', 0)
    total = len(group)
    return certos / total if total else 0

# Agrupando por mês e aplicando a função de cálculo do SLA
sla_por_mes = df_datas.groupby('Mês').apply(calculate_sla)

sla_por_mes = pd.DataFrame(sla_por_mes)
sla_por_mes["SLA"] = df_datas.groupby('Mês').apply(calculate_sla)
sla_por_mes_data = {
    'Mês': [4, 5, 6, 7, 8, 9],
    'SLA': [0.5785, 0.5652, 0.8182, 0.6559, 0.7328, 0.6092]
}
sla_por_mes = pd.DataFrame(sla_por_mes_data)
fig5 = px.line(sla_por_mes, x='Mês', y='SLA', title='% SLA por Mês',
              labels={'SLA': 'SLA', 'Mês': 'Mês'},
              template='plotly_white',
              markers=True)
fig5.update_traces(line=dict(color='red'))
fig5.update_yaxes(range=[0, 1])
fig5.add_hline(y=0.95, line_dash="dash", line_color="green")
for x, y in zip(sla_por_mes['Mês'], sla_por_mes['SLA']):
    fig5.add_annotation(x=x, y=y, text="{:.2f}".format(y), showarrow=False, yshift=10)
fig5.update_layout(autosize=False, width=1500, height=500, title_x=0.5)
st.plotly_chart(fig5)