import csv
import json
import os
from urllib import error, request

URL_BASE_PADRAO = "http://127.0.0.1:8000"


def extrair_rota_paginada(url_base, rota, page_size=50, pagina_inicial=1):
    """
    Busca todas as paginas de uma rota da API (ex.: 'clientes' ou 'pedidos').
    Devolve dois valores: (lista_de_registros, quantidade_de_paginas_lidas).
    Se houver erro de conexao ou pagina inexistente, imprime mensagem clara e devolve (None, 0).
    """
    todos_os_registros = []
    pagina_atual = pagina_inicial
    total_paginas = None

    while total_paginas is None or pagina_atual <= total_paginas:
        url = f"{url_base}/{rota}?page={pagina_atual}&page_size={page_size}"

        try:
            with request.urlopen(url, timeout=10) as resposta:
                # Confere se o codigo de status HTTP indica sucesso (200)
                if resposta.status != 200:
                    print(
                        f"erro: rota /{rota} pagina {pagina_atual} retornou status HTTP {resposta.status}"
                    )
                    return None, 0

                texto_resposta = resposta.read().decode("utf-8")
                dados_pagina = json.loads(texto_resposta)

        except error.HTTPError as err:
            # A API devolve 404 quando a pagina ou a rota nao existe
            if err.code == 404:
                print(
                    f"erro: pagina {pagina_atual} ou rota /{rota} inexistente (HTTP 404)."
                )
            else:
                print(
                    f"erro: falha HTTP {err.code} ao acessar /{rota} na pagina {pagina_atual}."
                )
            return None, 0

        except error.URLError as err:
            # Acontece quando a API esta desligada ou o endereco nao responde
            print(
                f"erro: falha de conexao com {url_base} ({err.reason}). Verifique se a API esta rodando."
            )
            return None, 0

        total_paginas = dados_pagina["total_pages"]
        todos_os_registros.extend(dados_pagina["items"])
        pagina_atual += 1

    paginas_lidas = pagina_atual - pagina_inicial
    return todos_os_registros, paginas_lidas


def ler_produtos_csv(caminho_csv):
    """Le o arquivo produtos.csv com o modulo csv e devolve uma lista de dicionarios."""
    try:
        with open(caminho_csv, mode="r", encoding="utf-8", newline="") as arquivo:
            leitor = csv.DictReader(arquivo)
            return list(leitor)
    except FileNotFoundError:
        print(f"erro: arquivo de produtos nao encontrado em {caminho_csv}.")
        return None


def salvar_bruto_json(dados, caminho_arquivo):
    """Cria a pasta de destino se nao existir e grava os dados originais em JSON."""
    pasta = os.path.dirname(caminho_arquivo)
    if pasta:
        os.makedirs(pasta, exist_ok=True)

    with open(caminho_arquivo, mode="w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)


def executar_extracao(
    url_base=URL_BASE_PADRAO,
    caminho_csv="insumos/dados/produtos.csv",
    pasta_brutos="brutos",
):
    """Orquestra a extracao da API e do CSV, salva os brutos e imprime os contadores."""
    clientes, paginas_clientes = extrair_rota_paginada(url_base, "clientes")
    if clientes is None:
        return None

    pedidos, paginas_pedidos = extrair_rota_paginada(url_base, "pedidos")
    if pedidos is None:
        return None

    produtos = ler_produtos_csv(caminho_csv)
    if produtos is None:
        return None

    salvar_bruto_json(clientes, os.path.join(pasta_brutos, "clientes.json"))
    salvar_bruto_json(pedidos, os.path.join(pasta_brutos, "pedidos.json"))
    salvar_bruto_json(produtos, os.path.join(pasta_brutos, "produtos.json"))

    print(f"extracao: clientes paginas={paginas_clientes} registros={len(clientes)}")
    print(f"extracao: pedidos paginas={paginas_pedidos} registros_brutos={len(pedidos)}")
    print(f"extracao: produtos registros={len(produtos)}")

    return {
        "clientes": clientes,
        "pedidos": pedidos,
        "produtos": produtos,
    }


if __name__ == "__main__":
    executar_extracao()