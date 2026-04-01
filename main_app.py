import streamlit as st
import polars as pl
import plotly.graph_objects as go
from src.connector import get_lazy_dataset

st.set_page_config(page_title="BI GovBR - Home", page_icon="🏠", layout="wide")

# --- FUNÇÃO DE FORMATAÇÃO (Para os Cards) ---
def format_brl(value):
    if value >= 1_000_000_000_000:
        return f"R$ {value / 1_000_000_000_000:.2f} Tri"
    elif value >= 1_000_000_000:
        return f"R$ {value / 1_000_000_000:.2f} Bi"
    elif value >= 1_000_000:
        return f"R$ {value / 1_000_000:.2f} Mi"
    return f"R$ {value:,.2f}"

st.title("🏠 Dashboard Executivo de Viagens")
st.markdown("---")

with st.spinner("Sincronizando com Azure Data Lake..."):
    lf_resumo = get_lazy_dataset("kpi_resumo_periodo")
    lf_variacao = get_lazy_dataset("kpi_anual_variacao")
    
    if lf_resumo is not None and lf_variacao is not None:
        df_resumo = lf_resumo.collect()
        df_variacao = lf_variacao.sort("ano_referencia").collect()

        # --- CARDS REESTILIZADOS ---
        c1, c2, c3, c4 = st.columns(4)
        
        # Usando containers para garantir que o estilo fique uniforme
        with c1:
            st.metric("Gasto Total", format_brl(df_resumo['valor_total'][0]))
        with c2:
            st.metric("Total Viagens", f"{df_resumo['qtd_viagens'][0] / 1_000_000:.2f} Mi")
        with c3:
            st.metric("Ticket Médio", f"R$ {df_resumo['ticket_medio'][0]:,.2f}")
        with c4:
            st.metric("Anos Cobertos", df_resumo['anos_cobertos'][0])

        st.markdown("### 📊 Tendência e Crescimento")

        # --- GRÁFICO AVANÇADO (Barras + Linha) ---
        fig = go.Figure()

        # Barras de Gasto Total
        fig.add_trace(go.Bar(
            x=df_variacao["ano_referencia"],
            y=df_variacao["valor_total"],
            name="Gasto Total (R$)",
            marker_color='#1f77b4',
            opacity=0.8
        ))

        # Linha de Variação % (Eixo Secundário)
        fig.add_trace(go.Scatter(
            x=df_variacao["ano_referencia"],
            y=df_variacao["variacao_valor_percentual"],
            name="Variação %",
            mode='lines+markers+text',
            text=[f"{v:.1f}%" if v else "" for v in df_variacao["variacao_valor_percentual"]],
            textposition="top center",
            yaxis="y2",
            line=dict(color='#ff7f0e', width=3)
        ))

        fig.update_layout(
            title="Evolução de Gastos vs Variação Anual",
            xaxis=dict(title="Ano de Referência"),
            yaxis=dict(title="Gasto Total (R$)", side="left"),
            yaxis2=dict(title="Variação (%)", side="right", overlaying="y", ticksuffix="%"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode="x unified",
            margin=dict(l=20, r=20, t=60, b=20),
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

        # --- TABELA TÉCNICA ---
        with st.expander("🔍 Ver Tabela de Dados"):
            st.dataframe(df_variacao.to_pandas(), use_container_width=True)
    else:
        st.error("Erro ao carregar dados.")