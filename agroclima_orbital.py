"""
agroclima_orbital.py

Modulo para analise estatistica do projeto AgroClima Orbital.
Use no notebook:

from agroclima_orbital import executar_analise_completa

resultados = executar_analise_completa(
    caminho_csv="dados/dataset_agroclima_orbital.csv",
    pasta_saida="resultados"
)

Depois acesse:
resultados["df"]
resultados["medias_por_cidade"]
resultados["outliers"]
resultados["correlacao"]
resultados["ic_temp_max"]
resultados["teste_t"]
resultados["cohens_d"]
resultados["tabela_risco"]
"""

from pathlib import Path
import math

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats


MAPA_COLUNAS = {
    "T2M": "temp_media",
    "T2M_MAX": "temp_max",
    "T2M_MIN": "temp_min",
    "PRECTOTCORR": "precipitacao",
    "RH2M": "umidade",
    "WS2M": "vento",
    "ALLSKY_SFC_SW_DWN": "radiacao_solar",
}

VARIAVEIS = [
    "temp_media",
    "temp_max",
    "temp_min",
    "precipitacao",
    "umidade",
    "vento",
    "radiacao_solar",
]


def carregar_e_preparar(caminho_csv: str) -> pd.DataFrame:
    """Carrega o CSV da NASA POWER e prepara as colunas para analise."""
    df = pd.read_csv(caminho_csv)

    if "data" not in df.columns:
        raise ValueError("A coluna 'data' nao foi encontrada no CSV.")

    if "cidade" not in df.columns:
        raise ValueError("A coluna 'cidade' nao foi encontrada no CSV.")

    df["data"] = pd.to_datetime(df["data"])
    df["ano"] = df["data"].dt.year
    df["mes"] = df["data"].dt.month

    df = df.rename(columns=MAPA_COLUNAS)

    colunas_faltando = [col for col in VARIAVEIS if col not in df.columns]
    if colunas_faltando:
        raise ValueError(f"Colunas faltando no dataset: {colunas_faltando}")

    return df


def estatistica_descritiva(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Retorna estatistica descritiva geral e por cidade."""
    descritiva_geral = df[VARIAVEIS].describe().round(3)
    descritiva_por_cidade = df.groupby("cidade")[VARIAVEIS].describe().round(3)
    return descritiva_geral, descritiva_por_cidade


def medias_por_cidade(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula as medias das variaveis por cidade."""
    return df.groupby("cidade")[VARIAVEIS].mean().round(2)


def gerar_histogramas(df: pd.DataFrame, pasta_saida: str = "resultados/graficos") -> None:
    """Gera histogramas para todas as variaveis principais."""
    pasta = Path(pasta_saida)
    pasta.mkdir(parents=True, exist_ok=True)

    for var in VARIAVEIS:
        plt.figure(figsize=(9, 5))

        for cidade in df["cidade"].unique():
            dados = df.loc[df["cidade"] == cidade, var]
            plt.hist(dados, bins=30, alpha=0.5, label=cidade)

        plt.title(f"Histograma de {var}")
        plt.xlabel(var)
        plt.ylabel("Frequencia")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(pasta / f"histograma_{var}.png", dpi=150)
        plt.close()


def gerar_boxplots(df: pd.DataFrame, pasta_saida: str = "resultados/graficos") -> None:
    """Gera boxplots por cidade para identificar outliers visualmente."""
    pasta = Path(pasta_saida)
    pasta.mkdir(parents=True, exist_ok=True)

    for var in VARIAVEIS:
        plt.figure(figsize=(8, 5))
        df.boxplot(column=var, by="cidade")
        plt.title(f"Boxplot de {var} por cidade")
        plt.suptitle("")
        plt.xlabel("Cidade")
        plt.ylabel(var)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(pasta / f"boxplot_{var}.png", dpi=150)
        plt.close()


def contar_outliers_iqr(dados: pd.DataFrame, coluna: str) -> tuple[int, float, float]:
    """Conta outliers usando o metodo IQR."""
    q1 = dados[coluna].quantile(0.25)
    q3 = dados[coluna].quantile(0.75)
    iqr = q3 - q1

    limite_inferior = q1 - 1.5 * iqr
    limite_superior = q3 + 1.5 * iqr

    outliers = dados[
        (dados[coluna] < limite_inferior)
        | (dados[coluna] > limite_superior)
    ]

    return len(outliers), float(limite_inferior), float(limite_superior)


def tabela_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """Cria tabela com quantidade de outliers por cidade e variavel."""
    resultados = []

    for cidade in df["cidade"].unique():
        dados_cidade = df[df["cidade"] == cidade]

        for var in VARIAVEIS:
            qtd, li, ls = contar_outliers_iqr(dados_cidade, var)
            resultados.append({
                "cidade": cidade,
                "variavel": var,
                "quantidade_outliers": qtd,
                "limite_inferior": round(li, 3),
                "limite_superior": round(ls, 3),
            })

    return pd.DataFrame(resultados)


def matriz_correlacao(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula matriz de correlacao de Pearson."""
    return df[VARIAVEIS].corr().round(3)


def gerar_grafico_correlacao(
    correlacao: pd.DataFrame,
    pasta_saida: str = "resultados/graficos",
) -> None:
    """Gera grafico da matriz de correlacao."""
    pasta = Path(pasta_saida)
    pasta.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(10, 8))
    plt.imshow(correlacao, aspect="auto")
    plt.colorbar(label="Correlacao")

    nomes = list(correlacao.columns)
    plt.xticks(range(len(nomes)), nomes, rotation=45, ha="right")
    plt.yticks(range(len(nomes)), nomes)
    plt.title("Matriz de correlacao entre variaveis climaticas")

    for i in range(len(nomes)):
        for j in range(len(nomes)):
            valor = correlacao.iloc[i, j]
            plt.text(j, i, f"{valor:.2f}", ha="center", va="center")

    plt.tight_layout()
    plt.savefig(pasta / "matriz_correlacao.png", dpi=150)
    plt.close()


def criar_indice_risco(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria indice de risco climatico agricola.

    Regras:
    - risco_calor: temperatura maxima acima do percentil 75
    - risco_seca: precipitacao abaixo ou igual ao percentil 25
    - risco_radiacao: radiacao solar acima do percentil 75
    - risco_umidade: umidade abaixo do percentil 25
    """
    df = df.copy()

    limite_calor = df["temp_max"].quantile(0.75)
    limite_baixa_chuva = df["precipitacao"].quantile(0.25)
    limite_radiacao = df["radiacao_solar"].quantile(0.75)
    limite_baixa_umidade = df["umidade"].quantile(0.25)

    df["risco_calor"] = df["temp_max"] > limite_calor
    df["risco_seca"] = df["precipitacao"] <= limite_baixa_chuva
    df["risco_radiacao"] = df["radiacao_solar"] > limite_radiacao
    df["risco_umidade"] = df["umidade"] < limite_baixa_umidade

    df["indice_risco_climatico"] = (
        df["risco_calor"].astype(int)
        + df["risco_seca"].astype(int)
        + df["risco_radiacao"].astype(int)
        + df["risco_umidade"].astype(int)
    )

    df["classificacao_risco"] = pd.cut(
        df["indice_risco_climatico"],
        bins=[-1, 1, 2, 4],
        labels=["Baixo", "Medio", "Alto"],
    )

    return df


def tabela_risco_percentual(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula percentual de dias em cada classificacao de risco por cidade."""
    tabela = pd.crosstab(
        df["cidade"],
        df["classificacao_risco"],
        normalize="index",
    ) * 100

    return tabela.round(2)


def gerar_grafico_risco(
    tabela_risco: pd.DataFrame,
    pasta_saida: str = "resultados/graficos",
) -> None:
    """Gera grafico de barras com percentual de risco por cidade."""
    pasta = Path(pasta_saida)
    pasta.mkdir(parents=True, exist_ok=True)

    tabela_risco.plot(kind="bar", figsize=(9, 5))
    plt.title("Percentual de dias por classificacao de risco climatico")
    plt.xlabel("Cidade")
    plt.ylabel("Percentual de dias (%)")
    plt.xticks(rotation=0)
    plt.legend(title="Classificacao")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(pasta / "risco_climatico_por_cidade.png", dpi=150)
    plt.close()


def intervalo_confianca_media(dados: pd.Series, confianca: float = 0.95) -> tuple[float, float, float]:
    """Calcula intervalo de confianca para a media usando distribuicao t."""
    dados = dados.dropna()
    n = len(dados)
    media = float(np.mean(dados))
    erro_padrao = stats.sem(dados)

    intervalo = stats.t.interval(
        confidence=confianca,
        df=n - 1,
        loc=media,
        scale=erro_padrao,
    )

    return media, float(intervalo[0]), float(intervalo[1])


def tabela_ic_temp_max(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula IC 95% da temperatura maxima media por cidade."""
    resultados = []

    for cidade in df["cidade"].unique():
        dados = df.loc[df["cidade"] == cidade, "temp_max"]
        media, limite_inf, limite_sup = intervalo_confianca_media(dados)

        resultados.append({
            "cidade": cidade,
            "variavel": "temp_max",
            "media": round(media, 3),
            "ic_95_inferior": round(limite_inf, 3),
            "ic_95_superior": round(limite_sup, 3),
        })

    return pd.DataFrame(resultados)


def teste_levene_temp_max(df: pd.DataFrame):
    """Teste de Levene para homogeneidade das variancias da temp_max."""
    cidades = list(df["cidade"].unique())
    if len(cidades) != 2:
        raise ValueError("Este teste foi configurado para exatamente duas cidades.")

    x = df.loc[df["cidade"] == cidades[0], "temp_max"]
    y = df.loc[df["cidade"] == cidades[1], "temp_max"]

    return stats.levene(x, y)


def teste_t_welch_temp_max(df: pd.DataFrame):
    """Teste t de Welch para comparar temperatura maxima media entre duas cidades."""
    cidades = list(df["cidade"].unique())
    if len(cidades) != 2:
        raise ValueError("Este teste foi configurado para exatamente duas cidades.")

    x = df.loc[df["cidade"] == cidades[0], "temp_max"]
    y = df.loc[df["cidade"] == cidades[1], "temp_max"]

    return stats.ttest_ind(x, y, equal_var=False)


def teste_t_welch_risco(df: pd.DataFrame):
    """Teste t de Welch para comparar indice medio de risco climatico."""
    cidades = list(df["cidade"].unique())
    if len(cidades) != 2:
        raise ValueError("Este teste foi configurado para exatamente duas cidades.")

    x = df.loc[df["cidade"] == cidades[0], "indice_risco_climatico"]
    y = df.loc[df["cidade"] == cidades[1], "indice_risco_climatico"]

    return stats.ttest_ind(x, y, equal_var=False)


def cohens_d(x: pd.Series, y: pd.Series) -> float:
    """Calcula Cohen's d para duas amostras independentes."""
    x = x.dropna()
    y = y.dropna()

    nx = len(x)
    ny = len(y)

    var_x = x.var(ddof=1)
    var_y = y.var(ddof=1)

    pooled_std = np.sqrt(
        ((nx - 1) * var_x + (ny - 1) * var_y) / (nx + ny - 2)
    )

    return float((x.mean() - y.mean()) / pooled_std)


def cohens_d_temp_max(df: pd.DataFrame) -> float:
    """Calcula Cohen's d da temperatura maxima entre duas cidades."""
    cidades = list(df["cidade"].unique())
    if len(cidades) != 2:
        raise ValueError("Este calculo foi configurado para exatamente duas cidades.")

    x = df.loc[df["cidade"] == cidades[0], "temp_max"]
    y = df.loc[df["cidade"] == cidades[1], "temp_max"]

    return cohens_d(x, y)


def interpretar_pvalor(pvalor: float, alpha: float = 0.05) -> str:
    """Interpreta um p-valor com base em alpha."""
    if pvalor < alpha:
        return "Rejeitamos H0: existe diferenca estatisticamente significativa."
    return "Nao rejeitamos H0: nao ha evidencia suficiente de diferenca significativa."


def interpretar_cohens_d(d: float) -> str:
    """Interpreta Cohen's d por regra pratica."""
    ad = abs(d)

    if ad < 0.2:
        return "efeito muito pequeno"
    if ad < 0.5:
        return "efeito pequeno"
    if ad < 0.8:
        return "efeito medio"
    return "efeito grande"


def salvar_tabelas_csv(resultados: dict, pasta_saida: str = "resultados/tabelas") -> None:
    """Salva as principais tabelas em CSV."""
    pasta = Path(pasta_saida)
    pasta.mkdir(parents=True, exist_ok=True)

    tabelas = {
        "descritiva_geral": resultados["descritiva_geral"],
        "medias_por_cidade": resultados["medias_por_cidade"],
        "outliers": resultados["outliers"],
        "correlacao": resultados["correlacao"],
        "tabela_risco": resultados["tabela_risco"],
        "ic_temp_max": resultados["ic_temp_max"],
    }

    for nome, tabela in tabelas.items():
        tabela.to_csv(pasta / f"{nome}.csv", encoding="utf-8-sig")


def imprimir_resumo(resultados: dict) -> None:
    """Imprime resumo final da analise."""
    df = resultados["df"]
    teste_t = resultados["teste_t"]
    teste_risco = resultados["teste_risco"]
    d = resultados["cohens_d"]

    print("RESUMO DO DATASET")
    print("-" * 60)
    print(f"Quantidade de registros: {df.shape[0]}")
    print(f"Quantidade de colunas: {df.shape[1]}")
    print(f"Periodo: {df['data'].min().date()} ate {df['data'].max().date()}")
    print(f"Cidades analisadas: {', '.join(df['cidade'].unique())}")

    print("\nMEDIA DAS VARIAVEIS POR CIDADE")
    print("-" * 60)
    print(resultados["medias_por_cidade"])

    print("\nCLASSIFICACAO DE RISCO POR CIDADE (%)")
    print("-" * 60)
    print(resultados["tabela_risco"])

    print("\nINTERVALO DE CONFIANCA 95% - TEMPERATURA MAXIMA")
    print("-" * 60)
    print(resultados["ic_temp_max"])

    print("\nTESTE DE LEVENE - HOMOGENEIDADE DAS VARIANCIAS")
    print("-" * 60)
    print(f"Estatistica: {resultados['teste_levene'].statistic:.4f}")
    print(f"P-valor: {resultados['teste_levene'].pvalue:.10f}")
    print(interpretar_pvalor(resultados["teste_levene"].pvalue))

    print("\nTESTE T DE WELCH - TEMPERATURA MAXIMA")
    print("-" * 60)
    print("H0: a temperatura maxima media das cidades e igual.")
    print("H1: a temperatura maxima media das cidades e diferente.")
    print(f"Estatistica t: {teste_t.statistic:.4f}")
    print(f"P-valor: {teste_t.pvalue:.10f}")
    print(interpretar_pvalor(teste_t.pvalue))

    print("\nTAMANHO DE EFEITO - COHEN'S D")
    print("-" * 60)
    print(f"Cohen's d: {d:.4f}")
    print(f"Interpretacao: {interpretar_cohens_d(d)}")

    print("\nTESTE T DE WELCH - INDICE DE RISCO CLIMATICO")
    print("-" * 60)
    print("H0: o indice medio de risco climatico das cidades e igual.")
    print("H1: o indice medio de risco climatico das cidades e diferente.")
    print(f"Estatistica t: {teste_risco.statistic:.4f}")
    print(f"P-valor: {teste_risco.pvalue:.10f}")
    print(interpretar_pvalor(teste_risco.pvalue))


def executar_analise_completa(
    caminho_csv: str = "dados/dataset_agroclima_orbital.csv",
    pasta_saida: str = "resultados",
    gerar_graficos: bool = True,
    salvar_csvs: bool = True,
    mostrar_resumo: bool = True,
) -> dict:
    """
    Executa a analise completa:
    - leitura e preparacao
    - estatistica descritiva
    - outliers
    - correlacao
    - indice de risco
    - intervalo de confianca
    - testes de hipotese
    - tamanho de efeito
    - graficos e tabelas
    """
    pasta_saida = Path(pasta_saida)
    pasta_saida.mkdir(parents=True, exist_ok=True)

    df = carregar_e_preparar(caminho_csv)
    df = criar_indice_risco(df)

    descritiva_geral, descritiva_por_cidade = estatistica_descritiva(df)
    medias = medias_por_cidade(df)
    outliers = tabela_outliers(df)
    correlacao = matriz_correlacao(df)
    risco = tabela_risco_percentual(df)
    ic = tabela_ic_temp_max(df)

    teste_levene = teste_levene_temp_max(df)
    teste_t = teste_t_welch_temp_max(df)
    teste_risco = teste_t_welch_risco(df)
    d = cohens_d_temp_max(df)

    resultados = {
        "df": df,
        "variaveis": VARIAVEIS,
        "descritiva_geral": descritiva_geral,
        "descritiva_por_cidade": descritiva_por_cidade,
        "medias_por_cidade": medias,
        "outliers": outliers,
        "correlacao": correlacao,
        "tabela_risco": risco,
        "ic_temp_max": ic,
        "teste_levene": teste_levene,
        "teste_t": teste_t,
        "teste_risco": teste_risco,
        "cohens_d": d,
    }

    if gerar_graficos:
        pasta_graficos = pasta_saida / "graficos"
        gerar_histogramas(df, pasta_graficos)
        gerar_boxplots(df, pasta_graficos)
        gerar_grafico_correlacao(correlacao, pasta_graficos)
        gerar_grafico_risco(risco, pasta_graficos)

    if salvar_csvs:
        salvar_tabelas_csv(resultados, pasta_saida / "tabelas")
        df.to_csv(
            pasta_saida / "dataset_agroclima_orbital_com_risco.csv",
            index=False,
            encoding="utf-8-sig",
        )

    if mostrar_resumo:
        imprimir_resumo(resultados)

    return resultados
