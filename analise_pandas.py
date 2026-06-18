from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

COLUNAS = ["id", "data", "cliente_id", "tipo", "valor", "descricao", "categoria"]
LIMITE_SUSPEITO = 10000.00
CSV_FILE_PATH = 'transacoes.csv'

def ler_transacoes_pandas(caminho=CSV_FILE_PATH):
    try:
        return pd.read_csv(caminho, dtype=str, keep_default_na=False)
    except FileNotFoundError:
        print(f"Arquivo nao encontrado: {caminho}")
        return pd.DataFrame(columns=COLUNAS)


def limpar_transacoes_pandas(df):
    total_linhas = len(df)
    dados = df.copy()

    for coluna in COLUNAS:
        if coluna not in dados.columns:
            dados[coluna] = ""
        dados[coluna] = dados[coluna].fillna("").astype(str).str.strip()

    ids_validos = dados["id"].str.fullmatch(r"\d+")
    clientes_validos = dados["cliente_id"] != ""
    tipos_validos = dados["tipo"].str.lower().isin(["credito", "debito"])

    valores = pd.to_numeric(dados["valor"], errors="coerce")
    valores_validos = valores.notna() & (valores > 0)

    datas = pd.to_datetime(dados["data"], format="%Y-%m-%d", errors="coerce")
    datas_validas = datas.notna() & (datas.dt.strftime("%Y-%m-%d") == dados["data"])

    linhas_validas = ids_validos & clientes_validos & tipos_validos & valores_validos & datas_validas

    validas = dados.loc[linhas_validas].copy()
    validas["id"] = validas["id"].astype(int)
    validas["data"] = datas.loc[linhas_validas]
    validas["tipo"] = validas["tipo"].str.lower()
    validas["valor"] = valores.loc[linhas_validas].round(2)
    validas = validas.drop_duplicates(subset="id", keep="first").reset_index(drop=True)

    estatisticas = {
        "total_linhas": total_linhas,
        "linhas_validas": len(validas),
        "linhas_invalidas": total_linhas - len(validas),
    }
    return validas, estatisticas


def gerar_relatorio_pandas(transacoes, estatisticas):
    if transacoes.empty:
        periodo = {"inicio": None, "fim": None}
        dias_entre = 0
        resumo_mensal = {}
        suspeitas = []
    else:
        dados = transacoes.copy()
        dados["mes"] = dados["data"].dt.strftime("%Y-%m")
        dados["valor_credito"] = dados["valor"].where(dados["tipo"] == "credito", 0.0)
        dados["valor_debito"] = dados["valor"].where(dados["tipo"] == "debito", 0.0)

        agrupado = dados.groupby("mes").agg(
            quantidade=("id", "count"),
            total_credito=("valor_credito", "sum"),
            total_debito=("valor_debito", "sum"),
            media=("valor", "mean"),
            maior_valor=("valor", "max"),
            menor_valor=("valor", "min"),
        )
        agrupado["saldo"] = agrupado["total_credito"] - agrupado["total_debito"]

        resumo_mensal = {}
        for mes, linha in agrupado.sort_index().iterrows():
            resumo_mensal[mes] = {
                "quantidade": int(linha["quantidade"]),
                "total_credito": round(float(linha["total_credito"]), 2),
                "total_debito": round(float(linha["total_debito"]), 2),
                "saldo": round(float(linha["saldo"]), 2),
                "media": round(float(linha["media"]), 2),
                "maior_valor": round(float(linha["maior_valor"]), 2),
                "menor_valor": round(float(linha["menor_valor"]), 2),
            }

        data_inicial = dados["data"].min()
        data_final = dados["data"].max()
        periodo = {
            "inicio": data_inicial.strftime("%Y-%m-%d"),
            "fim": data_final.strftime("%Y-%m-%d"),
        }
        dias_entre = int((data_final - data_inicial).days)

        suspeitas = [
            {
                "id": int(linha.id),
                "cliente_id": linha.cliente_id,
                "data": linha.data.strftime("%Y-%m-%d"),
                "valor": round(float(linha.valor), 2),
            }
            for linha in dados.loc[dados["valor"] > LIMITE_SUSPEITO].itertuples()
        ]



    return {
        "gerado_em": datetime.now().date().isoformat(),
        "total_transacoes_validas": estatisticas["linhas_validas"],
        "total_transacoes_invalidas": estatisticas["linhas_invalidas"],
        "total_linhas_lidas": estatisticas["total_linhas"],
        "periodo_analisado": periodo,
        "dias_entre_transacoes": dias_entre,
        "resumo_mensal": resumo_mensal,
        "transacoes_suspeitas": suspeitas,
    }

def executar_analise_pandas(caminho_csv=CSV_FILE_PATH):
    df = ler_transacoes_pandas(caminho_csv)
    transacoes, estatisticas = limpar_transacoes_pandas(df)
    return gerar_relatorio_pandas(transacoes, estatisticas)

def exibir_resumo_limpeza(estatisticas):
    print("===== RESUMO DA LIMPEZA =====")
    print(f"Total de linhas lidas: {estatisticas['total_linhas']}")
    print(f"Linhas validas: {estatisticas['linhas_validas']}")
    print(f"Linhas invalidas: {estatisticas['linhas_invalidas']}")
    print()

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def exibir_relatorio(relatorio):
    print("===== RELATORIO MENSAL =====")
    print()

    for mes, resumo in relatorio["resumo_mensal"].items():
        print(f"Mes: {mes}")
        print(f"Transacoes: {resumo['quantidade']}")
        print(f"Total credito: {formatar_moeda(resumo['total_credito'])}")
        print(f"Total debito:  {formatar_moeda(resumo['total_debito'])}")
        print(f"Saldo:         {formatar_moeda(resumo['saldo'])}")
        print(f"Media:         {formatar_moeda(resumo['media'])}")
        print(f"Maior valor:   {formatar_moeda(resumo['maior_valor'])}")
        print(f"Menor valor:   {formatar_moeda(resumo['menor_valor'])}")
        print("-" * 32)

    print()
    print("===== TRANSACOES SUSPEITAS =====")
    if not relatorio["transacoes_suspeitas"]:
        print("Nenhuma transacao suspeita encontrada.")
        return

    for transacao in relatorio["transacoes_suspeitas"]:
        print(
            "ID: {id} | Cliente: {cliente_id} | Data: {data} | Valor: {valor}".format(
                id=transacao["id"],
                cliente_id=transacao["cliente_id"],
                data=transacao["data"],
                valor=formatar_moeda(transacao["valor"]),
            )
        )

def gerar_grafico_saldo_mensal(relatorio, caminho="grafico.png"):
    resumo = relatorio["resumo_mensal"]
    meses = list(resumo.keys())
    saldos = [resumo[mes]["saldo"] for mes in meses]

    figura, eixo = plt.subplots(figsize=(9, 5))
    barras = eixo.bar(meses, saldos, color="#2563eb", label="Saldo mensal")

    eixo.set_title("Saldo mensal - ClearBank")
    eixo.set_xlabel("Mes")
    eixo.set_ylabel("Saldo (R$)")
    eixo.legend()
    eixo.grid(axis="y", linestyle="--", alpha=0.35)

    for barra, saldo in zip(barras, saldos):
        eixo.text(
            barra.get_x() + barra.get_width() / 2,
            barra.get_height(),
            formatar_moeda(saldo),
            ha="center",
            va="bottom",
            fontsize=8,
        )

    figura.tight_layout()
    figura.savefig(caminho, dpi=150)
    plt.close(figura)
    return Path(caminho)

def main():
    df = ler_transacoes_pandas()
    transacoes, estatisticas = limpar_transacoes_pandas(df)
    exibir_resumo_limpeza(estatisticas)

    relatorio = gerar_relatorio_pandas(transacoes, estatisticas)
    exibir_relatorio(relatorio)

    gerar_grafico_saldo_mensal(relatorio)

    print()
    print("Grafico salvo em: grafico.png")
    return relatorio


if __name__ == "__main__":
    main()
