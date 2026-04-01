# 📊 GovBR Travel Analytics - Azure Data Lake + Polars

Este projeto é um ecossistema de Business Intelligence (BI) de alta performance desenvolvido para analisar dados de viagens do Governo Federal Brasileiro. A solução foca em **eficiência de memória** e **escalabilidade**, processando desde indicadores anuais estratégicos até uma massa de quase **1 milhão de registros de viajantes únicos**.

## 🚀 Stack Tecnológica

* **Linguagem:** Python 3.13
* **Engine de Dados:** [Polars](https://pola.rs/) (Escrita em Rust, foco em performance e Lazy Evaluation)
* **Cloud Storage:** Azure Data Lake Storage (ADLS Gen2)
* **Frontend:** [Streamlit](https://streamlit.io/)
* **Visualização:** Plotly Express & Graph Objects
* **SO de Desenvolvimento:** Ubuntu (Xanmod Kernel)

## 🏗️ Arquitetura e Diferenciais Técnicos

### 1. Camada de Dados (Azure + Polars)
O projeto utiliza o protocolo `az://` para acessar arquivos Parquet diretamente no Azure. O diferencial aqui é o uso de **LazyFrames**, onde as queries são otimizadas antes da execução, reduzindo drasticamente o tráfego de rede e o uso de RAM.

### 2. Data Observability & Compliance
Diferente de dashboards comuns, este projeto inclui uma página de **Auditoria** que monitora:
* **Qualidade Técnica:** Percentual de IDs, órgãos e valores inválidos por ano.
* **Alertas de Compliance:** Identificação de *outliers* de valor e viagens urgentes sem justificativa.

### 3. Big Data no Edge
A página de **Perfil de Viajantes** processa **976.767 registros**. Utilizando a engine de **Streaming do Polars**, conseguimos realizar agregações e buscas textuais em tempo real, mesmo em hardware com limitações de recursos (Intel i5 4th Gen / 16GB RAM).

## 📂 Estrutura do Projeto

```text
.
├── main_app.py                # Dashboard Executivo (Home)
├── pages/
│   ├── 01_auditoria.py        # Qualidade de Dados e Alertas
│   ├── 02_analise_orgaos.py   # Rankings e Concentração (Pareto)
│   └── 03_perfil_viajantes.py # Processamento de Big Data (1M rows)
└── src/
    ├── connector.py           # Abstração da conexão com Azure
    └── discovery.py           # Script de mapeamento automático de metadados