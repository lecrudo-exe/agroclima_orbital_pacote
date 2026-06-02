import requests
import pandas as pd
from pathlib import Path

Path("dados").mkdir(exist_ok=True)

cidades = {
    "Petrolina/PE": {"latitude": -9.3986, "longitude": -40.5008},
    "Ribeirao Preto/SP": {"latitude": -21.1775, "longitude": -47.8103},
}

parametros = [
    "T2M",
    "T2M_MAX",
    "T2M_MIN",
    "PRECTOTCORR",
    "RH2M",
    "WS2M",
    "ALLSKY_SFC_SW_DWN",
]

inicio = "20150101"
fim = "20251231"


def baixar_nasa_power(nome_cidade, latitude, longitude):
    url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "parameters": ",".join(parametros),
        "community": "AG",
        "longitude": longitude,
        "latitude": latitude,
        "start": inicio,
        "end": fim,
        "format": "JSON",
    }
    response = requests.get(url, params=params, timeout=120)
    response.raise_for_status()
    dados = response.json()["properties"]["parameter"]
    df = pd.DataFrame(dados)
    df.index = pd.to_datetime(df.index, format="%Y%m%d")
    df = df.reset_index().rename(columns={"index": "data"})
    df["cidade"] = nome_cidade
    df["latitude"] = latitude
    df["longitude"] = longitude
    return df


def main():
    bases = []
    for nome, coords in cidades.items():
        print(f"Baixando dados de {nome}...")
        bases.append(baixar_nasa_power(nome, coords["latitude"], coords["longitude"]))

    dataset = pd.concat(bases, ignore_index=True)
    colunas = [
        "data", "cidade", "latitude", "longitude", "T2M", "T2M_MAX",
        "T2M_MIN", "PRECTOTCORR", "RH2M", "WS2M", "ALLSKY_SFC_SW_DWN",
    ]
    dataset = dataset[colunas].sort_values(["cidade", "data"]).reset_index(drop=True)
    caminho_saida = "dados/dataset_agroclima_orbital.csv"
    dataset.to_csv(caminho_saida, index=False, encoding="utf-8-sig")
    print("Dataset criado com sucesso!")
    print(f"Arquivo salvo em: {caminho_saida}")
    print(f"Shape: {dataset.shape}")
    print(dataset.head())
    dataset.info()


if __name__ == "__main__":
    main()
