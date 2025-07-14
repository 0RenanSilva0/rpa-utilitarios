import pandas as pd
import os

# Caminho do arquivo
caminho_entrada = r"C:\Users\Renan Silva\Documents\Documentos RPA\servidores.xlsx"
caminho_saida = r"C:\Users\Renan Silva\Documents\Documentos RPA\servidores_embaralhado.xlsx"

# Verifica se o arquivo existe
if not os.path.exists(caminho_entrada):
    print("❌ Arquivo não encontrado. Verifique o caminho ou o nome do arquivo.")
    print("Arquivos encontrados na pasta:")
    print(os.listdir(r"C:\Users\Renan Silva\Documents\Documentos RPA"))
else:
    # Lê a planilha original
    df = pd.read_excel(caminho_entrada, sheet_name="Nomes")
    
    print(f"✔ Planilha carregada com {len(df)} registros")
    print("\n📌 Primeiros 5 nomes antes do embaralhamento:")
    print(df.head())

    # Embaralha os dados
    df_shuffled = df.sample(frac=1).reset_index(drop=True)

    # Salva a nova planilha
    df_shuffled.to_excel(caminho_saida, sheet_name="Nomes", index=False)

    print("\n📌 Primeiros 5 nomes após o embaralhamento:")
    print(df_shuffled.head())

    print(f"\n✅ Planilha embaralhada salva com sucesso em:\n{caminho_saida}")
