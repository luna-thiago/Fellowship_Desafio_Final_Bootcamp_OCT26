-- Consultas de Validacao — ETL da Verdejar (PostgreSQL)

-- (a) Total de vendas por mes
SELECT
    DATE_TRUNC('month', data_pedido)::date AS mes,
    COUNT(*) AS quantidade_pedidos,
    SUM(valor_total) AS total_valor_pedidos,
    SUM(valor_itens) AS total_valor_itens
FROM pedidos
GROUP BY 1
ORDER BY 1;

-- Teste de consulta para (a): a soma dos meses deve bater com a soma geral da tabela pedidos
WITH vendas_por_mes AS (
    SELECT
        DATE_TRUNC('month', data_pedido)::date AS mes,
        SUM(valor_total) AS total_mes
    FROM pedidos
    GROUP BY 1
)
SELECT
    (SELECT SUM(total_mes) FROM vendas_por_mes) AS soma_dos_meses,
    (SELECT SUM(valor_total) FROM pedidos) AS soma_geral_tabela,
    (SELECT SUM(total_mes) FROM vendas_por_mes) - (SELECT SUM(valor_total) FROM pedidos) AS diferenca;

-- (b) Quantidade de pedidos por estado
SELECT
    c.estado,
    COUNT(p.id) AS quantidade_pedidos
FROM pedidos p
JOIN clientes c ON c.id = p.cliente_id
GROUP BY c.estado
ORDER BY quantidade_pedidos DESC, c.estado ASC;

-- (c) Pedidos divergentes (contagem total e amostra dos 10 primeiros)
SELECT COUNT(*) AS total_pedidos_divergentes
FROM pedidos
WHERE divergente = TRUE;

SELECT
    id,
    cliente_id,
    data_pedido,
    status,
    valor_total,
    valor_itens,
    (valor_total - valor_itens) AS diferenca
FROM pedidos
WHERE divergente = TRUE
ORDER BY id
LIMIT 10;