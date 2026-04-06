import streamlit as st
import polars as pl
import plotly.express as px
from src.connector import get_lazy_dataset
from src.ui import apply_dashboard_style

st.set_page_config(page_title="Perfil dos Viajantes", page_icon="👤", layout="wide")
apply_dashboard_style()

st.sidebar.header("Filtros de Visão")

st.title("👤 Análise de Perfil dos Viajantes")
st.markdown("""
Esta página processa **976.767 registros** de viajantes únicos. 
Utilizamos processamento em streaming para identificar padrões de consumo e 'Heavy Users' do sistema.
""")
st.markdown("---")

with st.spinner("Processando Big Data (Polars Streaming Engine)..."):
    lf_viajantes = get_lazy_dataset("perfil_viajantes_periodo")

    if lf_viajantes is not None:
        stats = lf_viajantes.select(
            pl.col("qtd_viagens").min().alias("min_viagens"),
            pl.col("qtd_viagens").max().alias("max_viagens")
        ).collect()

        min_viagens = int(stats["min_viagens"][0])
        max_viagens = int(stats["max_viagens"][0])

        selected_range = st.sidebar.slider(
            "Intervalo de Viagens",
            min_viagens,
            min(max_viagens, 100),
            (min_viagens, min(20, max_viagens)),
            step=1,
        )

        st.markdown(
            f"<div style='padding: 0.5rem 0 0.75rem; color:#cbd5e1;'>"
            f"Intervalo de viagens selecionado: <strong>{selected_range[0]} - {selected_range[1]}</strong>"
            f"</div>",
            unsafe_allow_html=True,
        )

        df_filtered = (
            lf_viajantes
            .filter(pl.col("qtd_viagens").is_between(selected_range[0], selected_range[1]))
        )

        st.subheader("📊 Distribuição de Viagens por Pessoa")
        df_dist = (
            df_filtered
            .group_by("qtd_viagens")
            .agg(pl.len().alias("total_pessoas"))
            .sort("qtd_viagens")
            .limit(20)
            .collect(engine="streaming")
        )

        fig_hist = px.bar(
            df_dist.to_pandas(),
            x="qtd_viagens",
            y="total_pessoas",
            title="Frequência: Quantas pessoas fazem X viagens?",
            labels={"qtd_viagens": "Nº de Viagens", "total_pessoas": "Qtd de Pessoas"},
            color_discrete_sequence=["#60a5fa"],
            template="plotly_dark",
        )
        fig_hist.update_layout(plot_bgcolor="#090d14", paper_bgcolor="#090d14", margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_hist, use_container_width=True)

        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("💰 Top 10 - Maior Gasto Acumulado")
            top_gastadores = (
                df_filtered
                .sort("valor_total", descending=True)
                .head(10)
                .with_columns(
                    pl.col("nome_viajante").str.slice(0, 10).alias("viajante_anon")
                )
                .collect(engine="streaming")
            )

            fig_top_gasto = px.bar(
                top_gastadores.to_pandas(),
                x="valor_total",
                y="viajante_anon",
                orientation='h',
                title="Top 10 Viajantes (R$)",
                color="valor_total",
                color_continuous_scale="Blues",
                template="plotly_dark",
            )
            fig_top_gasto.update_layout(plot_bgcolor="#090d14", paper_bgcolor="#090d14", margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_top_gasto, use_container_width=True)

        with col2:
            st.subheader("📈 Top 10 - Mais Frequentes")
            top_frequencia = (
                df_filtered
                .sort("qtd_viagens", descending=True)
                .head(10)
                .with_columns(
                    pl.col("nome_viajante").str.slice(0, 10).alias("viajante_anon")
                )
                .collect(engine="streaming")
            )

            fig_top_freq = px.bar(
                top_frequencia.to_pandas(),
                x="qtd_viagens",
                y="viajante_anon",
                orientation='h',
                title="Top 10 Viajantes (Qtd)",
                color="qtd_viagens",
                color_continuous_scale="Purples",
                template="plotly_dark",
            )
            fig_top_freq.update_layout(plot_bgcolor="#090d14", paper_bgcolor="#090d14", margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_top_freq, use_container_width=True)

        st.markdown("---")
        st.subheader("🔍 Pesquisa de Perfil")
        busca = st.text_input("Digite as iniciais de um nome para filtrar (Ex: JOAO):")

        if busca:
            df_busca = (
                df_filtered
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
