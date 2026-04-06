import streamlit as st
import pandas as pd
import polars as pl
import plotly.graph_objects as go
from src.connector import get_lazy_dataset
from src.ui import apply_dashboard_style, render_metric_card

st.set_page_config(page_title="Main App", page_icon="🏠", layout="wide")
apply_dashboard_style()

# --- FUNÇÃO DE FORMATAÇÃO (Para os Cards) ---
def format_brl(value):
    if value >= 1_000_000_000_000:
        return f"R$ {value / 1_000_000_000_000:.2f} Tri"
    elif value >= 1_000_000_000:
        return f"R$ {value / 1_000_000_000:.2f} Bi"
    elif value >= 1_000_000:
        return f"R$ {value / 1_000_000:.2f} Mi"
    return f"R$ {value:,.2f}"

st.sidebar.header("Filtros de Visão")

st.title("🏠 Dashboard Executivo de Viagens")
st.markdown("---")

with st.spinner("Sincronizando com Azure Data Lake..."):
    lf_variacao = get_lazy_dataset("kpi_anual_variacao")
    lf_orgaos = get_lazy_dataset("agg_viagens_mensal_orgao")

    if lf_variacao is not None:
        df_variacao = lf_variacao.sort("ano_referencia").collect()

        ano_options = sorted(list(dict.fromkeys(df_variacao.select(pl.col("ano_referencia")).to_series().to_list())))
        selected_years = st.sidebar.multiselect("Ano", ano_options, default=ano_options)

        # Carregar opções de órgãos
        orgao_options = ["Todos"]
        if lf_orgaos is not None:
            try:
                df_orgaos = lf_orgaos.select("orgao").unique().collect()
                orgao_options.extend(sorted(df_orgaos["orgao"].to_list()))
            except Exception as e:
                print(f"Aviso: Não foi possível carregar órgãos: {e}")

        selected_orgao = st.sidebar.selectbox("Órgão", orgao_options, index=0)
        selected_faixa = st.sidebar.selectbox(
            "Faixa de Valor",
            [
                "Todos",
                "Até R$ 10k",
                "R$ 10k - R$ 50k",
                "R$ 50k - R$ 150k",
                "Acima de R$ 150k"
            ],
            index=0,
        )

        if not selected_years:
            selected_years = ano_options

        # Aplicar filtros
        df_filtered = df_variacao.filter(pl.col("ano_referencia").is_in(selected_years))

        # Filtragem por órgão (se não for "Todos")
        if selected_orgao != "Todos":
            try:
                lf_orgao_detalhes = get_lazy_dataset("agg_viagens_mensal_orgao")
                if lf_orgao_detalhes is not None:
                    df_orgao_detalhes = lf_orgao_detalhes.filter(
                        (pl.col("orgao") == selected_orgao)
                    ).with_columns(
                        ano_referencia = pl.col("mes_referencia").str.slice(0, 4).cast(pl.Int32)
                    ).filter(
                        pl.col("ano_referencia").is_in(selected_years)
                    ).group_by("ano_referencia").agg([
                        pl.col("valor_total").sum().alias("valor_total"),
                        pl.col("qtd_viagens").sum().alias("qtd_viagens"),
                        (pl.col("valor_total").sum() / pl.col("qtd_viagens").sum()).alias("ticket_medio"),
                        pl.lit(None).alias("valor_total_ano_anterior"),
                        pl.lit(None).alias("qtd_viagens_ano_anterior"),
                        pl.lit(None).alias("variacao_valor_percentual"),
                        pl.lit(None).alias("variacao_qtd_percentual"),
                    ]).sort("ano_referencia").collect()

                    if len(df_orgao_detalhes) > 0:
                        df_filtered = df_orgao_detalhes
            except Exception as e:
                print(f"Aviso: Não foi possível filtrar por órgão: {e}")
                # Mantém df_filtered original em caso de erro

        df_resumo = df_filtered.select([
            pl.col("valor_total").sum().alias("valor_total"),
            pl.col("qtd_viagens").sum().alias("qtd_viagens"),
            pl.col("ticket_medio").mean().alias("ticket_medio"),
            pl.col("ano_referencia").n_unique().alias("anos_cobertos"),
        ])

        st.markdown(
            f"<div style='padding: 0.5rem 0 0.75rem; color:#cbd5e1;'>"
            f"Escopo selecionado: <strong>{', '.join(str(y) for y in selected_years)}</strong> · "
            f"Órgão: <strong>{selected_orgao}</strong> · "
            f"Faixa: <strong>{selected_faixa}</strong></div>",
            unsafe_allow_html=True,
        )

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(
                render_metric_card(
                    "Gasto Total",
                    format_brl(df_resumo["valor_total"][0]),
                    "Agregado no período selecionado"
                ),
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                render_metric_card(
                    "Total de Viagens",
                    f"{df_resumo['qtd_viagens'][0] / 1_000_000:.2f} Mi",
                    "Volume global de deslocamentos"
                ),
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                render_metric_card(
                    "Ticket Médio",
                    f"R$ {df_resumo['ticket_medio'][0]:,.2f}",
                    "Custo médio por viagem"
                ),
                unsafe_allow_html=True,
            )
        with c4:
            st.markdown(
                render_metric_card(
                    "Anos Cobertos",
                    str(df_resumo["anos_cobertos"][0]),
                    "Horizonte temporal da análise"
                ),
                unsafe_allow_html=True,
            )

        st.markdown("### 📊 Tendência e Crescimento")

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=df_filtered["ano_referencia"],
                y=df_filtered["valor_total"],
                name="Gasto Total (R$)",
                marker_color="#4f7cff",
                opacity=0.92,
                hovertemplate="Ano: %{x}<br>Gasto Total: %{y:$,.2f}<extra></extra>",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df_filtered["ano_referencia"],
                y=df_filtered["variacao_valor_percentual"],
                name="Variação %",
                mode="lines+markers+text",
                text=[f"{v:.1f}%" if v is not None else "" for v in df_filtered["variacao_valor_percentual"]],
                textposition="top center",
                yaxis="y2",
                line=dict(color="#72d6ff", width=3),
                hovertemplate="Ano: %{x}<br>Variação: %{y:.1f}%<extra></extra>",
            )
        )

        fig.update_layout(
            template="plotly_dark",
            title="Evolução de Gastos vs Variação Anual",
            xaxis=dict(title="Ano de Referência", showgrid=False),
            yaxis=dict(title="Gasto Total (R$)", showgrid=False),
            yaxis2=dict(
                title="Variação (%)",
                overlaying="y",
                side="right",
                ticksuffix="%",
                showgrid=False,
            ),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode="x unified",
            plot_bgcolor="#090d14",
            paper_bgcolor="#090d14",
            margin=dict(l=24, r=24, t=72, b=24),
            height=520,
        )

        st.plotly_chart(fig, use_container_width=True)

        with st.expander("🔍 Ver Detalhes dos Dados por Ano"):
            mapa_colunas = {
                "ano_referencia": "Ano",
                "qtd_viagens": "Qtd. Viagens",
                "valor_total": "Gasto Total (R$)",
                "ticket_medio": "Ticket Médio (R$)",
                "valor_total_ano_anterior": "Gasto Ano Anterior (R$)",
                "qtd_viagens_ano_anterior": "Viagens Ano Anterior",
                "variacao_valor_percentual": "Var. Gasto (%)",
                "variacao_qtd_percentual": "Var. Qtd (%)",
            }
            df_display = df_filtered.to_pandas().rename(columns=mapa_colunas)
            st.dataframe(
                df_display.style.format({
                    "Gasto Total (R$)": lambda x: f"R$ {x:,.2f}" if pd.notna(x) else "",
                    "Ticket Médio (R$)": lambda x: f"R$ {x:,.2f}" if pd.notna(x) else "",
                    "Gasto Ano Anterior (R$)": lambda x: f"R$ {x:,.2f}" if pd.notna(x) else "",
                    "Var. Gasto (%)": lambda x: f"{x:.2f}%" if pd.notna(x) else "",
                    "Var. Qtd (%)": lambda x: f"{x:.2f}%" if pd.notna(x) else "",
                    "Qtd. Viagens": lambda x: f"{x:,.0f}" if pd.notna(x) else "",
                    "Viagens Ano Anterior": lambda x: f"{x:,.0f}" if pd.notna(x) else "",
                }),
                use_container_width=True,
            )
    else:
        st.error("Erro ao carregar dados.")


def format_brl(value):
    if value >= 1_000_000_000_000:
        return f"R$ {value / 1_000_000_000_000:.2f} Tri"
    elif value >= 1_000_000_000:
        return f"R$ {value / 1_000_000_000:.2f} Bi"
    elif value >= 1_000_000:
        return f"R$ {value / 1_000_000:.2f} Mi"
    return f"R$ {value:,.2f}"
