"""
Exemplo de uso do modulo de analise no notebook ou em scripts Python.
"""

from agroclima_orbital import executar_analise_completa


resultados = executar_analise_completa(
    caminho_csv="dados/dataset_agroclima_orbital.csv",
    pasta_saida="resultados",
    gerar_graficos=True,
    salvar_csvs=True,
    mostrar_resumo=True,
)

df_final = resultados["df"]
medias_por_cidade = resultados["medias_por_cidade"]
correlacao = resultados["correlacao"]
outliers = resultados["outliers"]
ic_temp_max = resultados["ic_temp_max"]
tabela_risco = resultados["tabela_risco"]

df_final.head()
