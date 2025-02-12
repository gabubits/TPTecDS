import streamlit as st
import pandas as pd
from bases.trat_agua import trat_agua

st.set_page_config('DataSaúde', ':bar_chart:')

bases_values = ['TRAT_AGUA']
bases_labels = ['Tratamento de água']

st.sidebar.markdown('''# :bar_chart: DataSaúde\n\nPortal de **dados** e **estatísticas** sobre a saúde.''')
select_filtro_base = st.sidebar.selectbox('Selecione o que gostaria de saber sobre a saúde:\n\n', bases_values, placeholder='Selecione uma área da saúde', format_func=lambda x: bases_labels[bases_values.index(x)])

if select_filtro_base == bases_values[0]:
    trat_agua()