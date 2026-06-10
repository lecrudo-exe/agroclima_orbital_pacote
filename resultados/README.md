# Resultados

Esta pasta recebe os arquivos gerados pela analise:

- dataset final com indice de risco;
- graficos em PNG;
- tabelas em CSV.

Para gerar os resultados, rode o notebook `analise_agroclima.ipynb` ou execute:

```python
from agroclima_orbital import executar_analise_completa

resultados = executar_analise_completa(
    caminho_csv="dados/dataset_agroclima_orbital.csv",
    pasta_saida="resultados"
)
```
