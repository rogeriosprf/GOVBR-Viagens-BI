import streamlit as st
import polars as pl
import plotly.express as px
from src.connector import get_lazy_dataset

st.set_page_config(page_title="Perfil dos Viajantes", page_icon="👤", layout="wide")

st.title("👤 Análise de Perfil dos Viajantes")
st.markdown("""
Esta página processa **976.767 registros** de viajantes únicos. 
Utilizamos processamento em streaming para identificar padrões de consumo e 'Heavy Users' do sistema.
""")
st.markdown("---")

with st.spinner("Processando Big Data (Polars Streaming Engine)..."):
    lf_viajantes = get_lazy_dataset("perfil_viajantes_periodo")

    if lf_viajantes is not None:
        # 1. Distribuição de Frequência (Histograma)
        # Calculamos a distribuição sem trazer tudo para a RAM
        st.subheader("📊 Distribuição de Viagens por Pessoa")
        
        # Agrupando para ver quantas pessoas viajam X vezes
        df_dist = (
            lf_viajantes
            .group_by("qtd_viagens")
            .agg(pl.len().alias("total_pessoas"))
            .sort("qtd_viagens")
            .limit(20) # Focamos na cauda curta para o gráfico
            .collect(engine="streaming")
        )

        fig_hist = px.bar(df_dist.to_pandas(), x="qtd_viagens", y="total_pessoas",
                          title="Frequência: Quantas pessoas fazem X viagens?",
                          labels={"qtd_viagens": "Nº de Viagens", "total_pessoas": "Qtd de Pessoas"},
                          color_discrete_sequence=["#636EFA"])
        st.plotly_chart(fig_hist, use_container_width=True)

        # 2. Top 10 'Heavy Users' (Maiores Gastos Acumulados)
        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("💰 Top 10 - Maior Gasto Acumulado")
            # Aqui mostramos apenas as iniciais ou nome parcial para manter o portfólio ético
            top_gastadores = (
                lf_viajantes
                .sort("valor_total", descending=True)
                .head(10)
                .with_columns(
                    pl.col("nome_viajante").str.slice(0, 10).alias("viajante_anon")
                )
                .collect(engine="streaming")
            )
            
            fig_top_gasto = px.bar(top_gastadores.to_pandas(), x="valor_total", y="viajante_anon", 
                                   orientation='h', title="Top 10 Viajantes (R$)",
                                   color="valor_total", color_continuous_scale="GnBu")
            st.plotly_chart(fig_top_gasto, use_container_width=True)

        with col2:
            st.subheader("📈 Top 10 - Mais Frequentes")
            top_frequencia = (
                lf_viajantes
                .sort("qtd_viagens", descending=True)
                .head(10)
                .with_columns(
                    pl.col("nome_viajante").str.slice(0, 10).alias("viajante_anon")
                )
                .collect(engine="streaming")
            )
            
            fig_top_freq = px.bar(top_frequencia.to_pandas(), x="qtd_viagens", y="viajante_anon", 
                                  orientation='h', title="Top 10 Viajantes (Qtd)",
                                  color="qtd_viagens", color_continuous_scale="Purples")
            st.plotly_chart(fig_top_freq, use_container_width=True)

        # 3. Tabela de Busca (Otimizada)
        st.markdown("---")
        st.subheader("🔍 Pesquisa de Perfil")
        busca = st.text_input("Digite as iniciais de um nome para filtrar (Ex: JOAO):")
        
        if busca:
            df_busca = (
                lf_viajantes
                .filter(pl.col("nome_viajante").str.contains(busca.upper()))
                .sort("valor_total", descending=True)
                .head(50)
                .collect()
            )
            st.dataframe(df_busca.to_pandas(), use_container_width=True)
        else:
            st.info("Use a busca acima para filtrar registros específicos na massa de 1 milhão de linhas.")

    else:
        st.error("Erro ao carregar a massa de dados de viajantes.")