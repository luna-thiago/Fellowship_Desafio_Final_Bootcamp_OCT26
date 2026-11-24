from decimal import Decimal
import os
import psycopg


def carregar_variaveis_env(caminho_env=".env"):
    """Le variaveis de ambiente de um arquivo .env local, se existir, sem sobrescrever as do sistema."""
    if not os.path.exists(caminho_env):
        return

    with open(caminho_env, mode="r", encoding="utf-8") as arquivo:
        for linha in arquivo:
            texto = linha.strip()
            if not texto or texto.startswith("#") or "=" not in texto:
                continue
            chave, valor = texto.split("=", 1)
            chave = chave.strip()
            valor = valor.strip().strip('"').strip("'")
            os.environ.setdefault(chave, valor)


def obter_conexao():
    """Abre conexao com o PostgreSQL usando variaveis de ambiente."""
    carregar_variaveis_env()
    senha = os.getenv("PGPASSWORD")
    if not senha:
        raise RuntimeError(
            "Senha do PostgreSQL nao encontrada. Defina PGPASSWORD no arquivo .env ou no terminal."
        )

    return psycopg.connect(
        host=os.getenv("PGHOST", "127.0.0.1"),
        port=int(os.getenv("PGPORT", "5432")),
        dbname=os.getenv("PGDATABASE", "verdejar"),
        user=os.getenv("PGUSER", "postgres"),
        password=senha,
    )


def carregar_dados_no_banco(dados_transformados, conn=None):
    """
    Carrega produtos, clientes, pedidos e itens_pedido no PostgreSQL de forma idempotente.
    Usa TRUNCATE dentro da mesma transacao para evitar duplicacoes em reexecucoes.
    """
    fechar_ao_final = False
    if conn is None:
        conn = obter_conexao()
        fechar_ao_final = True

    try:
        with conn:
            with conn.cursor() as cur:
                # Estrategia de idempotencia: limpa as 4 tabelas na mesma transacao antes de inserir
                cur.execute(
                    "TRUNCATE TABLE itens_pedido, pedidos, clientes, produtos;"
                )

                # 1. Tabela produtos
                cur.executemany(
                    """
                    INSERT INTO produtos (produto_id, nome, categoria, preco_base)
                    VALUES (%s, %s, %s, %s);
                    """,
                    [
                        (
                            p["produto_id"],
                            p["nome"],
                            p["categoria"],
                            p["preco_base"],
                        )
                        for p in dados_transformados["produtos"]
                    ],
                )

                # 2. Tabela clientes
                cur.executemany(
                    """
                    INSERT INTO clientes (id, nome, email, cidade, estado, cadastro_em)
                    VALUES (%s, %s, %s, %s, %s, %s);
                    """,
                    [
                        (
                            c["id"],
                            c["nome"],
                            c["email"],
                            c["cidade"],
                            c["estado"],
                            c["cadastro_em"],
                        )
                        for c in dados_transformados["clientes"]
                    ],
                )

                # 3. Tabela pedidos
                cur.executemany(
                    """
                    INSERT INTO pedidos (
                        id, cliente_id, data_pedido, status, valor_total, valor_itens, divergente
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                    """,
                    [
                        (
                            ped["id"],
                            ped["cliente_id"],
                            ped["data_pedido"],
                            ped["status"],
                            ped["valor_total"],
                            ped["valor_itens"],
                            ped["divergente"],
                        )
                        for ped in dados_transformados["pedidos"]
                    ],
                )

                # 4. Tabela itens_pedido
                cur.executemany(
                    """
                    INSERT INTO itens_pedido (
                        pedido_id, linha, produto_id, quantidade, preco_unitario
                    )
                    VALUES (%s, %s, %s, %s, %s);
                    """,
                    [
                        (
                            item["pedido_id"],
                            item["linha"],
                            item["produto_id"],
                            item["quantidade"],
                            item["preco_unitario"],
                        )
                        for item in dados_transformados["itens_pedido"]
                    ],
                )

                # Consulta contagens e soma diretamente do banco para reconciliacao
                cur.execute("SELECT COUNT(*) FROM clientes;")
                total_clientes = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*) FROM produtos;")
                total_produtos = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*) FROM pedidos;")
                total_pedidos = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*) FROM itens_pedido;")
                total_itens = cur.fetchone()[0]

                cur.execute("SELECT COALESCE(SUM(valor_itens), 0) FROM pedidos;")
                soma_destino = Decimal(str(cur.fetchone()[0])).quantize(Decimal("0.01"))

        soma_origem = sum(
            (ped["valor_itens"] for ped in dados_transformados["pedidos"]),
            Decimal("0.00"),
        ).quantize(Decimal("0.01"))
        diferenca = abs(soma_origem - soma_destino).quantize(Decimal("0.01"))

        print(
            f"carga: clientes={total_clientes} produtos={total_produtos} "
            f"pedidos={total_pedidos} itens={total_itens}"
        )
        print(
            f"reconciliacao: soma_valor_itens_origem={soma_origem} "
            f"soma_valor_itens_destino={soma_destino} diferenca={diferenca}"
        )

        return {
            "clientes": total_clientes,
            "produtos": total_produtos,
            "pedidos": total_pedidos,
            "itens": total_itens,
            "soma_origem": soma_origem,
            "soma_destino": soma_destino,
            "diferenca": diferenca,
        }
    finally:
        if fechar_ao_final:
            conn.close()