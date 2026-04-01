import os
import polars as pl
from dotenv import load_dotenv

load_dotenv()

def get_lazy_dataset(folder_name):
    account_name = os.getenv("AZURE_ACCOUNT_NAME")
    account_key = os.getenv("AZURE_ACCOUNT_KEY")
    
    container_name = "govbr-datalake"
    # Agora apontamos para uma pasta específica dentro de BI
    uri_azure = f"az://{container_name}/Sys/BI/{folder_name}/*.parquet"

    storage_options = {
        "account_name": account_name,
        "account_key": account_key,
    }

    try:
        # Usamos collect_schema() para evitar aquele warning de performance
        lf = pl.scan_parquet(uri_azure, storage_options=storage_options)
        return lf
    except Exception as e:
        print(f"❌ Erro ao acessar a pasta {folder_name}: {e}")
        return None

if __name__ == "__main__":
    # Vamos testar especificamente a pasta que deu erro (ela parece ser a mais rica em dados)
    dataset = "agg_viagens_mensal_orgao" 
    
    print(f"🔍 Lendo dataset: {dataset}...")
    df_lazy = get_lazy_dataset(dataset)
    
    if df_lazy is not None:
        print("\n--- Novo Schema Detectado ---")
        print(df_lazy.collect_schema())
        
        print("\n🔢 Contando registros...")
        # Adicionamos streaming=True caso o arquivo seja grande para o seu i5
        # Em vez de collect(streaming=True)
        count = df_lazy.select(pl.len()).collect(engine="streaming")
        print(f"Total de registros em {dataset}: {count.item()}")
        
        print("\n👀 Amostra dos dados:")
        print(df_lazy.head(5).collect())