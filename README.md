# AgroClima Orbital

Projeto de Data Science e Statistical Computing para a Global Solution FIAP 2026, com foco em industria espacial aplicada a problemas reais da Terra.

## Tema

**AgroClima Orbital: analise estatistica de risco climatico agricola usando dados espaciais da NASA**

O projeto utiliza dados climaticos e solares da base NASA POWER para comparar duas regioes brasileiras relevantes para agricultura:

- Petrolina/PE
- Ribeirao Preto/SP

A proposta conecta dados espaciais, clima, agricultura e sustentabilidade, criando um indice simples de risco climatico agricola com base em temperatura maxima, precipitacao, umidade e radiacao solar.

## Pergunta principal

As regioes analisadas apresentam diferencas significativas em variaveis climaticas associadas ao risco agricola?

## Fonte dos dados

- Fonte: NASA POWER
- Link: https://power.larc.nasa.gov/
- Periodo analisado: 2015 a 2025
- Granularidade: diaria
- Tipo de dado: meteorologico e solar por coordenada geografica

### Coordenadas e URLs da API

- Petrolina/PE: latitude -9.3986, longitude -40.5008
- Ribeirao Preto/SP: latitude -21.1775, longitude -47.8103
- API Petrolina/PE: https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,RH2M,WS2M,ALLSKY_SFC_SW_DWN&community=AG&longitude=-40.5008&latitude=-9.3986&start=20150101&end=20251231&format=CSV
- API Ribeirao Preto/SP: https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,RH2M,WS2M,ALLSKY_SFC_SW_DWN&community=AG&longitude=-47.8103&latitude=-21.1775&start=20150101&end=20251231&format=CSV

## Variaveis usadas

| Variavel original | Nome usado no projeto | Descricao |
|---|---|---|
| T2M | temp_media | Temperatura media a 2 metros |
| T2M_MAX | temp_max | Temperatura maxima a 2 metros |
| T2M_MIN | temp_min | Temperatura minima a 2 metros |
| PRECTOTCORR | precipitacao | Precipitacao diaria corrigida |
| RH2M | umidade | Umidade relativa a 2 metros |
| WS2M | vento | Velocidade do vento a 2 metros |
| ALLSKY_SFC_SW_DWN | radiacao_solar | Radiacao solar na superficie |

## Analises realizadas

- Descricao do dataset
- Estatistica descritiva
- Histogramas
- Boxplots
- Identificacao de outliers pelo metodo IQR
- Matriz de correlacao
- Criacao de indice de risco climatico
- Intervalo de confianca de 95%
- Teste de Levene para pressuposto de homogeneidade das variancias
- Teste t de Welch para comparacao entre cidades
- Calculo de tamanho de efeito com Cohen's d

## Estrutura recomendada

```text
agroclima_orbital_pacote/
|-- README.md
|-- requirements.txt
|-- baixar_dataset.py
|-- analise_agroclima.ipynb
|-- agroclima_orbital.py
|-- usar_no_notebook.py
|-- dados/
|   `-- dataset_agroclima_orbital.csv
`-- resultados/
    |-- dataset_agroclima_orbital_com_risco.csv
    |-- graficos/
    `-- tabelas/
```

## Como executar

1. Instale as dependencias:

```bash
pip install -r requirements.txt
```

2. Baixe o dataset:

```bash
python baixar_dataset.py
```

3. Rode o notebook `analise_agroclima.ipynb` ou execute no Python:

```python
from agroclima_orbital import executar_analise_completa

resultados = executar_analise_completa(
    caminho_csv="dados/dataset_agroclima_orbital.csv",
    pasta_saida="resultados"
)
```

## Saidas geradas

A analise gera automaticamente:

- `resultados/dataset_agroclima_orbital_com_risco.csv`
- graficos em `resultados/graficos/`
- tabelas em `resultados/tabelas/`

## Hipoteses estatisticas

### Hipotese 1: temperatura maxima

- H0: a temperatura maxima media de Petrolina/PE e Ribeirao Preto/SP e igual.
- H1: a temperatura maxima media das cidades e diferente.

### Hipotese 2: indice de risco climatico

- H0: o indice medio de risco climatico das cidades e igual.
- H1: o indice medio de risco climatico das cidades e diferente.

## Observacao

O codigo gera os resultados estatisticos, mas o relatorio final deve interpretar os resultados obtidos, relacionando-os ao tema da industria espacial, agricultura, clima e sustentabilidade.
