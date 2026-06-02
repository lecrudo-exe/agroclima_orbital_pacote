COMO USAR

1. Coloque o arquivo agroclima_orbital.py na mesma pasta do seu notebook:
   SPRTINT1/
   ├── analise_agroclima.ipynb
   ├── agroclima_orbital.py
   └── dados/
       └── dataset_agroclima_orbital.csv

2. No notebook, rode:

from agroclima_orbital import executar_analise_completa

resultados = executar_analise_completa(
    caminho_csv="dados/dataset_agroclima_orbital.csv",
    pasta_saida="resultados"
)

3. O script vai gerar:
   - resumo no output do notebook
   - pasta resultados/graficos com os PNGs
   - pasta resultados/tabelas com tabelas CSV
   - dataset final com indice de risco:
     resultados/dataset_agroclima_orbital_com_risco.csv

4. Para acessar tabelas no notebook:

resultados["medias_por_cidade"]
resultados["outliers"]
resultados["correlacao"]
resultados["tabela_risco"]
resultados["ic_temp_max"]

5. Para acessar o DataFrame final:

df_final = resultados["df"]
df_final.head()
