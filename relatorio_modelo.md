# Relatorio - AgroClima Orbital

## Integrantes

- Nome:
- RM:
- Nome:
- RM:

## 1. Introducao

A industria espacial tem papel cada vez mais importante na solucao de problemas terrestres. Dados obtidos por satelites e modelos associados permitem monitorar clima, agricultura, desastres naturais e mudancas ambientais.

Este projeto utiliza dados da NASA POWER para analisar variaveis climaticas e solares em duas regioes brasileiras: Petrolina/PE e Ribeirao Preto/SP. A proposta e avaliar diferencas climaticas entre as regioes e criar um indice de risco climatico agricola.

### Objetivo

Analisar estatisticamente dados climaticos derivados de infraestrutura espacial para comparar o risco climatico agricola entre Petrolina/PE e Ribeirao Preto/SP.

### Pergunta principal

As regioes analisadas apresentam diferencas significativas em variaveis climaticas associadas ao risco agricola?

## 2. Descricao do dataset

O dataset foi construido a partir da API NASA POWER, utilizando dados diarios de 2015 a 2025.

### Fonte

NASA POWER: https://power.larc.nasa.gov/

### Registros

O dataset possui aproximadamente 8.036 registros, considerando dados diarios para duas cidades entre 2015 e 2025.

### Variaveis principais

- `temp_media`: temperatura media diaria.
- `temp_max`: temperatura maxima diaria.
- `temp_min`: temperatura minima diaria.
- `precipitacao`: precipitacao diaria.
- `umidade`: umidade relativa.
- `vento`: velocidade do vento.
- `radiacao_solar`: radiacao solar na superficie.

## 3. Estatistica descritiva

Nesta secao, inserir a tabela de medias por cidade e comentar as diferencas observadas.

Exemplo de interpretacao:

> A estatistica descritiva mostra diferencas entre as cidades em variaveis como temperatura maxima, precipitacao, umidade e radiacao solar. Essas diferencas indicam padroes climaticos distintos, relevantes para avaliacao de risco agricola.

## 4. Analise exploratoria

Foram gerados histogramas, boxplots e matriz de correlacao para compreender a distribuicao das variaveis, identificar possiveis outliers e observar relacoes entre variaveis climaticas.

### Histogramas

Os histogramas permitem observar a distribuicao das variaveis climaticas em cada cidade.

### Boxplots

Os boxplots permitem comparar a dispersao das variaveis por cidade e apoiar a identificacao visual de valores extremos.

## 5. Correlacao

A matriz de correlacao foi usada para avaliar relacoes lineares entre variaveis, como temperatura, umidade, precipitacao e radiacao solar.

Inserir aqui a tabela `correlacao.csv` e comentar os pares de variaveis com correlacoes mais fortes.

## 6. Outliers

Os boxplots foram usados para analise visual de outliers. O metodo IQR foi usado para contabilizar valores extremos.

Inserir aqui a tabela `outliers.csv` e comentar quais variaveis apresentaram maior quantidade de outliers.

## 7. Amostra e populacao

A populacao pode ser entendida como todos os dias possiveis de observacao climatica nas regioes analisadas.

A amostra corresponde aos dados diarios coletados entre 2015 e 2025 para Petrolina/PE e Ribeirao Preto/SP.

## 8. Indice de risco climatico

Foi criado um indice de risco climatico agricola com quatro criterios:

- temperatura maxima acima do percentil 75;
- precipitacao abaixo ou igual ao percentil 25;
- radiacao solar acima do percentil 75;
- umidade abaixo do percentil 25.

Cada criterio soma 1 ponto ao indice. A classificacao final foi:

- 0 a 1: baixo risco;
- 2: medio risco;
- 3 a 4: alto risco.

## 9. Intervalo de confianca

Foi calculado o intervalo de confianca de 95% para a temperatura maxima media de cada cidade.

Inserir aqui a tabela `ic_temp_max.csv` e interpretar se os intervalos sugerem diferenca entre as cidades.

## 10. Teste de hipotese

### Hipotese para temperatura maxima

- H0: a temperatura maxima media de Petrolina/PE e Ribeirao Preto/SP e igual.
- H1: a temperatura maxima media das cidades e diferente.

Foi aplicado o teste t de Welch, adequado quando as variancias podem ser diferentes entre os grupos.

## 11. Pressupostos

Foi aplicado o teste de Levene para verificar homogeneidade das variancias.

Se o p-valor do teste de Levene for menor que 0,05, ha evidencia de variancias diferentes. Por isso, o teste t de Welch e uma escolha adequada.

## 12. Tamanho de efeito

Foi calculado o tamanho de efeito usando Cohen's d.

Interpretacao pratica:

- 0,2: efeito pequeno;
- 0,5: efeito medio;
- 0,8 ou mais: efeito grande.

## 13. Conclusao

Preencher apos rodar o notebook.

Exemplo de conclusao:

> Os resultados indicam que as cidades analisadas apresentam diferencas climaticas relevantes, especialmente em variaveis ligadas a temperatura, umidade, precipitacao e radiacao solar. O indice de risco climatico permitiu transformar dados espaciais da NASA em uma medida aplicada ao contexto agricola brasileiro. Dessa forma, o projeto demonstra como dados da industria espacial podem apoiar decisoes relacionadas a agricultura, sustentabilidade e adaptacao climatica.

## 14. Limitacoes e melhorias futuras

- O estudo analisou apenas duas cidades.
- O indice criado e simplificado e poderia ser ajustado com apoio de especialistas em agronomia.
- Futuras versoes poderiam incluir produtividade agricola real, tipos de cultura e dados de solo.
- Tambem seria possivel expandir a analise para mais cidades e diferentes biomas brasileiros.
