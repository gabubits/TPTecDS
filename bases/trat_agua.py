import pandas as pd
import streamlit as st
import plotly.express as px
import json
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium

def trat_agua():
    @st.cache_data
    def carregar_dados():
        tratamento = pd.read_csv('trat_mg.csv', encoding='utf-8', dtype={'COD_IBGE': str, 'ANO': str, 'CARROPIPA': str, 'CHAFARIZ': str, 'FONTE': str, 'CISTERNA': str, 'CANALIZACAO': str})

        tratamento['CANALIZACAO'] = tratamento.CANALIZACAO.fillna('N')
        tratamento['CARROPIPA'] = tratamento.CARROPIPA.fillna('N')
        tratamento['FONTE'] = tratamento.FONTE.fillna('N')
        tratamento['CHAFARIZ'] = tratamento.CHAFARIZ.fillna('N')
        tratamento['CISTERNA'] = tratamento.CISTERNA.fillna('N')
        tratamento['VAZAO_AGUA'] = tratamento.VAZAO_AGUA.fillna(0.0)
        tratamento['NUM_FILTROS'] = tratamento.NUM_FILTROS.fillna(0.0)
        tratamento['OUTRA_ETP'] = tratamento.OUTRA_ETP.fillna('N')
        tratamento['OUTRO_DESINF'] = tratamento.OUTRO_DESINF.fillna('N')
        tratamento['OUTRO_SUPRIMENTO'] = tratamento.OUTRO_SUPRIMENTO.fillna('N')

        return tratamento

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
    ignorar_coluna = ['OUTRO_DESINF', 'OUTRA_ETP', 'OUTRO_SUPRIMENTO']

    for coluna in tratamento.columns:
        if coluna in ignorar_coluna: continue
        if len(tratamento[coluna].unique()) < 3:
            filtro_colunas.append(coluna)

    tabEstats, tabConsulta, tabInsights = st.tabs([":chart_with_upwards_trend: Informações gerais", ":memo: Consulta", ":linked_paperclips: Insights com outras bases"])
    
    with tabEstats:
        st.header(":chart_with_upwards_trend: Informações gerais")
        st.markdown("Descrição. Fonte: [Ministério da Saúde](https://link.com)")
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
            if select_filtro_coluna:
                fig, ax = plt.subplots()
                df_filtrado[select_filtro_coluna].value_counts().plot(kind='bar', ax=ax)
                ax.set_title(f"Distribuição de {select_filtro_coluna} para o ano {select_filtro_ano}")
                ax.set_xlabel(select_filtro_coluna)
                ax.set_ylabel("Frequência")
                st.pyplot(fig)

            # Extrair os códigos IBGE dos dados filtrados
            codigos_ibge_filtrados = df_filtrado['COD_IBGE'].unique()

            # --- Criação do mapa ---
            st.header(":world_map: Mapa das Cidades Filtradas")
            m = folium.Map(location=[-18.5122, -44.5550], zoom_start=6)

            # Função que define o estilo das cidades (baseado na filtragem)
            def style_function(feature):
                cidade_cod_ibge = feature['properties']['id']
                if cidade_cod_ibge in codigos_ibge_filtrados:
                    return {
                        'fillColor': '#00FF00',  # Verde para cidades filtradas
                        'color': '#000000',       # Cor da borda
                        'weight': 1,
                        'fillOpacity': 0.7
                    }
                else:
                    return {
                        'fillColor': '#808080',  # Cinza para cidades não filtradas
                        'color': '#000000',
                        'weight': 1,
                        'fillOpacity': 0.3
                    }

            # Função para obter o valor da categoria para uma cidade (usando o código IBGE)
            def get_categoria_dado(cidade, categoria):
                dados_categoria = df_filtrado[df_filtrado['COD_IBGE'] == cidade]
                if not dados_categoria.empty:
                    return dados_categoria[categoria].values[0]
                else:
                    return 'N/A'

            # Para cada cidade (feature) no GeoJSON, adiciona os campos 'categoria' e 'dado'
            for feature in geojson_data['features']:
                cidade_cod_ibge = feature['properties']['id']
                feature['properties']['categoria'] = select_filtro_coluna
                feature['properties']['dado'] = get_categoria_dado(cidade_cod_ibge, select_filtro_coluna)

            folium.GeoJson(
                geojson_data,
                style_function=style_function,
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

    with tabInsights:
        st.markdown(":linked_paperclips: Insights com outras bases")
        st.write("Aqui serão exibidos alguns insights e curiosidades com outras bases disponíveis no sistema.")
