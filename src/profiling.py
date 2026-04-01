import polars as pl
from connector import get_lazy_dataset

# Lista de datasets baseada na sua imagem do Azure
datasets = [
    "agg_viagens_mensal_orgao",
    "kpi_anual",
    "alerta_operacional",
    "concentracao_gastos" # Ajuste os nomes conforme aparecem no Azure
]

def levantamento_geral():
    print(f"{'DATASET':<30} | {'LINHAS':<10} | {'COLUNAS'}")
    print("-" * 70)
    
    for ds in datasets:
        lf = get_lazy_dataset(ds)
        if lf is not None:
            try:
                # Pegamos o schema e a contagem de forma eficiente
                schema = list(lf.collect_schema().names())
                count = lf.select(pl.len()).collect(engine="streaming").item()
                
                print(f"{ds:<30} | {count:<10} | {', '.join(schema)}")
            except Exception as e:
                print(f"⚠️ Erro ao ler {ds}: {e}")

if __name__ == "__main__":
    levantamento_geral()