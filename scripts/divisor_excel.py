import pandas as pd

# Caminho do arquivo CSV original
caminho_csv_original = 'A:\Documentos RPA\ARQUIVOS CONSULTA MARGEM\piaui_2.csv'

# Carrega o CSV usando o pandas
df = pd.read_csv(caminho_csv_original)

# Define o número de linhas por arquivo
linhas_por_arquivo = 10000

# Calcula o número de partes necessárias
num_partes = len(df) // linhas_por_arquivo + (1 if len(df) % linhas_por_arquivo != 0 else 0)

# Divide e salva cada parte
for i in range(num_partes):
    inicio = i * linhas_por_arquivo
    fim = inicio + linhas_por_arquivo
    df_parte = df.iloc[inicio:fim]
    caminho_arquivo_parte = f'CONSULTA_MARGEM_PIAUI_PT_{i + 1}.csv'
    df_parte.to_csv(caminho_arquivo_parte, index=False)
    print(f'Arquivo {caminho_arquivo_parte} salvo com sucesso.')