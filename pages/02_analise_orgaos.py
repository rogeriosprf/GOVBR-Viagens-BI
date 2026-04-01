import streamlit as st
import polars as pl
import plotly.express as px
import plotly.graph_objects as go
from src.connector import get_lazy_dataset

st.set_page_config(page_title="Análise por Órgão", page_icon="🏢", layout="wide")

st.title("🏢 Distribuição e Ranking por Órgão")
st.markdown("""
Esta visão detalha como os gastos estão concentrados entre os diferentes órgãos do Governo Federal, 
permitindo identificar os maiores utilizadores e a eficiência de gastos (Ticket Médio).
""")
st.markdown("---")

with st.spinner("Carregando dados de concentração e ranking..."):
    lf_concentracao = get_lazy_dataset("concentracao_gasto_orgaos_periodo")
    lf_ranking = get_lazy_dataset("ranking_orgaos_ano_participacao")

    if lf_concentracao is not None and lf_ranking is not None:
        # Coletando dados (Datasets de tamanho médio, ~35 a 350 linhas)
        df_c = lf_concentracao.sort("ordem_valor_total").collect()
        df_r = lf_ranking.collect()

        # --- SEÇÃO 1: CONCENTRAÇÃO (PARETO) ---
        st.subheader("📊 Concentração de Gastos (Pareto)")
        
        fig_pareto = go.Figure()

        # Barras de Participação Percentual
        fig_pareto.add_trace(go.Bar(
            x=df_c["orgao"],
            y=df_c["participacao_percentual"],
            name="Participação Individual (%)",
            marker_color='#1f77b4'
        ))

        # Linha de Participação Acumulada
        fig_pareto.add_trace(go.Scatter(
            x=df_c["orgao"],
            y=df_c["participacao_acumulada_percentual"],
            name="Participação Acumulada (%)",
            yaxis="y2",
            line=dict(color="#d62728", width=3)
        ))

        fig_pareto.update_layout(
            title="Curva de Concentração de Gastos por Órgão",
            yaxis=dict(title="Participação (%)", side="left", showgrid=False),
            yaxis2=dict(title="Acumulado (%)", side="right", overlaying="y", range=[0, 105], showgrid=False),
            xaxis=dict(tickangle=-45),
            legend=dict(orientation="h", y=1.1)
        )
        st.plotly_chart(fig_pareto, use_container_width=True)

        # --- SEÇÃO 2: RANKINGS DE EFICIÊNCIA ---
        st.markdown("---")
        col_rank1, col_rank2 = st.columns(2)

        with col_rank1:
            st.subheader("🏆 Top 10 - Maior Gasto Total")
            top_10_gasto = df_c.head(10).to_pandas()
            fig_top_gasto = px.bar(top_10_gasto, x="valor_total", y="orgao", orientation='h',
                                   color="valor_total", color_continuous_scale="Viridis",
                                   labels={"valor_total": "Total (R$)", "orgao": "Órgão"})
            fig_top_gasto.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_top_gasto, use_container_width=True)

        with col_rank2:
            st.subheader("🎫 Top 10 - Maior Ticket Médio")
            # Filtrando apenas órgãos com volume relevante para evitar distorções
            top_10_ticket = df_c.filter(pl.col("qtd_viagens") > 10).sort("ticket_medio", descending=True).head(10).to_pandas()
            fig_top_ticket = px.bar(top_10_ticket, x="ticket_medio", y="orgao", orientation='h',
                                    color="ticket_medio", color_continuous_scale="Reds")
            fig_top_ticket.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_top_ticket, use_container_width=True)

        # --- TABELA DE DADOS ---
        with st.expander("🔍 Ver Dados Completos de Ranking"):
            st.dataframe(df_c.to_pandas(), use_container_width=True)

    else:
        st.error("Erro ao carregar dados dos órgãos.")