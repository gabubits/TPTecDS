# import streamlit as st
# import pandas as pd
# from bases.trat_agua import trat_agua

# st.set_page_config('DataSaúde', ':bar_chart:')

# bases_values = ['TRAT_AGUA']
# bases_labels = ['Tratamento de água']

# st.sidebar.markdown('''# :bar_chart: DataSaúde\n\nPortal de **dados** e **estatísticas** sobre a saúde.''')
# select_filtro_base = st.sidebar.selectbox('Selecione o que gostaria de saber sobre a saúde:\n\n', bases_values, placeholder='Selecione uma área da saúde', format_func=lambda x: bases_labels[bases_values.index(x)])

# if select_filtro_base == bases_values[0]:
#     trat_agua()
# 


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import folium
from streamlit_folium import folium_static
import json

# Configuração da página
st.set_page_config(page_title='DataSaúde', page_icon=':bar_chart:')

# Sidebar
st.sidebar.markdown('''# :bar_chart: DataSaúde
Portal de **dados** e **estatísticas** sobre a saúde.''')

bases_values = ['TRAT_AGUA']
bases_labels = ['Tratamento de água']

select_filtro_base = st.sidebar.selectbox(
    'Selecione o que gostaria de saber sobre a saúde:\n\n',
    bases_values,
    format_func=lambda x: bases_labels[bases_values.index(x)]
)

# Função para carregar e tratar os dados
@st.cache_data
def carregar_dados():
    df = pd.read_csv('trat_mg.csv', encoding='utf-8', dtype={'COD_IBGE': str, 'ANO': str})
    for col in ['CANALIZACAO', 'CARROPIPA', 'FONTE', 'CHAFARIZ', 'CISTERNA',
                'OUTRA_ETP', 'OUTRO_DESINF', 'OUTRO_SUPRIMENTO']:
        df[col] = df[col].fillna('N')
    for col in ['VAZAO_AGUA', 'NUM_FILTROS']:
        df[col] = df[col].fillna(0.0)
    return df

# Função para carregar o GeoJSON
@st.cache_data
def carregar_geojson():
    with open('geojs-31-mun.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Executa apenas se "Tratamento de água" for selecionado
if select_filtro_base == 'TRAT_AGUA':
    # Carrega os dados
    tratamento = carregar_dados()
    geojson_data = carregar_geojson()

    # Cria abas para exibir informações gerais e consulta
    tabEstats, tabConsulta = st.tabs([":chart_with_upwards_trend: Informações gerais", ":memo: Consulta"])

    with tabEstats:
        st.header(":chart_with_upwards_trend: Informações gerais")
        st.write(f"Total de registros: {len(tratamento)}")

    with tabConsulta:
        st.header(":memo: Consulta")

        # Opções de filtro: ano e categoria
        anos_para_filtro = ['Todos'] + sorted(tratamento['ANO'].unique())
        filtro_colunas = [col for col in tratamento.columns if tratamento[col].nunique() < 10]

        col_ano, col_coluna = st.columns(2)
        with col_ano:
            select_filtro_ano = st.selectbox('Selecione um ano:', anos_para_filtro)
        with col_coluna:
            select_filtro_coluna = st.selectbox('Selecione uma categoria:', filtro_colunas)

        # Filtragem dos dados conforme o ano selecionado
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
        folium_static(m)
