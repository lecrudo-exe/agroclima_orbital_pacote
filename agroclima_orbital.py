"""
Modulo principal do projeto AgroClima Orbital.

Executa a analise estatistica de risco climatico agricola com dados diarios da
NASA POWER para Petrolina/PE e Ribeirao Preto/SP.
"""

from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from scipy import stats


matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

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


def carregar_e_preparar(caminho_csv: str | Path) -> pd.DataFrame:
    """Carrega o CSV da NASA POWER e prepara as colunas da analise."""
    df = pd.read_csv(caminho_csv, encoding="utf-8-sig")

    colunas_obrigatorias = {"data", "cidade", "latitude", "longitude"}
    faltantes = colunas_obrigatorias.difference(df.columns)
    if faltantes:
        raise ValueError(f"Colunas obrigatorias ausentes: {sorted(faltantes)}")

    df["data"] = pd.to_datetime(df["data"])
    df = df.rename(columns=MAPA_COLUNAS)

    colunas_faltando = [coluna for coluna in VARIAVEIS if coluna not in df.columns]
    if colunas_faltando:
        raise ValueError(f"Colunas climaticas ausentes: {colunas_faltando}")

    df[VARIAVEIS] = df[VARIAVEIS].apply(pd.to_numeric, errors="coerce")
    df[VARIAVEIS] = df[VARIAVEIS].replace(-999, np.nan)
    df["ano"] = df["data"].dt.year
    df["mes"] = df["data"].dt.month

    return df.sort_values(["cidade", "data"]).reset_index(drop=True)


def estatistica_descritiva(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Calcula estatistica descritiva geral e por cidade."""
    descritiva_geral = df[VARIAVEIS].describe().round(3)
    descritiva_por_cidade = (
        df.groupby("cidade")[VARIAVEIS]
        .describe()
        .round(3)
    )
    return descritiva_geral, descritiva_por_cidade


def calcular_medias_por_cidade(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula medias das variaveis climaticas por cidade."""
    return df.groupby("cidade")[VARIAVEIS].mean().round(3)


def gerar_histogramas(df: pd.DataFrame, pasta_saida: str | Path) -> None:
    """Gera histogramas das variaveis climaticas por cidade."""
    pasta = Path(pasta_saida)
    pasta.mkdir(parents=True, exist_ok=True)

    for variavel in VARIAVEIS:
        plt.figure(figsize=(9, 5))
        sns.histplot(
            data=df,
            x=variavel,
            hue="cidade",
            bins=30,
            kde=True,
            alpha=0.45,
        )
        plt.title(f"Histograma de {variavel}")
        plt.xlabel(variavel)
        plt.ylabel("Frequencia")
        plt.grid(True, alpha=0.25)
        plt.tight_layout()
        plt.savefig(pasta / f"histograma_{variavel}.png", dpi=150)
        plt.close()


def gerar_boxplots(df: pd.DataFrame, pasta_saida: str | Path) -> None:
    """Gera boxplots das variaveis climaticas por cidade."""
    pasta = Path(pasta_saida)
    pasta.mkdir(parents=True, exist_ok=True)

    for variavel in VARIAVEIS:
        plt.figure(figsize=(8, 5))
        sns.boxplot(data=df, x="cidade", y=variavel)
        plt.title(f"Boxplot de {variavel} por cidade")
        plt.xlabel("Cidade")
        plt.ylabel(variavel)
        plt.grid(True, axis="y", alpha=0.25)
        plt.tight_layout()
        plt.savefig(pasta / f"boxplot_{variavel}.png", dpi=150)
        plt.close()


def identificar_outliers_iqr(df: pd.DataFrame) -> pd.DataFrame:
    """Identifica outliers pelo metodo IQR para cada cidade e variavel."""
    linhas = []

    for cidade, grupo in df.groupby("cidade"):
        for variavel in VARIAVEIS:
            serie = grupo[variavel].dropna()
            q1 = serie.quantile(0.25)
            q3 = serie.quantile(0.75)
            iqr = q3 - q1
            limite_inferior = q1 - 1.5 * iqr
            limite_superior = q3 + 1.5 * iqr
            mascara = (serie < limite_inferior) | (serie > limite_superior)

            linhas.append(
                {
                    "cidade": cidade,
                    "variavel": variavel,
                    "q1": round(q1, 3),
                    "q3": round(q3, 3),
                    "iqr": round(iqr, 3),
                    "limite_inferior": round(limite_inferior, 3),
                    "limite_superior": round(limite_superior, 3),
                    "quantidade_outliers": int(mascara.sum()),
                    "percentual_outliers": round(mascara.mean() * 100, 3),
                }
            )

    return pd.DataFrame(linhas)


def calcular_correlacao(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula matriz de correlacao de Pearson."""
    return df[VARIAVEIS].corr().round(3)


def gerar_grafico_correlacao(correlacao: pd.DataFrame, pasta_saida: str | Path) -> None:
    """Gera heatmap da matriz de correlacao."""
    pasta = Path(pasta_saida)
    pasta.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(10, 8))
    sns.heatmap(
        correlacao,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        linewidths=0.5,
    )
    plt.title("Matriz de correlacao entre variaveis climaticas")
    plt.tight_layout()
    plt.savefig(pasta / "matriz_correlacao.png", dpi=150)
    plt.close()


def criar_indice_risco_climatico(df: pd.DataFrame) -> pd.DataFrame:
    """Cria indice e classificacao de risco climatico agricola."""
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
        df[["risco_calor", "risco_seca", "risco_radiacao", "risco_umidade"]]
        .astype(int)
        .sum(axis=1)
    )
    df["classificacao_risco"] = pd.cut(
        df["indice_risco_climatico"],
        bins=[-1, 1, 2, 4],
        labels=["Baixo", "Médio", "Alto"],
    )

    return df


def calcular_tabela_risco(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula percentual de dias por classificacao de risco e cidade."""
    tabela = pd.crosstab(
        df["cidade"],
        df["classificacao_risco"],
        normalize="index",
    )
    return (tabela * 100).round(3)


def gerar_grafico_risco(tabela_risco: pd.DataFrame, pasta_saida: str | Path) -> None:
    """Gera grafico de barras com distribuicao do risco por cidade."""
    pasta = Path(pasta_saida)
    pasta.mkdir(parents=True, exist_ok=True)

    ax = tabela_risco.plot(kind="bar", figsize=(9, 5))
    ax.set_title("Percentual de dias por classificacao de risco climatico")
    ax.set_xlabel("Cidade")
    ax.set_ylabel("Percentual de dias (%)")
    ax.tick_params(axis="x", rotation=0)
    ax.grid(True, axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(pasta / "risco_climatico_por_cidade.png", dpi=150)
    plt.close()


def intervalo_confianca_media(
    serie: pd.Series,
    confianca: float = 0.95,
) -> tuple[float, float, float, int]:
    """Calcula intervalo de confianca da media usando distribuicao t."""
    serie = serie.dropna()
    n = len(serie)
    media = float(serie.mean())
    erro_padrao = stats.sem(serie)
    intervalo = stats.t.interval(
        confidence=confianca,
        df=n - 1,
        loc=media,
        scale=erro_padrao,
    )
    return media, float(intervalo[0]), float(intervalo[1]), n


def calcular_ic_temp_max(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula IC 95% da temperatura maxima por cidade."""
    linhas = []

    for cidade, grupo in df.groupby("cidade"):
        media, inferior, superior, n = intervalo_confianca_media(grupo["temp_max"])
        linhas.append(
            {
                "cidade": cidade,
                "variavel": "temp_max",
                "n": n,
                "media": round(media, 3),
                "ic_95_inferior": round(inferior, 3),
                "ic_95_superior": round(superior, 3),
            }
        )

    return pd.DataFrame(linhas)


def _obter_duas_amostras(df: pd.DataFrame, coluna: str) -> tuple[str, str, pd.Series, pd.Series]:
    cidades = sorted(df["cidade"].dropna().unique())
    if len(cidades) != 2:
        raise ValueError("A comparacao estatistica exige exatamente duas cidades.")

    cidade_a, cidade_b = cidades
    amostra_a = df.loc[df["cidade"] == cidade_a, coluna].dropna()
    amostra_b = df.loc[df["cidade"] == cidade_b, coluna].dropna()
    return cidade_a, cidade_b, amostra_a, amostra_b


def executar_teste_levene(df: pd.DataFrame) -> pd.DataFrame:
    """Executa teste de Levene para temp_max entre as duas cidades."""
    cidade_a, cidade_b, amostra_a, amostra_b = _obter_duas_amostras(df, "temp_max")
    resultado = stats.levene(amostra_a, amostra_b)
    return pd.DataFrame(
        [
            {
                "variavel": "temp_max",
                "grupo_1": cidade_a,
                "grupo_2": cidade_b,
                "estatistica": float(resultado.statistic),
                "p_valor": float(resultado.pvalue),
                "alpha": 0.05,
                "homogeneidade_variancias": "Nao" if resultado.pvalue < 0.05 else "Sim",
            }
        ]
    )


def executar_teste_t_welch(df: pd.DataFrame, coluna: str = "temp_max") -> pd.DataFrame:
    """Executa teste t de Welch entre as duas cidades."""
    cidade_a, cidade_b, amostra_a, amostra_b = _obter_duas_amostras(df, coluna)
    resultado = stats.ttest_ind(amostra_a, amostra_b, equal_var=False)
    return pd.DataFrame(
        [
            {
                "variavel": coluna,
                "grupo_1": cidade_a,
                "grupo_2": cidade_b,
                "media_grupo_1": round(float(amostra_a.mean()), 3),
                "media_grupo_2": round(float(amostra_b.mean()), 3),
                "estatistica_t": float(resultado.statistic),
                "p_valor": float(resultado.pvalue),
                "alpha": 0.05,
                "rejeita_h0": "Sim" if resultado.pvalue < 0.05 else "Nao",
            }
        ]
    )


def calcular_cohens_d(df: pd.DataFrame, coluna: str = "temp_max") -> pd.DataFrame:
    """Calcula Cohen's d entre as duas cidades."""
    cidade_a, cidade_b, amostra_a, amostra_b = _obter_duas_amostras(df, coluna)
    n_a = len(amostra_a)
    n_b = len(amostra_b)
    variancia_a = amostra_a.var(ddof=1)
    variancia_b = amostra_b.var(ddof=1)
    desvio_agrupado = np.sqrt(
        ((n_a - 1) * variancia_a + (n_b - 1) * variancia_b) / (n_a + n_b - 2)
    )
    valor = float((amostra_a.mean() - amostra_b.mean()) / desvio_agrupado)

    if abs(valor) < 0.2:
        interpretacao = "muito pequeno"
    elif abs(valor) < 0.5:
        interpretacao = "pequeno"
    elif abs(valor) < 0.8:
        interpretacao = "medio"
    else:
        interpretacao = "grande"

    return pd.DataFrame(
        [
            {
                "variavel": coluna,
                "grupo_1": cidade_a,
                "grupo_2": cidade_b,
                "cohens_d": round(valor, 6),
                "interpretacao": interpretacao,
            }
        ]
    )


def salvar_tabelas(resultados: dict, pasta_saida: str | Path) -> None:
    """Salva as principais tabelas da analise em CSV."""
    pasta = Path(pasta_saida)
    pasta.mkdir(parents=True, exist_ok=True)

    nomes_tabelas = [
        "descritiva_geral",
        "descritiva_por_cidade",
        "medias_por_cidade",
        "outliers",
        "correlacao",
        "ic_temp_max",
        "tabela_risco",
        "teste_levene",
        "teste_t_welch_temp_max",
        "teste_t_welch_risco",
        "cohens_d",
    ]

    for nome in nomes_tabelas:
        resultados[nome].to_csv(pasta / f"{nome}.csv", encoding="utf-8-sig")


def imprimir_resumo(resultados: dict) -> None:
    """Imprime um resumo curto da analise completa."""
    df = resultados["df"]

    print("RESUMO DO DATASET")
    print("-" * 60)
    print(f"Shape: {df.shape}")
    print(f"Periodo: {df['data'].min().date()} a {df['data'].max().date()}")
    print(f"Cidades: {', '.join(sorted(df['cidade'].unique()))}")

    print("\nMEDIAS POR CIDADE")
    print("-" * 60)
    print(resultados["medias_por_cidade"])

    print("\nINTERVALO DE CONFIANCA 95% - TEMP_MAX")
    print("-" * 60)
    print(resultados["ic_temp_max"])

    print("\nTESTE T DE WELCH - TEMP_MAX")
    print("-" * 60)
    print(resultados["teste_t_welch_temp_max"])

    print("\nCOHEN'S D - TEMP_MAX")
    print("-" * 60)
    print(resultados["cohens_d"])


def executar_analise_completa(
    caminho_csv: str | Path = "dados/dataset_agroclima_orbital.csv",
    pasta_saida: str | Path = "resultados",
    gerar_graficos: bool = True,
    salvar_csvs: bool = True,
    mostrar_resumo: bool = True,
) -> dict:
    """Executa a analise completa e retorna tabelas, testes e dataset final."""
    pasta_saida = Path(pasta_saida)
    pasta_graficos = pasta_saida / "graficos"
    pasta_tabelas = pasta_saida / "tabelas"
    pasta_saida.mkdir(parents=True, exist_ok=True)

    df = carregar_e_preparar(caminho_csv)
    df = criar_indice_risco_climatico(df)

    descritiva_geral, descritiva_por_cidade = estatistica_descritiva(df)
    resultados = {
        "df": df,
        "descritiva_geral": descritiva_geral,
        "descritiva_por_cidade": descritiva_por_cidade,
        "medias_por_cidade": calcular_medias_por_cidade(df),
        "outliers": identificar_outliers_iqr(df),
        "correlacao": calcular_correlacao(df),
        "ic_temp_max": calcular_ic_temp_max(df),
        "tabela_risco": calcular_tabela_risco(df),
        "teste_levene": executar_teste_levene(df),
        "teste_t_welch_temp_max": executar_teste_t_welch(df, "temp_max"),
        "teste_t_welch_risco": executar_teste_t_welch(df, "indice_risco_climatico"),
        "cohens_d": calcular_cohens_d(df, "temp_max"),
    }
    resultados["teste_t"] = resultados["teste_t_welch_temp_max"]

    if gerar_graficos:
        gerar_histogramas(df, pasta_graficos)
        gerar_boxplots(df, pasta_graficos)
        gerar_grafico_correlacao(resultados["correlacao"], pasta_graficos)
        gerar_grafico_risco(resultados["tabela_risco"], pasta_graficos)

    if salvar_csvs:
        salvar_tabelas(resultados, pasta_tabelas)
        df.to_csv(
            pasta_saida / "dataset_agroclima_orbital_com_risco.csv",
            index=False,
            encoding="utf-8-sig",
        )

    if mostrar_resumo:
        imprimir_resumo(resultados)

    return resultados


if __name__ == "__main__":
    executar_analise_completa()
