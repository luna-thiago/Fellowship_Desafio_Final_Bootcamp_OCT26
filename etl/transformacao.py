from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import json
import os

DUAS_CASAS = Decimal("0.01")


# --- Funcoes pequenas e puras para as armadilhas A1 a A6 ---


def tratar_email(email):
    """Armadilha A1: mantem None se o e-mail estiver ausente ou vazio."""
    if email is None:
        return None
    texto = str(email).strip()
    return texto if texto else None


def padronizar_estado(estado):
    """Armadilha A2: garante a sigla do estado em 2 letras maiusculas."""
    return str(estado).strip().upper()


def converter_data(data_texto):
    """Armadilha A3: converte 'AAAA-MM-DD' ou 'DD/MM/AAAA' para objeto date do Python."""
    texto = str(data_texto).strip()
    if "/" in texto:
        return datetime.strptime(texto, "%d/%m/%Y").date()
    return datetime.strptime(texto, "%Y-%m-%d").date()


def converter_valor(valor):
    """Armadilha A4: converte numero ou texto com virgula (ex.: '125,84' ou '1.250,84') para Decimal exato."""
    texto = str(valor).strip()
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    return Decimal(texto).quantize(DUAS_CASAS, rounding=ROUND_HALF_UP)


def remover_pedidos_repetidos(lista_pedidos):
    """Armadilha A5: remove pedidos com mesmo id, mantendo a primeira ocorrencia."""
    ids_vistos = set()
    pedidos_unicos = []
    repetidos_descartados = 0

    for pedido in lista_pedidos:
        pedido_id = int(pedido["id"])
        if pedido_id in ids_vistos:
            repetidos_descartados += 1
        else:
            ids_vistos.add(pedido_id)
            pedidos_unicos.append(pedido)

    return pedidos_unicos, repetidos_descartados


def calcular_e_verificar_itens(itens, valor_total_convertido):
    """Armadilha A6: soma (quantidade * preco_unitario) com Decimal e verifica divergencia > 0.01."""
    soma_itens = Decimal("0.00")
    for item in itens:
        quantidade = Decimal(int(item["quantidade"]))
        preco_unitario = converter_valor(item["preco_unitario"])
        soma_itens += quantidade * preco_unitario

    valor_itens = soma_itens.quantize(DUAS_CASAS, rounding=ROUND_HALF_UP)
    divergente = abs(valor_total_convertido - valor_itens) > DUAS_CASAS
    return valor_itens, divergente


# --- Transformacao completa de cada conjunto de dados ---


def transformar_clientes(clientes_brutos):
    """Limpa a lista de clientes (A1 e A2) e retorna (clientes_limpos, contadores)."""
    clientes_limpos = []
    emails_nulos = 0
    estados_padronizados = 0

    for cliente in clientes_brutos:
        email_limpo = tratar_email(cliente.get("email"))
        if email_limpo is None:
            emails_nulos += 1

        estado_original = str(cliente["estado"]).strip()
        estado_limpo = padronizar_estado(estado_original)
        if estado_original != estado_limpo:
            estados_padronizados += 1

        clientes_limpos.append(
            {
                "id": int(cliente["id"]),
                "nome": str(cliente["nome"]).strip(),
                "email": email_limpo,
                "cidade": str(cliente["cidade"]).strip(),
                "estado": estado_limpo,
                "cadastro_em": converter_data(cliente["cadastro_em"]),
            }
        )

    contadores = {
        "emails_nulos": emails_nulos,
        "estados_padronizados": estados_padronizados,
    }
    return clientes_limpos, contadores


def transformar_produtos(produtos_brutos):
    """Converte os tipos do catalogo de produtos vindo do CSV."""
    produtos_limpos = []
    for produto in produtos_brutos:
        produtos_limpos.append(
            {
                "produto_id": int(produto["produto_id"]),
                "nome": str(produto["nome"]).strip(),
                "categoria": str(produto["categoria"]).strip(),
                "preco_base": converter_valor(produto["preco_base"]),
            }
        )
    return produtos_limpos


def transformar_pedidos(pedidos_brutos):
    """Limpa pedidos (A3, A4, A5, A6), separa itens_pedido e retorna (pedidos, itens, contadores)."""
    pedidos_unicos, repetidos_descartados = remover_pedidos_repetidos(pedidos_brutos)

    pedidos_limpos = []
    itens_limpos = []
    datas_convertidas = 0
    valores_convertidos = 0
    divergentes = 0

    for pedido in pedidos_unicos:
        pedido_id = int(pedido["id"])
        data_original = str(pedido["data_pedido"]).strip()
        if "/" in data_original:
            datas_convertidas += 1
        data_limpa = converter_data(data_original)

        valor_original = pedido["valor_total"]
        if isinstance(valor_original, str):
            valores_convertidos += 1
        valor_total_limpo = converter_valor(valor_original)

        itens_brutos = pedido.get("itens", [])
        valor_itens, divergente = calcular_e_verificar_itens(
            itens_brutos, valor_total_limpo
        )
        if divergente:
            divergentes += 1

        pedidos_limpos.append(
            {
                "id": pedido_id,
                "cliente_id": int(pedido["cliente_id"]),
                "data_pedido": data_limpa,
                "status": str(pedido["status"]).strip(),
                "valor_total": valor_total_limpo,
                "valor_itens": valor_itens,
                "divergente": divergente,
            }
        )

        # Numera cada item do pedido a partir de 1 para a coluna 'linha'
        for numero_linha, item in enumerate(itens_brutos, start=1):
            itens_limpos.append(
                {
                    "pedido_id": pedido_id,
                    "linha": numero_linha,
                    "produto_id": int(item["produto_id"]),
                    "quantidade": int(item["quantidade"]),
                    "preco_unitario": converter_valor(item["preco_unitario"]),
                }
            )

    contadores = {
        "pedidos_unicos": len(pedidos_limpos),
        "repetidos_descartados": repetidos_descartados,
        "datas_convertidas": datas_convertidas,
        "valores_convertidos": valores_convertidos,
        "divergentes": divergentes,
    }
    return pedidos_limpos, itens_limpos, contadores


def ler_bruto_json(caminho_arquivo):
    """Le um arquivo JSON salvo na pasta brutos/."""
    with open(caminho_arquivo, mode="r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def executar_transformacao(dados_brutos=None, pasta_brutos="brutos"):
    """Executa todas as transformacoes (a partir da memoria ou dos arquivos em brutos/) e imprime os contadores."""
    if dados_brutos is None:
        dados_brutos = {
            "clientes": ler_bruto_json(os.path.join(pasta_brutos, "clientes.json")),
            "pedidos": ler_bruto_json(os.path.join(pasta_brutos, "pedidos.json")),
            "produtos": ler_bruto_json(os.path.join(pasta_brutos, "produtos.json")),
        }

    clientes_limpos, cont_clientes = transformar_clientes(dados_brutos["clientes"])
    produtos_limpos = transformar_produtos(dados_brutos["produtos"])
    pedidos_limpos, itens_limpos, cont_pedidos = transformar_pedidos(
        dados_brutos["pedidos"]
    )

    print(
        f"transformacao: pedidos_unicos={cont_pedidos['pedidos_unicos']} "
        f"repetidos_descartados={cont_pedidos['repetidos_descartados']}"
    )
    print(
        f"transformacao: emails_nulos={cont_clientes['emails_nulos']} "
        f"estados_padronizados={cont_clientes['estados_padronizados']} "
        f"datas_convertidas={cont_pedidos['datas_convertidas']} "
        f"valores_convertidos={cont_pedidos['valores_convertidos']}"
    )
    print(
        f"divergentes: {cont_pedidos['divergentes']} pedidos com valor_total diferente da soma dos itens"
    )

    return {
        "clientes": clientes_limpos,
        "produtos": produtos_limpos,
        "pedidos": pedidos_limpos,
        "itens_pedido": itens_limpos,
    }


if __name__ == "__main__":
    executar_transformacao()