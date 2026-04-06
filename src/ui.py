import streamlit as st

DARK_CSS = """
<style>
:root {
    color-scheme: dark;
}
body, .stApp, .main, .reportview-container .main .block-container, .css-1d391kg {
    background-color: #090d14 !important;
    color: #e7eef7 !important;
}
.css-18ni7ap.e8zbici2 {
    background-color: #090d14 !important;
}
.stSidebar .sidebar-content {
    position: relative;
    padding-top: 120px;
}
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
    border-radius: 18px;
    background-color: #080b12;
}
.stSidebar .sidebar-content {
    background: #07101c;
}
.stSidebar .css-1d391kg {
    background-color: #07101c !important;
}
.metric-card,
.status-card {
    border-radius: 16px;
    background: linear-gradient(180deg, rgba(12,18,33,0.95) 0%, rgba(15,24,44,0.95) 100%);
    border: 1px solid rgba(80, 154, 255, 0.18);
    box-shadow: 0 18px 50px rgba(0, 0, 0, 0.25);
    padding: 16px;
    margin-bottom: 12px;
}
.metric-card:hover,
.status-card:hover {
    transform: translateY(-2px);
}
.metric-card {
    transition: transform 0.15s ease-in-out;
}
.status-card {
    transition: all 0.15s ease-in-out;
}
.metric-title,
.status-title {
    color: #94a3b8;
    font-size: 0.85rem;
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
.metric-value,
.status-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #eef2ff;
    margin-bottom: 4px;
}
.metric-note,
.status-note {
    color: #cbd5e1;
    font-size: 0.85rem;
}
.sidebar-logo {
    text-align: center;
    padding: 12px 0 16px;
    margin-bottom: 18px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    width: 100%;
    z-index: 40;
    background: #07101c;
}
.stSidebar {
    display: flex;
    flex-direction: column;
}
.sidebar-logo h1 {
    margin: 0;
    font-size: 1.35rem;
    letter-spacing: 0.12em;
    color: #60a5fa;
}
.sidebar-logo p {
    margin: 0.2rem 0 0;
    color: #94a3b8;
    font-size: 0.92rem;
}
.sidebar-section {
    padding: 12px 0 0;
}
.status-card.critical { border-left: 5px solid #ff4d6d; }
.status-card.warning { border-left: 5px solid #ffb347; }
.status-card.info { border-left: 5px solid #4f9dff; }
.status-card.success { border-left: 5px solid #34d399; }
</style>
"""


def apply_dashboard_style():
    st.markdown(DARK_CSS, unsafe_allow_html=True)


def render_metric_card(title: str, value: str, note: str = "") -> str:
    return f"""
    <div class='metric-card'>
        <div class='metric-title'>{title}</div>
        <div class='metric-value'>{value}</div>
        <div class='metric-note'>{note}</div>
    </div>
    """


def render_status_card(title: str, value: str, note: str, severity: str = "info") -> str:
    return f"""
    <div class='status-card {severity}'>
        <div class='status-title'>{title}</div>
        <div class='status-value'>{value}</div>
        <div class='status-note'>{note}</div>
    </div>
    """
