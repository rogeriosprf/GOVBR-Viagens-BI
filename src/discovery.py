import os
import polars as pl
from dotenv import load_dotenv
from azure.storage.blob import ContainerClient

load_dotenv()

def mapear_todos_datasets():
    account_name = os.getenv("AZURE_ACCOUNT_NAME")
    account_key = os.getenv("AZURE_ACCOUNT_KEY")
    container_name = "govbr-datalake"
    base_path = "Sys/BI/"

    # 1. Usamos o SDK da Azure para listar os diretórios reais
    conn_str = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
    container_client = ContainerClient.from_connection_string(conn_str, container_name)
    
    # Lista todos os blobs e extrai o nome da primeira subpasta após BI/
    blobs = container_client.list_blobs(name_starts_with=base_path)
    folders = sorted(list(set([b.name.split('/')[2] for b in blobs if len(b.name.split('/')) > 2])))

    print(f"🔍 Encontrados {len(folders)} possíveis datasets.\n")
    
    mapa_datasets = {}

    storage_options = {"account_name": account_name, "account_key": account_key}

    for folder in folders:
        uri = f"az://{container_name}/{base_path}{folder}/*.parquet"
        try:
            # Tenta ler apenas o esquema (operação levíssima)
            lf = pl.scan_parquet(uri, storage_options=storage_options)
            schema = lf.collect_schema()
            
            # Conta registros (opcional, pode demorar se o volume for bizarro)
            count = lf.select(pl.len()).collect(engine="streaming").item()
            
            mapa_datasets[folder] = {
                "colunas": list(schema.names()),
                "linhas": count,
                "tipos": schema
            }
            print(f"✅ [OK] {folder:<30} | {count:>8} linhas")
        except Exception:
            print(f"❌ [ERRO] {folder:<30} | Pasta vazia ou formato inválido")

    return mapa_datasets

if __name__ == "__main__":
    relatorio = mapear_todos_datasets()
    
    # Exemplo de como usar o relatório para planejar o BI
    print("\n" + "="*50)
    print("RESUMO PARA PLANEJAMENTO DE DASHBOARDS")
    print("="*50)
    for ds, info in relatorio.items():
        print(f"\nDataset: {ds}")
        print(f"Colunas: {', '.join(info['colunas'])}")