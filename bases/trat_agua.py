import pandas as pd
import streamlit as st

def trat_agua():
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

    tabEstats, tabConsulta = st.tabs([":chart_with_upwards_trend: Informações gerais", ":memo: Consulta"])
    with tabEstats:
        st.header(":chart_with_upwards_trend: Informações gerais")
    with tabConsulta:
        st.header(":memo: Consulta")
        
        anos_para_filtro = tratamento['ANO'].unique()
        filtro_colunas = []

        # Ignorar coluna OUTRO_DESINF pois não trás mais informações de qual outra desinfecção é feita
        # Ignorar OUTRA_ETP e OUTRO_SUPRIMENTO pelo mesmo motivo
        ignorar_coluna = ['OUTRO_DESINF', 'OUTRA_ETP', 'OUTRO_SUPRIMENTO']

        for coluna in tratamento.columns:
            if coluna in ignorar_coluna: continue
            if len(tratamento[coluna].unique()) < 3:
                filtro_colunas.append(coluna)
        filtro_labels = ['Forma de abastecimento', 'Captação Superficial', 'Capetação Subterrânea', 'Captação da água de chuva', 'Etapa de pré oxidação', 'Etapa de mistura rápida / coagulação', 'Etapa de Floculação', 'Etapa de decantação', 'Etapa de flotação', 'Impedimento de monitaramento', 'Etapa de desinfecção', 'Desinfecção com Cloro Gás ou Hipoclorito', 'Desinfecção com isocianuratos', 'Desinfecção com Cloramina', 'Dexinfecção com dióxido de cloro', 'Desinfecção com ozônio', 'Desinfecção com UV', 'RAD Cloro residual livre', 'RAD dióxido de cloro', 'RAD cloro residual combinado', 'Polímero com epicolidrina', 'Polímero com acrilamida', 'Etapa de fluoretação', 'Etapa de desfluoretação', 'Carro pipa', 'Chafariz', 'Fonte', 'Cisterna', 'Canalização']
        
        col_ano, col_coluna = st.columns(2)

        with col_ano:
            select_filtro_ano = st.selectbox('Selecione um ano:', anos_para_filtro, index=None, placeholder='Selecione um ano')
        with col_coluna:
            select_filtro_coluna = st.selectbox('Selecione uma categoria:', filtro_colunas, format_func=lambda x: filtro_labels[filtro_colunas.index(x)], index=None, placeholder='Selecione uma categoria')