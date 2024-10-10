# DASHBOARD-STREAMLIT-QUEIROZ-CARTOES
# Análise de Orçamento e Rentabilidade - Projeto Processo Seletivo

Este projeto foi desenvolvido com o objetivo de realizar análises de orçamento e rentabilidade, apoiando a governança e o processo decisório em relação às projeções patrimoniais e de resultado. O projeto permite simulações de impactos no resultado e na rentabilidade, além de apoiar áreas do banco com informações sobre o acompanhamento dos seus resultados.

## Descrição

O repositório contém scripts em Python e planilhas em Excel para analisar dados financeiros e contábeis, simular cenários econômicos e avaliar a rentabilidade de produtos e serviços. O projeto visa a criação de relatórios para acompanhamento mensal do realizado x orçado e criar projeções de cenários futuros.

## Funcionalidades

- **Importação e tratamento de dados contábeis e financeiros.**
- **Cálculo de indicadores de rentabilidade e margens de contribuição.**
- **Análise de variação do orçado x realizado com visualizações.**
- **Simulação de cenários futuros com base em inputs variáveis.**
- **Geração de relatórios automatizados e dashboards.**
- **Análise de Dados Financeiros:** Utiliza `pandas` para importar e tratar dados, calcular indicadores financeiros e realizar agrupamentos e sumarizações.
- **Visualizações Interativas:** Emprega `streamlit` para criar um dashboard web interativo, `altair` e `plotly_express` para gráficos dinâmicos, e `PIL` para manipulação de imagens.
- **Modelagem Estatística:** Utiliza `statsmodels` para previsões de tendências e padrões com a técnica de suavização exponencial de Holt-Winters.
- **Dashboard Streamlit:** Um dashboard interativo com filtros customizáveis, visualização de dados e previsões financeiras.

## Funcionalidades do Dashboard

O dashboard, criado com Streamlit, oferece as seguintes funcionalidades:

- Filtros interativos para seleção de tipos de plástico e períodos de tempo.
- Gráficos de barras e linhas para visualizar o consumo e custo de personalização dos cartões.
- Previsões de consumo e custo para os próximos 6 e 12 meses usando a técnica de suavização exponencial de Holt-Winters.
- Cálculo de SLA (Service Level Agreement) para monitorar a eficiência do processo de expedição dos cartões.

## Estrutura do Código

- Importação de bibliotecas e definição de funções para geração e tratamento dos DataFrames.
- Configuração da página do Streamlit e definição de layout do dashboard.
- Blocos interativos Streamlit com filtros e métricas.
- Utilização de `plotly_express` e `altair` para criar gráficos baseados nos DataFrames filtrados.
- Implementação de modelos preditivos para previsão de tendências de consumo.

## Bibliotecas Utilizadas

- `pandas`: Manipulação e análise de dados.
- `streamlit`: Criação de aplicativos web para visualização de dados.
- `altair`: Visualizações declarativas.
- `plotly_express`: Gráficos interativos avançados.
- `PIL`: Biblioteca de imagens do Python para adicionar logotipos e outros recursos gráficos.
- `datetime`: Manipulação de datas e horas.
- `statsmodels`: Modelagem estatística, incluindo previsão e análise de séries temporais.

