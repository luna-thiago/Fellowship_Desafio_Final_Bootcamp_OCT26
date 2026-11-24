from decimal import Decimal
from etl.carga import obter_conexao
from etl.transformacao import ler_bruto_json, transformar_pedidos


def test_reconciliacao_origem_e_destino_postgresql():
    """
    Compara a contagem de pedidos unicos e a soma de valor_itens da origem
    com os dados carregados na tabela pedidos do PostgreSQL (tolerancia de R$ 0,01).
    """
    pedidos_brutos = ler_bruto_json("brutos/pedidos.json")
    pedidos_unicos, _, _ = transformar_pedidos(pedidos_brutos)

    contagem_origem = len(pedidos_unicos)
    soma_origem = sum(
        (p["valor_itens"] for p in pedidos_unicos), Decimal("0.00")
    ).quantize(Decimal("0.01"))

    with obter_conexao() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM pedidos;")
            contagem_destino = cur.fetchone()[0]

            cur.execute("SELECT COALESCE(SUM(valor_itens), 0) FROM pedidos;")
            soma_destino = Decimal(str(cur.fetchone()[0])).quantize(Decimal("0.01"))

    assert contagem_destino == contagem_origem
    assert abs(soma_origem - soma_destino) <= Decimal("0.01")