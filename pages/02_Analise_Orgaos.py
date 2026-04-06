import streamlit as st
import polars as pl
import plotly.express as px
import plotly.graph_objects as go
from src.connector import get_lazy_dataset
from src.ui import apply_dashboard_style

st.set_page_config(page_title="Análise por Órgão", page_icon="🏢", layout="wide")
apply_dashboard_style()

st.sidebar.header("Filtros de Visão")

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
        df_c = lf_concentracao.sort("ordem_valor_total").collect()

        ano_options = []
        if "ano_referencia" in df_c.columns:
            ano_options = sorted(list(dict.fromkeys(df_c.select(pl.col("ano_referencia")).to_series().to_list())))
            selected_years = st.sidebar.multiselect("Ano", ano_options, default=ano_options)
            if not selected_years:
                selected_years = ano_options
            df_c = df_c.filter(pl.col("ano_referencia").is_in(selected_years))
        else:
            selected_years = ["Todos"]

        selected_orgao = st.sidebar.selectbox("Órgão", ["Todos"], index=0)

        st.markdown(
            f"<div style='padding: 0.5rem 0 0.75rem; color:#cbd5e1;'>"
            f"Escopo selecionado: <strong>{', '.join(str(y) for y in selected_years)}</strong> · "
            f"Órgão: <strong>{selected_orgao}</strong></div>",
            unsafe_allow_html=True,
        )

        st.subheader("📊 Concentração de Gastos (Pareto)")
        fig_pareto = go.Figure()
        fig_pareto.add_trace(go.Bar(
            x=df_c["orgao"],
            y=df_c["participacao_percentual"],
            name="Participação Individual (%)",
            marker_color='#4f7cff'
        ))
        fig_pareto.add_trace(go.Scatter(
            x=df_c["orgao"],
            y=df_c["participacao_acumulada_percentual"],
            name="Participação Acumulada (%)",
            yaxis="y2",
            line=dict(color="#72d6ff", width=3)
        ))
        fig_pareto.update_layout(
            template="plotly_dark",
            title="Curva de Concentração de Gastos por Órgão",
            yaxis=dict(title="Participação (%)", side="left", showgrid=False),
            yaxis2=dict(title="Acumulado (%)", side="right", overlaying="y", range=[0, 105], showgrid=False),
            xaxis=dict(tickangle=-45),
            legend=dict(orientation="h", y=1.1),
            plot_bgcolor="#090d14",
            paper_bgcolor="#090d14",
            margin=dict(l=24, r=24, t=60, b=24),
        )
        st.plotly_chart(fig_pareto, use_container_width=True)

        st.markdown("---")
        col_rank1, col_rank2 = st.columns(2)

        with col_rank1:
            st.subheader("🏆 Top 10 - Maior Gasto Total")
            top_10_gasto = df_c.head(10).to_pandas()
            fig_top_gasto = px.bar(
                top_10_gasto,
                x="valor_total",
                y="orgao",
                orientation='h',
                color="valor_total",
                color_continuous_scale="Blues",
                labels={"valor_total": "Total (R$)", "orgao": "Órgão"},
                template="plotly_dark",
            )
            fig_top_gasto.update_layout(yaxis={'categoryorder':'total ascending'}, plot_bgcolor="#090d14", paper_bgcolor="#090d14", margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_top_gasto, use_container_width=True)

        with col_rank2:
            st.subheader("🎫 Top 10 - Maior Ticket Médio")
            top_10_ticket = df_c.filter(pl.col("qtd_viagens") > 10).sort("ticket_medio", descending=True).head(10).to_pandas()
            fig_top_ticket = px.bar(
                top_10_ticket,
                x="ticket_medio",
                y="orgao",
                orientation='h',
                color="ticket_medio",
                color_continuous_scale="Teal",
                template="plotly_dark",
            )
            fig_top_ticket.update_layout(yaxis={'categoryorder':'total ascending'}, plot_bgcolor="#090d14", paper_bgcolor="#090d14", margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_top_ticket, use_container_width=True)

        with st.expander("🔍 Ver Dados Completos de Ranking"):
            st.dataframe(df_c.to_pandas(), use_container_width=True)
    else:
        st.error("Erro ao carregar dados dos órgãos.")
