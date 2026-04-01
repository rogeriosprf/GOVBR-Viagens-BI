import streamlit as st
import polars as pl
import plotly.express as px
import plotly.graph_objects as go
from src.connector import get_lazy_dataset

st.set_page_config(page_title="Auditoria e Compliance", page_icon="🚨", layout="wide")

st.title("🚨 Auditoria e Qualidade de Dados")
st.markdown("""
Esta visão apresenta a integridade dos dados processados e alertas operacionais sobre gastos fora da curva (outliers) 
e viagens urgentes sem a devida justificativa.
""")
st.markdown("---")

with st.spinner("Analisando qualidade dos dados no Data Lake..."):
    lf_qualidade = get_lazy_dataset("qualidade_dados_anual")
    lf_alertas = get_lazy_dataset("alerta_operacional_anual")

    if lf_qualidade is not None and lf_alertas is not None:
        df_q = lf_qualidade.sort("ano_referencia").collect()
        df_a = lf_alertas.sort("ano_referencia").collect()

        # --- SEÇÃO 1: ALERTAS OPERACIONAIS (COMPLIANCE) ---
        st.subheader("🚩 Alertas de Compliance Operacional")
        col1, col2 = st.columns(2)

        with col1:
            # Gráfico de Outliers de Valor
            fig_outliers = px.line(df_a, x="ano_referencia", y="qtd_outliers_valor",
                                    title="Evolução de Outliers de Valor (Viagens muito acima da média)",
                                    markers=True, line_shape="spline", color_discrete_sequence=["#EF553B"])
            st.plotly_chart(fig_outliers, use_container_width=True)

        with col2:
            # Gráfico de Viagens Urgentes sem Justificativa
            fig_urgente = px.bar(df_a, x="ano_referencia", y="qtd_urgente_sem_justificativa",
                                  title="Viagens Urgentes sem Justificativa",
                                  color_discrete_sequence=["#FFA15A"])
            st.plotly_chart(fig_urgente, use_container_width=True)

        # --- SEÇÃO 2: QUALIDADE TÉCNICA (DATA QUALITY) ---
        st.markdown("---")
        st.subheader("⚙️ Integridade Técnica do Pipeline")
        
        # Criando um gráfico de barras empilhadas para mostrar os tipos de erros encontrados
        # Vamos derreter (melt) o dataframe para o Plotly ler as categorias de erro
        df_erros = df_q.select([
            "ano_referencia", "perc_orgao_invalido", "perc_valor_invalido", 
            "perc_data_inicio_invalida", "perc_id_invalido"
        ]).to_pandas().melt(id_vars="ano_referencia", var_name="Tipo de Erro", value_name="Percentual")

        fig_dq = px.bar(df_erros, x="ano_referencia", y="Percentual", color="Tipo de Erro",
                        title="Distribuição de Inconsistências Detectadas (%)",
                        barmode="stack", color_discrete_sequence=px.colors.qualitative.Pastel)
        
        st.plotly_chart(fig_dq, use_container_width=True)

        # --- DETALHES TÉCNICOS ---
        with st.expander("🔍 Detalhes da Auditoria (Tabela Bruta)"):
            st.write("Dados de Alertas Anuais")
            st.dataframe(df_a, use_container_width=True)
            
            st.write("Dados de Qualidade de Dados (Inconsistências)")
            st.dataframe(df_q, use_container_width=True)

    else:
        st.error("Não foi possível carregar os dados de auditoria.")