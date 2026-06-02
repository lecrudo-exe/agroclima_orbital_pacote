# usar_no_notebook.py
# Exemplo de uso no notebook ou script.

from agroclima_orbital import executar_analise_completa

resultados = executar_analise_completa(
    caminho_csv="dados/dataset_agroclima_orbital.csv",
    pasta_saida="resultados",
    gerar_graficos=True,
    salvar_csvs=True,
    mostrar_resumo=True,
)

# Exemplos para visualizar no notebook:
df_final = resultados["df"]
medias = resultados["medias_por_cidade"]
outliers = resultados["outliers"]
correlacao = resultados["correlacao"]
risco = resultados["tabela_risco"]

df_final.head()
