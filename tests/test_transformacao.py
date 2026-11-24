from datetime import date
from decimal import Decimal
from etl.transformacao import (
    calcular_e_verificar_itens,
    converter_data,
    converter_valor,
    padronizar_estado,
    remover_pedidos_repetidos,
    tratar_email,
)


# Armadilha A1: e-mail ausente ou vazio vira None sem descartar o cliente
def test_a1_email_nulo_ou_vazio_preserva_none():
    assert tratar_email(None) is None
    assert tratar_email("   ") is None
    assert tratar_email("ana.silva1@exemplo.com") == "ana.silva1@exemplo.com"


# Armadilha A2: sigla do estado em minusculas vira maiusculas
def test_a2_estado_minusculo_vira_maiusculo():
    assert padronizar_estado("rs") == "RS"
    assert padronizar_estado(" sp ") == "SP"
    assert padronizar_estado("PR") == "PR"


# Armadilha A3 (obrigatoria): datas em DD/MM/AAAA e AAAA-MM-DD viram date
def test_a3_datas_em_dois_formatos_convertem_para_date():
    assert converter_data("25/11/2026") == date(2026, 11, 25)
    assert converter_data("2026-11-25") == date(2026, 11, 25)


# Armadilha A4 (obrigatoria): texto com virgula e numero viram Decimal com 2 casas
def test_a4_valor_com_virgula_vira_decimal_exato():
    assert converter_valor("125,84") == Decimal("125.84")
    assert converter_valor(94.34) == Decimal("94.34")
    assert converter_valor("1.250,84") == Decimal("1250.84")


# Armadilha A5 (obrigatoria): pedidos duplicados sao descartados mantendo o primeiro
def test_a5_pedidos_repetidos_mantem_apenas_primeira_ocorrencia():
    pedidos_entrada = [
        {"id": 10, "status": "entregue"},
        {"id": 20, "status": "cancelado"},
        {"id": 10, "status": "entregue"},
    ]
    unicos, descartados = remover_pedidos_repetidos(pedidos_entrada)

    assert len(unicos) == 2
    assert descartados == 1
    assert [p["id"] for p in unicos] == [10, 20]


# Armadilha A6: identifica quando valor_total diverge da soma dos itens em mais de 1 centavo
def test_a6_detecta_divergencia_entre_valor_total_e_soma_itens():
    itens = [
        {"produto_id": 1, "quantidade": 2, "preco_unitario": "10.00"},
        {"produto_id": 2, "quantidade": 1, "preco_unitario": "5.50"},
    ]
    # Soma real = 25.50; informado = 30.50 -> divergente = True
    valor_itens, divergente = calcular_e_verificar_itens(itens, Decimal("30.50"))
    assert valor_itens == Decimal("25.50")
    assert divergente is True

    # Quando bate exatamente -> divergente = False
    valor_itens_ok, divergente_ok = calcular_e_verificar_itens(itens, Decimal("25.50"))
    assert valor_itens_ok == Decimal("25.50")
    assert divergente_ok is False