import pandas as pd
import streamlit as st
import plotly.express as px
import json
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
import random


def trat_agua():

    @st.cache_data
    def carregar_dados():
        tratamento = pd.read_csv('trat_mg.csv', encoding='utf-8', dtype={'COD_IBGE': str, 'ANO': str, 'CARROPIPA': str, 'CHAFARIZ': str, 'FONTE': str, 'CISTERNA': str, 'CANALIZACAO': str})
        return tratamento

    def aprendizado_maq():
        dados = pd.read_csv('trat_num.csv', encoding='utf-8', dtype={'COD_IBGE': str, 'ANO': str, 'CANALIZACAO': str})
        
        colunas = ['CAPT_SUPERFICIAL', 'CAPT_SUBTERRANEA', 'CAPT_AGUA_CHUVA', 'ETP_PRE_OXIDACAO', 'ETP_MIST_RAP_C0AG', 'ETP_FLOCULACAO', 'ETP_DECANTACAO', 'ETP_FLOTACAO', 'IMP_MONIT', 'DESINF_CLORO_GAS_HIPOC', 'DESINF_ISOCIANURATOS', 'DESINF_CLORAMINA', 'DESINF_DIOXIDO_CLORO', 'DESINF_OZONIO', 'DESINF_UV', 'RAD_CLORO_RES_LIVRE', 'RAD_DIOX_CLORO', 'RAD_CLORO_RES_COMB', 'POLIM_COM_EPICOLIDRINA', 'POLIM_COM_ACRILAMIDA', 'CARROPIPA', 'CHAFARIZ', 'FONTE', 'CISTERNA', 'CLASSIFICACAO_TRATAMENTO']
        colunas_labels = ['Captação Superficial', 'Captação Subterrânea', 'Captação da água de chuva', 'Etapa de pré oxidação', 'Etapa de mistura rápida / coagulação', 'Etapa de Floculação', 'Etapa de decantação', 'Etapa de flotação', 'Impedimento de monitaramento', 'Desinfecção com Cloro Gás ou Hipoclorito', 'Desinfecção com isocianuratos', 'Desinfecção com Cloramina', 'Desinfecção com dióxido de cloro', 'Desinfecção com ozônio', 'Desinfecção com UV', 'RAD Cloro residual livre', 'RAD dióxido de cloro', 'RAD cloro residual combinado', 'Polímero com epicolidrina', 'Polímero com acrilamida', 'Carro pipa', 'Chafariz', 'Fonte', 'Cisterna']

        dados = dados[colunas]
        x = dados.drop(columns=["CLASSIFICACAO_TRATAMENTO"])
        y = dados["CLASSIFICACAO_TRATAMENTO"]

        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.75)
        clf = DecisionTreeClassifier()
        clf.fit(x_train, y_train)

        colunas_valores = {}
        for i in range(len(colunas[:-1])):
            colunas_valores[colunas[i]] = int(st.checkbox(colunas_labels[i]))

        to_dataframe = pd.DataFrame.from_dict(colunas_valores, orient='index').T
        predicao = clf.predict(to_dataframe)
        if predicao[0]:
            st.markdown('#### :x: De acordo com nossos critérios, o tratamento de água na sua cidade é **INADEQUADO**.')
            st.write('Entre em contato com o gestor da cidade para requisitar melhorias!!')
        else:
            st.markdown('#### :white_check_mark: De acordo com nossos critérios, o tratamento de água na sua cidade é **ADEQUADO**.')
            st.write('Fique de olho e sempre fiscalize a água da sua cidade para que se mantenha limpa e própria para uso!!')
    
    # Função para carregar o GeoJSON
    @st.cache_data
    def carregar_geojson():
        with open('geojs-31-mun.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @st.cache_data
    def indicadoresPorAno():
        data = tratamento[['ANO'] + filtro_colunas[1:]]
        data_melted = data.melt(id_vars=['ANO'], var_name="Etapa", value_name="Status")
        data_count = data_melted[data_melted["Status"] == "S"].groupby(["ANO", "Etapa"]).size().reset_index(name="Qtd_Cidades")

        anos_unicos = tratamento["ANO"].unique()
        etapas_unicas = data_melted["Etapa"].unique()
        df_combinado = pd.MultiIndex.from_product([anos_unicos, etapas_unicas], names=["ANO", "Etapa"]).to_frame(index=False)

        df_final = df_combinado.merge(data_count, on=["ANO", "Etapa"], how="left").fillna(0)

        df_final["Qtd_Cidades"] = df_final["Qtd_Cidades"].astype(int)

        fig = px.line(df_final, x="ANO", y="Qtd_Cidades", color="Etapa", markers=True)
        
        for i in range(len(filtro_colunas)):
            fig.update_traces({'name': filtro_labels[i]}, selector={'name': filtro_colunas[i]})
        st.plotly_chart(fig)

    tratamento = carregar_dados()
    
    geojson_data = carregar_geojson()

    filtro_labels = ['Forma de abastecimento', 'Captação Superficial', 'Captação Subterrânea', 'Captação da água de chuva', 'Etapa de pré oxidação', 'Etapa de mistura rápida / coagulação', 'Etapa de Floculação', 'Etapa de decantação', 'Etapa de flotação', 'Impedimento de monitaramento', 'Etapa de desinfecção', 'Desinfecção com Cloro Gás ou Hipoclorito', 'Desinfecção com isocianuratos', 'Desinfecção com Cloramina', 'Dexinfecção com dióxido de cloro', 'Desinfecção com ozônio', 'Desinfecção com UV', 'RAD Cloro residual livre', 'RAD dióxido de cloro', 'RAD cloro residual combinado', 'Polímero com epicolidrina', 'Polímero com acrilamida', 'Etapa de fluoretação', 'Etapa de desfluoretação', 'Carro pipa', 'Chafariz', 'Fonte', 'Cisterna', 'Canalização']
    filtro_colunas = []

    # Ignorar coluna OUTRO_DESINF pois não trás mais informações de qual outra desinfecção é feita
    # Ignorar OUTRA_ETP e OUTRO_SUPRIMENTO pelo mesmo motivo
    ignorar_coluna = ['OUTRO_DESINF', 'OUTRA_ETP', 'OUTRO_SUPRIMENTO', 'CLASSIFICACAO_TRATAMENTO']

    for coluna in tratamento.columns:
        if coluna in ignorar_coluna: continue
        if len(tratamento[coluna].unique()) < 3:
            filtro_colunas.append(coluna)

    tabEstats, tabConsulta, tabInsights = st.tabs([":chart_with_upwards_trend: Informações gerais", ":memo: Consulta", ":linked_paperclips: Insights com outras bases"])
    
    with tabEstats:
        st.header(":chart_with_upwards_trend: Informações gerais")
        st.markdown("Dados sobre o tratamento de água empregado nos sistemas e soluções alternativas de abastecimento de água para consumo humano, informados pelo prestador de serviço em frequência anual. Fonte: [Ministério da Saúde](https://dados.gov.br/dados/conjuntos-dados/sisagua-tratamento-de-agua)")
        st.markdown(f"- Número total de registros: {len(tratamento)} instâncias.")
        st.markdown(f"- Anos disponíveis para consulta: {', '.join(tratamento['ANO'].unique())}.")
        st.markdown(f"- Quantidade de colunas: {len(tratamento.columns)}")
        st.markdown(f"- Quantidade de valores ausentes: ")
        st.session_state.valores_ausentes = False
        for k in tratamento.columns:
            nonna_values = tratamento[k].count()
            if not nonna_values:
                st.session_state.valores_ausentes = True
                st.write(f"Coluna {k} - {nonna_values} valores")
        if not st.session_state.valores_ausentes:
            st.markdown("-- Não há valores ausentes na base")
        st.markdown("- Resumo estatístico de variáveis numéricas:")
        st.write(tratamento.describe())
        
        st.markdown('- Evolução das formas de aplicação de tratamento de água por ano:')
        st.markdown('-- Esse gráfico mostra a evolução do número de cidades do estado de Minas Gerais atendida por certa aplicação de tratamento de água.\n\nAvaliar quais etapas de tratamento de água estão presentes em uma cidade é essencial para entender os riscos à saúde pública e a qualidade da infraestrutura sanitária. Além disso, essa análise pode auxiliar na formulação de políticas públicas voltadas para melhorias no sistema de abastecimento, garantindo maior segurança hídrica para a população.')
        indicadoresPorAno()

    with tabConsulta:
        st.header(":memo: Consulta")
        
        anos_para_filtro = ['Todos'] + list(tratamento['ANO'].unique())
        
        col_ano, col_coluna = st.columns(2)

        with col_ano:
            select_filtro_ano = st.selectbox('Selecione um ano:', anos_para_filtro, index=None, placeholder='Selecione um ano')
        with col_coluna:
            select_filtro_coluna = st.selectbox('Selecione uma categoria:', filtro_colunas, format_func=lambda x: filtro_labels[filtro_colunas.index(x)], index=None, placeholder='Selecione uma categoria')

        if select_filtro_ano and select_filtro_coluna:
            df_filtrado = tratamento if select_filtro_ano == 'Todos' else tratamento[tratamento['ANO'] == select_filtro_ano]

            # Exibe uma tabela com os dados agregados
            st.dataframe(df_filtrado[[select_filtro_coluna, 'ANO']].value_counts().reset_index())

            # Gerar gráfico de barras para a categoria selecionada
            fig, ax = plt.subplots()
            df_filtrado[select_filtro_coluna].value_counts().plot(kind='bar', ax=ax)
            ax.set_title(f"Distribuição de {select_filtro_coluna} para o ano {select_filtro_ano}")
            ax.set_xlabel(select_filtro_coluna)
            ax.set_ylabel("Frequência")
            st.pyplot(fig)

            df_for_map = df_filtrado.set_index("COD_IBGE")

            for feature in geojson_data['features']:
                feature['properties']['id'] = feature['properties']['id'][:-1]
                cidade_cod_ibge = feature['properties']['id']
                feature['properties']['categoria'] = select_filtro_coluna
                if cidade_cod_ibge in df_for_map.index:
                    feature['properties']['dado'] = df_for_map.loc[cidade_cod_ibge, select_filtro_coluna]
                else: feature['properties']['dado'] = 'N'

            # --- Criação do mapa ---
            st.header(":world_map: Mapa das Cidades Filtradas")
            m = folium.Map(location=[-18.5122, -44.5550], zoom_start=6)

            folium.GeoJson(
                geojson_data,
                style_function= lambda feature: {
                    "fillColor": "#00FF00" if feature['properties']['dado'] == 'S' else '#808080',
                    "color": "#000000",
                    "weight": 1,
                    "fillOpacity": 0.7,
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=['name', 'categoria', 'dado'],
                    aliases=['Cidade: ', 'Categoria: ', 'Dado: '],
                    localize=True,
                    sticky=True,
                    labels=True,
                    max_width=300,
                )
            ).add_to(m)

            # Exibe o mapa no Streamlit
            st_folium(m)

        st.divider()
        st.header(":grey_question: O tratamento de água é adequado na sua cidade?")
        st.markdown("- **Critérios**:")
        st.markdown("-- Água de fontes alternativas sem tratamento (Carro-pipa, chafariz, fonte ou cisterna): **Inadequada**.")
        st.markdown("-- Água sem informações de captação: **Inadequada**.")
        st.markdown("-- O tratamento só será considerada **Adequado** quando tem monitoramento, etapas de desinfecção e etapas de tratamento.")
        st.markdown("-- Etapas de tratamento básico: Etapas de pré-oxidação, floculação, decantação, flotação e mistura rápida / coagulação.")
        st.markdown("-- Etapas de desinfecção: Desinfecção com Cloro Gás ou Hipoclorito, Desinfecção com isocianuratos, Desinfecção com Cloramina, Desinfecção com dióxido de cloro, Desinfecção com ozônio e Desinfecção com UV.")
        
        st.markdown("- Selecione as etapas presentes na sua cidade: ")
        aprendizado_maq()
        
    with tabInsights:
        st.header(":linked_paperclips: Insights com outras bases")
        st.write("Aqui serão exibidos alguns insights e curiosidades com outras bases disponíveis no sistema.")
