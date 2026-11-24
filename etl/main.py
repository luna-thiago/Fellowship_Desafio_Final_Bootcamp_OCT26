import sys
from etl.extracao import executar_extracao
from etl.transformacao import executar_transformacao
from etl.carga import carregar_dados_no_banco


def executar_pipeline():
    """Executa o fluxo completo do ETL da Verdejar: Extracao -> Transformacao -> Carga."""
    dados_brutos = executar_extracao()
    if dados_brutos is None:
        print("erro: pipeline interrompido na etapa de extracao.")
        sys.exit(1)

    dados_limpos = executar_transformacao(dados_brutos=dados_brutos)
    carregar_dados_no_banco(dados_limpos)


if __name__ == "__main__":
    executar_pipeline()