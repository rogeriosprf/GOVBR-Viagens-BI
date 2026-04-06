import streamlit as st
import polars as pl
import plotly.express as px
import plotly.graph_objects as go
from src.connector import get_lazy_dataset
from src.ui import apply_dashboard_style, render_status_card

st.set_page_config(page_title="Auditoria e Compliance", page_icon="🚨", layout="wide")
apply_dashboard_style()

st.sidebar.header("Filtros de Auditoria")

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

        ano_options = sorted(list(dict.fromkeys(df_a.select(pl.col("ano_referencia")).to_series().to_list())))
        selected_years = st.sidebar.multiselect("Ano", ano_options, default=ano_options)
        if not selected_years:
            selected_years = ano_options

        df_a = df_a.filter(pl.col("ano_referencia").is_in(selected_years))
        df_q = df_q.filter(pl.col("ano_referencia").is_in(selected_years))

        latest_alert = df_a.tail(1)
        outliers_value = int(latest_alert["qtd_outliers_valor"][0]) if latest_alert.height > 0 else 0
        urgente_value = int(latest_alert["qtd_urgente_sem_justificativa"][0]) if latest_alert.height > 0 else 0

        latest_quality = df_q.tail(1)
        perc_orgao = latest_quality["perc_orgao_invalido"][0] if latest_quality.height > 0 else 0.0
        perc_valor = latest_quality["perc_valor_invalido"][0] if latest_quality.height > 0 else 0.0
        max_issue = max(perc_orgao, perc_valor)

        card_col1, card_col2, card_col3, card_col4 = st.columns(4)
        with card_col1:
            st.markdown(
                render_status_card(
                    "Outliers de Valor",
                    f"{outliers_value:,}",
                    "Viagens com gasto muito acima da média",
                    "critical" if outliers_value > 250 else "warning",
                ),
                unsafe_allow_html=True,
            )
        with card_col2:
            st.markdown(
                render_status_card(
                    "Urgências sem Justificativa",
                    f"{urgente_value:,}",
                    "Casos sem justificativa operacional",
                    "critical" if urgente_value > 120 else "warning",
                ),
                unsafe_allow_html=True,
            )
        with card_col3:
            st.markdown(
                render_status_card(
                    "Inconsistências Críticas",
                    f"{max_issue:.1f}%",
                    "Maior percentual de falhas por categoria",
                    "warning" if max_issue > 8 else "info",
                ),
                unsafe_allow_html=True,
            )
        with card_col4:
            st.markdown(
                render_status_card(
                    "Confiabilidade de Pipeline",
                    f"{100 - max_issue:.1f}%",
                    "Qualidade estimada dos dados processados",
                    "success" if max_issue < 5 else "warning",
                ),
                unsafe_allow_html=True,
            )

        st.subheader("🚩 Alertas de Compliance Operacional")
        col1, col2 = st.columns(2)

        with col1:
            fig_outliers = px.line(
                df_a,
                x="ano_referencia",
                y="qtd_outliers_valor",
                title="Evolução de Outliers de Valor",
                markers=True,
                line_shape="spline",
                color_discrete_sequence=["#EF553B"],
                template="plotly_dark",
            )
            fig_outliers.update_traces(
                hovertemplate="Ano: %{x}<br>Outliers: %{y:,}<extra></extra>",
                line=dict(width=3),
            )
            fig_outliers.update_layout(
                plot_bgcolor="#090d14",
                paper_bgcolor="#090d14",
                margin=dict(l=20, r=20, t=50, b=20),
            )
            st.plotly_chart(fig_outliers, use_container_width=True)

        with col2:
            fig_urgente = px.bar(
                df_a,
                x="ano_referencia",
                y="qtd_urgente_sem_justificativa",
                title="Viagens Urgentes sem Justificativa",
                color_discrete_sequence=["#FFA15A"],
                template="plotly_dark",
            )
            fig_urgente.update_traces(
                hovertemplate="Ano: %{x}<br>Urgências: %{y:,}<extra></extra>",
                marker_line_width=0,
            )
            fig_urgente.update_layout(
                plot_bgcolor="#090d14",
                paper_bgcolor="#090d14",
                margin=dict(l=20, r=20, t=50, b=20),
            )
            st.plotly_chart(fig_urgente, use_container_width=True)

        st.markdown("---")
        st.subheader("⚙️ Integridade Técnica do Pipeline")

        df_erros = df_q.select([
            "ano_referencia",
            "perc_orgao_invalido",
            "perc_valor_invalido",
            "perc_data_inicio_invalida",
            "perc_id_invalido",
        ]).to_pandas().melt(id_vars="ano_referencia", var_name="Tipo de Erro", value_name="Percentual")

        fig_dq = px.bar(
            df_erros,
            x="ano_referencia",
            y="Percentual",
            color="Tipo de Erro",
            title="Distribuição de Inconsistências Detectadas (%)",
            barmode="stack",
            template="plotly_dark",
            color_discrete_sequence=["#636EFA", "#EF553B", "#00CC96", "#FFA15A"],
        )
        fig_dq.update_layout(
            plot_bgcolor="#090d14",
            paper_bgcolor="#090d14",
            margin=dict(l=20, r=20, t=50, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        fig_dq.update_traces(hovertemplate="Ano: %{x}<br>%{fullData.name}: %{y:.2f}%<extra></extra>")
        st.plotly_chart(fig_dq, use_container_width=True)

        with st.expander("🔍 Detalhes da Auditoria (Tabela Bruta)"):
            st.write("Dados de Alertas Anuais")
            st.dataframe(df_a, use_container_width=True)

            st.write("Dados de Qualidade de Dados (Inconsistências)")
            st.dataframe(df_q, use_container_width=True)
    else:
        st.error("Não foi possível carregar os dados de auditoria.")
