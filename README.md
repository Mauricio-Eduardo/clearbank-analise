# ClearBank - Analise de Transacoes

Projeto de pos-graduacao para validar, limpar e analisar transacoes financeiras mensais exportadas em CSV.

## Como executar

1. Abra o arquivo `analise-financeira.ipynb` no Google Colab.
2. Faça upload do arquivo `transacoes.csv`. na sessão do Colab:
    - No menu lateral esquerdo, clique em `Arquivos`;
    - Vai abrir uma aba ao lado, nesta aba, nas opções superiores, clique em `Fazer upload para armazenamento da sessão`;
    - Selecione o arquivo `transacoes.csv` e faça o upload;
2. Execute as celulas em ordem, do inicio ao fim.

## O que o notebook gera

Ao executar a analise, o notebook:

- le o arquivo `transacoes.csv` com `csv.DictReader`;
- valida campos obrigatorios, datas, tipos e valores;
- exibe o resumo da limpeza no terminal;
- calcula metricas mensais de credito, debito, saldo, media, maior valor e menor valor;
- lista transacoes suspeitas acima de R$ 10.000,00;
- salva o resultado em `relatorio.json`.
- executa uma versao alternativa com `pandas` em `analise_pandas.py`;
- gera o grafico de saldo mensal com `matplotlib` em `grafico.png`.

## Arquivos principais

- `analise-financeira.ipynb`: notebook principal com as celulas executadas e saidas salvas.
- `transacoes.csv`: base de exemplo com registros validos e invalidos.
- `analise_clearbank.py`: modulo com as funcoes usadas no notebook.
- `analise_pandas.py`: versao opcional com pandas e matplotlib.
- `relatorio.json`: arquivo gerado pela execucao da analise.
- `grafico.png`: grafico de barras com o saldo mensal.
